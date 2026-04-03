import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import random
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from datetime import timedelta

# Configurazione pagina
st.set_page_config(
    page_title="Forex Sentinel Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizzato
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #13183a 100%);
    }
    .main-header {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        margin-bottom: 2rem;
    }
    .signal-card {
        background: rgba(26, 31, 62, 0.9);
        border-radius: 15px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid;
        backdrop-filter: blur(10px);
    }
    .signal-buy {
        border-left-color: #10b981;
    }
    .signal-sell {
        border-left-color: #ef4444;
    }
    .metric-card {
        background: rgba(26, 31, 62, 0.8);
        border-radius: 15px;
        padding: 1rem;
        text-align: center;
        backdrop-filter: blur(10px);
    }
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-high {
        background: rgba(16, 185, 129, 0.2);
        color: #10b981;
    }
    .badge-medium {
        background: rgba(245, 158, 11, 0.2);
        color: #f59e0b;
    }
    .badge-low {
        background: rgba(239, 68, 68, 0.2);
        color: #ef4444;
    }
</style>
""", unsafe_allow_html=True)

# Titolo
st.markdown("""
<div class="main-header">
    <h1 style="color: white; margin: 0;">📊 Forex Sentinel Pro</h1>
    <p style="color: rgba(255,255,255,0.9); margin-top: 0.5rem;">Segnali di Trading basati su COT + Sentiment Retail</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## ⚙️ Configurazione")
    
    # Coppie forex da monitorare
    forex_pairs = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'NZDUSD', 'USDCHF']
    
    st.markdown("### 📈 Coppie monitorate")
    for pair in forex_pairs:
        st.markdown(f"- {pair}")
    
    st.markdown("---")
    st.markdown("### 🔄 Aggiornamento")
    
    if st.button("🔄 Aggiorna Dati", type="primary", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📊 Fonti Dati")
    st.markdown("""
    - **COT**: CFTC (istituzionale)
    - **Sentiment**: Myfxbook (retail)
    - **Prezzi**: Yahoo Finance
    """)
    
    st.markdown("---")
    st.markdown("### 💡 Strategia")
    st.markdown("""
    Segnali generati quando:
    - COT istituzionale ALLINEATO
    - Sentiment retail ESTREMO (contrarian)
    - Livelli tecnici CONFERMANO
    """)

# Funzioni di caching
@st.cache_data(ttl=3600)  # cache 1 ora
def get_cot_data():
    """Simula dati COT (in produzione: scraping CFTC)"""
    return {
        'EURUSD': {'bias': 'bullish', 'strength': 'strong', 'long': 62, 'short': 28},
        'GBPUSD': {'bias': 'neutral', 'strength': 'weak', 'long': 45, 'short': 44},
        'USDJPY': {'bias': 'bearish', 'strength': 'moderate', 'long': 38, 'short': 55},
        'AUDUSD': {'bias': 'bullish', 'strength': 'strong', 'long': 58, 'short': 29},
        'USDCAD': {'bias': 'neutral', 'strength': 'weak', 'long': 44, 'short': 47},
        'NZDUSD': {'bias': 'bullish', 'strength': 'moderate', 'long': 52, 'short': 38},
        'USDCHF': {'bias': 'bearish', 'strength': 'moderate', 'long': 35, 'short': 54}
    }

@st.cache_data(ttl=1800)  # cache 30 minuti
def get_retail_sentiment():
    """Simula dati Myfxbook (in produzione: scraping)"""
    return {
        'EURUSD': {'long': 42, 'short': 58, 'signal': 'buy', 'extremity': 'moderate'},
        'GBPUSD': {'long': 35, 'short': 65, 'signal': 'buy', 'extremity': 'extreme'},
        'USDJPY': {'long': 68, 'short': 32, 'signal': 'sell', 'extremity': 'extreme'},
        'AUDUSD': {'long': 55, 'short': 45, 'signal': 'neutral', 'extremity': 'moderate'},
        'USDCAD': {'long': 38, 'short': 62, 'signal': 'buy', 'extremity': 'extreme'},
        'NZDUSD': {'long': 48, 'short': 52, 'signal': 'neutral', 'extremity': 'low'},
        'USDCHF': {'long': 72, 'short': 28, 'signal': 'sell', 'extremity': 'extreme'}
    }

@st.cache_data(ttl=300)  # cache 5 minuti
def get_current_prices(pairs):
    """Recupera prezzi da Yahoo Finance"""
    prices = {}
    for pair in pairs:
        try:
            symbol = f"{pair}=X"
            ticker = yf.Ticker(symbol)
            data = ticker.history(period='1d')
            if not data.empty:
                prices[pair] = round(data['Close'].iloc[-1], 5)
            else:
                prices[pair] = None
        except:
            prices[pair] = None
        time.sleep(0.5)  # evita rate limiting
    return prices

def calculate_pivot_levels(pair, current_price):
    """Calcola pivot points"""
    try:
        symbol = f"{pair}=X"
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period='5d')
        
        if len(hist) >= 2:
            yesterday = hist.iloc[-2]
            high = yesterday['High']
            low = yesterday['Low']
            close = yesterday['Close']
            
            pivot = (high + low + close) / 3
            r1 = 2 * pivot - low
            s1 = 2 * pivot - high
            
            return {
                'pivot': round(pivot, 5),
                'r1': round(r1, 5),
                's1': round(s1, 5),
                'current': current_price
            }
    except:
        pass
    
    # Fallback
    if current_price:
        return {
            'pivot': current_price,
            'r1': round(current_price * 1.005, 5),
            's1': round(current_price * 0.995, 5),
            'current': current_price
        }
    return None

def generate_signals(cot_data, retail_data, prices, levels):
    """Genera segnali combinati"""
    signals = []
    
    for pair in cot_data.keys():
        if pair not in retail_data or pair not in levels:
            continue
        
        cot = cot_data[pair]
        retail = retail_data[pair]
        level = levels[pair]
        price = prices.get(pair)
        
        score = 0
        reasons = []
        
        # COT score (max 40)
        if cot['bias'] == 'bullish':
            if cot['strength'] == 'strong':
                score += 40
                reasons.append("COT fortemente rialzista")
            else:
                score += 25
                reasons.append("COT moderatamente rialzista")
        elif cot['bias'] == 'bearish':
            if cot['strength'] == 'strong':
                score += 40
                reasons.append("COT fortemente ribassista")
            else:
                score += 25
                reasons.append("COT moderatamente ribassista")
        
        # Retail contrarian score (max 40)
        if retail['signal'] == 'buy':
            if retail['extremity'] == 'extreme':
                score += 40
                reasons.append("Retail estremamente short 📉")
            else:
                score += 25
                reasons.append("Retail short")
        elif retail['signal'] == 'sell':
            if retail['extremity'] == 'extreme':
                score += 40
                reasons.append("Retail estremamente long 📈")
            else:
                score += 25
                reasons.append("Retail long")
        
        # Technical score (max 20)
        if price and level:
            if price < level['s1']:
                score += 20
                reasons.append("Sotto supporto chiave")
            elif price > level['r1']:
                score += 20
                reasons.append("Sopra resistenza chiave")
        
        # Determina azione
        action = None
        if cot['bias'] == 'bullish' and retail['signal'] == 'buy':
            action = 'BUY'
        elif cot['bias'] == 'bearish' and retail['signal'] == 'sell':
            action = 'SELL'
        elif score > 60:
            action = 'BUY' if cot['bias'] == 'bullish' else 'SELL'
        
        if action and score >= 50:
            # Calcola entry/TP/SL
            if action == 'BUY':
                entry = level['s1'] if level['s1'] else price
                tp = level['pivot'] if level['pivot'] else price * 1.005
                sl = entry * 0.995
                rr = round((tp - entry) / (entry - sl), 2) if sl else 0
            else:
                entry = level['r1'] if level['r1'] else price
                tp = level['pivot'] if level['pivot'] else price * 0.995
                sl = entry * 1.005
                rr = round((entry - tp) / (sl - entry), 2) if sl else 0
            
            signals.append({
                'pair': pair,
                'action': action,
                'score': score,
                'confidence': 'HIGH' if score >= 75 else 'MEDIUM' if score >= 60 else 'LOW',
                'entry': entry,
                'tp': tp,
                'sl': sl,
                'rr': rr,
                'reasons': ' | '.join(reasons[:2]),
                'current_price': price
            })
    
    # Ordina per score
    signals.sort(key=lambda x: x['score'], reverse=True)
    return signals

# Main app
try:
    # Mostra spinner durante il caricamento
    with st.spinner('Caricamento dati in corso...'):
        # Recupera dati
        cot_data = get_cot_data()
        retail_data = get_retail_sentiment()
        prices = get_current_prices(forex_pairs)
        
        # Calcola livelli
        levels = {}
        for pair in forex_pairs:
            level = calculate_pivot_levels(pair, prices.get(pair))
            if level:
                levels[pair] = level
        
        # Genera segnali
        signals = generate_signals(cot_data, retail_data, prices, levels)
    
    # Metriche in cima
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3 style="margin: 0; color: #667eea;">{}</h3>
            <p style="margin: 0; color: #a0a5c0;">Segnali Attivi</p>
        </div>
        """.format(len(signals)), unsafe_allow_html=True)
    
    with col2:
        buys = len([s for s in signals if s['action'] == 'BUY'])
        st.markdown("""
        <div class="metric-card">
            <h3 style="margin: 0; color: #10b981;">{}</h3>
            <p style="margin: 0; color: #a0a5c0;">Acquisti</p>
        </div>
        """.format(buys), unsafe_allow_html=True)
    
    with col3:
        sells = len([s for s in signals if s['action'] == 'SELL'])
        st.markdown("""
        <div class="metric-card">
            <h3 style="margin: 0; color: #ef4444;">{}</h3>
            <p style="margin: 0; color: #a0a5c0;">Vendite</p>
        </div>
        """.format(sells), unsafe_allow_html=True)
    
    with col4:
        avg_score = round(sum(s['score'] for s in signals) / len(signals), 1) if signals else 0
        st.markdown("""
        <div class="metric-card">
            <h3 style="margin: 0; color: #f59e0b;">{}</h3>
            <p style="margin: 0; color: #a0a5c0;">Score Medio</p>
        </div>
        """.format(avg_score), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Tabella segnali
    st.markdown("## 🎯 Segnali di Trading")
    
    if signals:
        # Converti in DataFrame per visualizzazione
        df_signals = pd.DataFrame(signals)
        df_signals['entry'] = df_signals['entry'].apply(lambda x: f"{x:.5f}")
        df_signals['tp'] = df_signals['tp'].apply(lambda x: f"{x:.5f}")
        df_signals['sl'] = df_signals['sl'].apply(lambda x: f"{x:.5f}")
        df_signals['current_price'] = df_signals['current_price'].apply(lambda x: f"{x:.5f}" if x else "N/A")
        
        # Colori per azione
        def color_action(val):
            if val == 'BUY':
                return 'background-color: rgba(16, 185, 129, 0.2)'
            elif val == 'SELL':
                return 'background-color: rgba(239, 68, 68, 0.2)'
            return ''
        
        styled_df = df_signals[['pair', 'action', 'confidence', 'entry', 'tp', 'sl', 'rr', 'reasons']].style.applymap(
            color_action, subset=['action']
        )
        
        st.dataframe(styled_df, use_container_width=True, height=400)
        
        # Dettaglio segnali con carte
        st.markdown("### 📋 Dettaglio Segnali")
        
        for signal in signals[:5]:  # Mostra primi 5
            card_class = "signal-card signal-buy" if signal['action'] == 'BUY' else "signal-card signal-sell"
            badge_class = f"badge badge-{signal['confidence'].lower()}"
            
            st.markdown(f"""
            <div class="{card_class}">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h3 style="margin: 0;">{signal['pair']}</h3>
                        <span class="{badge_class}">{signal['confidence']} CONFIDENZA</span>
                    </div>
                    <div style="text-align: right;">
                        <h2 style="margin: 0; color: {'#10b981' if signal['action'] == 'BUY' else '#ef4444'}">
                            {signal['action']}
                        </h2>
                        <span style="font-size: 12px;">Score: {signal['score']}</span>
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-top: 1rem;">
                    <div>
                        <small style="color: #a0a5c0;">Entry</small>
                        <br/>
                        <strong>{signal['entry']:.5f}</strong>
                    </div>
                    <div>
                        <small style="color: #a0a5c0;">Take Profit</small>
                        <br/>
                        <strong style="color: #10b981;">{signal['tp']:.5f}</strong>
                    </div>
                    <div>
                        <small style="color: #a0a5c0;">Stop Loss</small>
                        <br/>
                        <strong style="color: #ef4444;">{signal['sl']:.5f}</strong>
                    </div>
                    <div>
                        <small style="color: #a0a5c0;">R:R Ratio</small>
                        <br/>
                        <strong>1:{signal['rr']}</strong>
                    </div>
                </div>
                <div style="margin-top: 0.75rem; font-size: 12px; color: #a0a5c0;">
                    <i class="fas fa-info-circle"></i> {signal['reasons']}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Nessun segnale al momento. Riprova più tardi.")
    
    st.markdown("---")
    
    # Due colonne per COT e Retail
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("## 🏦 COT Analysis (Istituzionale)")
        
        cot_df = pd.DataFrame([
            {
                'Coppia': pair,
                'Long %': data['long'],
                'Short %': data['short'],
                'Bias': '🟢 BULL' if data['bias'] == 'bullish' else '🔴 BEAR' if data['bias'] == 'bearish' else '⚪ NEUTRO'
            }
            for pair, data in cot_data.items()
        ])
        st.dataframe(cot_df, use_container_width=True, hide_index=True)
        
        # Grafico COT
        fig_cot = go.Figure()
        for pair in list(cot_data.keys())[:5]:
            fig_cot.add_trace(go.Bar(
                name=pair,
                x=['Long', 'Short'],
                y=[cot_data[pair]['long'], cot_data[pair]['short']],
                text=[f"{cot_data[pair]['long']}%", f"{cot_data[pair]['short']}%"],
                textposition='auto'
            ))
        fig_cot.update_layout(
            title="Posizionamento Non-Commercial",
            barmode='group',
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
        st.plotly_chart(fig_cot, use_container_width=True)
    
    with col2:
        st.markdown("## 👥 Retail Sentiment (Myfxbook)")
        
        retail_df = pd.DataFrame([
            {
                'Coppia': pair,
                'Long %': data['long'],
                'Short %': data['short'],
                'Segnale': '🟢 BUY' if data['signal'] == 'buy' else '🔴 SELL' if data['signal'] == 'sell' else '⚪ NEUTRO'
            }
            for pair, data in retail_data.items()
        ])
        st.dataframe(retail_df, use_container_width=True, hide_index=True)
        
        # Grafico retail
        fig_retail = go.Figure()
        for pair in list(retail_data.keys())[:5]:
            fig_retail.add_trace(go.Bar(
                name=pair,
                x=['Long', 'Short'],
                y=[retail_data[pair]['long'], retail_data[pair]['short']],
                text=[f"{retail_data[pair]['long']}%", f"{retail_data[pair]['short']}%"],
                textposition='auto'
            ))
        fig_retail.update_layout(
            title="Sentiment Trader Retail",
            barmode='group',
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
        st.plotly_chart(fig_retail, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #a0a5c0; font-size: 12px; padding: 1rem;">
        <p>⚠️ Disclaimer: I segnali sono generati automaticamente. Non costituiscono consulenza finanziaria. 
        Il trading forex comporta rischi significativi. Opera sempre con consapevolezza.</p>
        <p>📊 Dati: CFTC COT Report | Myfxbook Sentiment | Yahoo Finance</p>
        <p>🔄 Ultimo aggiornamento: {}</p>
    </div>
    """.format(datetime.now().strftime("%d/%m/%Y %H:%M:%S")), unsafe_allow_html=True)

except Exception as e:
    st.error(f"Errore nel caricamento dell'app: {str(e)}")
    st.info("Prova a ricaricare la pagina o attendi qualche minuto.")
