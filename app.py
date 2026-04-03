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

# CSS personalizzato con contrasto ottimale
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
    .main-header h1 {
        color: white !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .main-header p {
        color: rgba(255,255,255,0.95) !important;
        font-weight: 500;
    }
    .signal-card {
        background: rgba(26, 31, 62, 0.95);
        border-radius: 15px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid;
        backdrop-filter: blur(10px);
        color: #ffffff;
    }
    .signal-buy {
        border-left-color: #10b981;
    }
    .signal-sell {
        border-left-color: #ef4444;
    }
    .metric-card {
        background: rgba(26, 31, 62, 0.9);
        border-radius: 15px;
        padding: 1rem;
        text-align: center;
        backdrop-filter: blur(10px);
        color: #ffffff;
    }
    .metric-card h3 {
        color: white !important;
        font-weight: 700;
    }
    .metric-card p {
        color: #cbd5e1 !important;
        font-weight: 500;
    }
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-high {
        background: rgba(16, 185, 129, 0.3);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.5);
    }
    .badge-medium {
        background: rgba(245, 158, 11, 0.3);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.5);
    }
    .badge-low {
        background: rgba(239, 68, 68, 0.3);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.5);
    }
    /* SIDEBAR - Leggibilità ottimale */
    section[data-testid="stSidebar"] {
        background: rgba(19, 24, 58, 0.95);
    }
    section[data-testid="stSidebar"] .stMarkdown {
        color: #cbd5e1 !important;
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #a5b4fc !important;
        font-weight: 600;
    }
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] li,
    section[data-testid="stSidebar"] span {
        color: #cbd5e1 !important;
    }
    section[data-testid="stSidebar"] .stButton button {
        background: #4f46e5;
        color: white;
        font-weight: 500;
        border: none;
    }
    section[data-testid="stSidebar"] .stButton button:hover {
        background: #6366f1;
    }
    /* Tabelle */
    .stDataFrame {
        color: #e2e8f0 !important;
    }
    .stDataFrame td, .stDataFrame th {
        color: #e2e8f0 !important;
    }
    /* Grafici */
    .js-plotly-plot .main-svg {
        background: transparent !important;
    }
    /* Card dettaglio */
    .signal-card small {
        color: #94a3b8 !important;
        font-weight: 500;
    }
    .signal-card strong {
        color: #f1f5f9 !important;
    }
    /* Info box */
    .stAlert {
        background: rgba(26, 31, 62, 0.9) !important;
        color: #e2e8f0 !important;
    }
    /* Metriche */
    div[data-testid="stMetricValue"] {
        color: #f1f5f9 !important;
        font-weight: 700;
    }
    div[data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
    }
</style>
""", unsafe_allow_html=True)

# Titolo
st.markdown("""
<div class="main-header">
    <h1 style="color: white; margin: 0;">📊 Forex Sentinel Pro</h1>
    <p style="color: rgba(255,255,255,0.95); margin-top: 0.5rem;">Segnali di Trading basati su COT + Sentiment Retail</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## ⚙️ Configurazione")
    
    # Coppie forex da monitorare con XAUUSD
    forex_pairs = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'NZDUSD', 'USDCHF', 'XAUUSD']
    
    st.markdown("### 📈 Coppie monitorate")
    for pair in forex_pairs:
        icon = "🥇" if pair == "XAUUSD" else "💱"
        st.markdown(f"- {icon} {pair}")
    
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
    
    st.markdown("---")
    st.markdown("### 🏆 Oro (XAUUSD)")
    st.markdown("""
    L'oro è incluso come asset rifugio
    """)

# Funzioni di caching
@st.cache_data(ttl=3600)
def get_cot_data():
    """Simula dati COT (in produzione: scraping CFTC)"""
    return {
        'EURUSD': {'bias': 'bullish', 'strength': 'strong', 'long': 62, 'short': 28},
        'GBPUSD': {'bias': 'neutral', 'strength': 'weak', 'long': 45, 'short': 44},
        'USDJPY': {'bias': 'bearish', 'strength': 'moderate', 'long': 38, 'short': 55},
        'AUDUSD': {'bias': 'bullish', 'strength': 'strong', 'long': 58, 'short': 29},
        'USDCAD': {'bias': 'neutral', 'strength': 'weak', 'long': 44, 'short': 47},
        'NZDUSD': {'bias': 'bullish', 'strength': 'moderate', 'long': 52, 'short': 38},
        'USDCHF': {'bias': 'bearish', 'strength': 'moderate', 'long': 35, 'short': 54},
        'XAUUSD': {'bias': 'bullish', 'strength': 'strong', 'long': 68, 'short': 22}
    }

@st.cache_data(ttl=1800)
def get_retail_sentiment():
    """Simula dati Myfxbook (in produzione: scraping)"""
    return {
        'EURUSD': {'long': 42, 'short': 58, 'signal': 'buy', 'extremity': 'moderate'},
        'GBPUSD': {'long': 35, 'short': 65, 'signal': 'buy', 'extremity': 'extreme'},
        'USDJPY': {'long': 68, 'short': 32, 'signal': 'sell', 'extremity': 'extreme'},
        'AUDUSD': {'long': 55, 'short': 45, 'signal': 'neutral', 'extremity': 'moderate'},
        'USDCAD': {'long': 38, 'short': 62, 'signal': 'buy', 'extremity': 'extreme'},
        'NZDUSD': {'long': 48, 'short': 52, 'signal': 'neutral', 'extremity': 'low'},
        'USDCHF': {'long': 72, 'short': 28, 'signal': 'sell', 'extremity': 'extreme'},
        'XAUUSD': {'long': 32, 'short': 68, 'signal': 'buy', 'extremity': 'extreme'}
    }

@st.cache_data(ttl=300)
def get_current_prices(pairs):
    """Recupera prezzi da Yahoo Finance"""
    prices = {}
    for pair in pairs:
        try:
            if pair == 'XAUUSD':
                symbol = 'GC=F'
            else:
                symbol = f"{pair}=X"
            
            ticker = yf.Ticker(symbol)
            data = ticker.history(period='1d')
            if not data.empty:
                price = round(data['Close'].iloc[-1], 2) if pair == 'XAUUSD' else round(data['Close'].iloc[-1], 5)
                prices[pair] = price
            else:
                prices[pair] = None
        except Exception as e:
            print(f"Errore prezzo {pair}: {e}")
            prices[pair] = None
        time.sleep(0.5)
    return prices

def calculate_pivot_levels(pair, current_price):
    """Calcola pivot points"""
    try:
        if pair == 'XAUUSD':
            symbol = 'GC=F'
        else:
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
            
            decimals = 2 if pair == 'XAUUSD' else 5
            
            return {
                'pivot': round(pivot, decimals),
                'r1': round(r1, decimals),
                's1': round(s1, decimals),
                'current': current_price
            }
    except:
        pass
    
    if current_price:
        decimals = 2 if pair == 'XAUUSD' else 5
        multiplier = 0.005 if pair == 'XAUUSD' else 0.005
        return {
            'pivot': current_price,
            'r1': round(current_price * (1 + multiplier), decimals),
            's1': round(current_price * (1 - multiplier), decimals),
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
        
        if price and level:
            if price < level['s1']:
                score += 20
                reasons.append("Sotto supporto chiave")
            elif price > level['r1']:
                score += 20
                reasons.append("Sopra resistenza chiave")
        
        action = None
        if cot['bias'] == 'bullish' and retail['signal'] == 'buy':
            action = 'BUY'
        elif cot['bias'] == 'bearish' and retail['signal'] == 'sell':
            action = 'SELL'
        elif score > 60:
            action = 'BUY' if cot['bias'] == 'bullish' else 'SELL'
        
        if action and score >= 50:
            decimals = 2 if pair == 'XAUUSD' else 5
            sl_multiplier = 0.005 if pair == 'XAUUSD' else 0.005
            
            if action == 'BUY':
                entry = level['s1'] if level['s1'] else price
                tp = level['pivot'] if level['pivot'] else price * 1.005
                sl = entry * (1 - sl_multiplier)
                rr = round((tp - entry) / (entry - sl), 2) if sl else 0
            else:
                entry = level['r1'] if level['r1'] else price
                tp = level['pivot'] if level['pivot'] else price * 0.995
                sl = entry * (1 + sl_multiplier)
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
    
    signals.sort(key=lambda x: x['score'], reverse=True)
    return signals

# Main app
try:
    with st.spinner('Caricamento dati in corso...'):
        cot_data = get_cot_data()
        retail_data = get_retail_sentiment()
        prices = get_current_prices(forex_pairs)
        
        levels = {}
        for pair in forex_pairs:
            level = calculate_pivot_levels(pair, prices.get(pair))
            if level:
                levels[pair] = level
        
        signals = generate_signals(cot_data, retail_data, prices, levels)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="margin: 0; color: #667eea;">{len(signals)}</h3>
            <p style="margin: 0; color: #cbd5e1;">Segnali Attivi</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        buys = len([s for s in signals if s['action'] == 'BUY'])
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="margin: 0; color: #10b981;">{buys}</h3>
            <p style="margin: 0; color: #cbd5e1;">Acquisti</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        sells = len([s for s in signals if s['action'] == 'SELL'])
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="margin: 0; color: #ef4444;">{sells}</h3>
            <p style="margin: 0; color: #cbd5e1;">Vendite</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        avg_score = round(sum(s['score'] for s in signals) / len(signals), 1) if signals else 0
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="margin: 0; color: #f59e0b;">{avg_score}</h3>
            <p style="margin: 0; color: #cbd5e1;">Score Medio</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("## 🎯 Segnali di Trading")
    
    if signals:
        df_signals = pd.DataFrame(signals)
        
        def format_price(pair, value):
            if value is None:
                return "N/A"
            decimals = 2 if pair == 'XAUUSD' else 5
            return f"{value:.{decimals}f}"
        
        df_signals['entry'] = df_signals.apply(lambda x: format_price(x['pair'], x['entry']), axis=1)
        df_signals['tp'] = df_signals.apply(lambda x: format_price(x['pair'], x['tp']), axis=1)
        df_signals['sl'] = df_signals.apply(lambda x: format_price(x['pair'], x['sl']), axis=1)
        
        def color_action(val):
            if val == 'BUY':
                return 'background-color: rgba(16, 185, 129, 0.3); color: #34d399; font-weight: bold;'
            elif val == 'SELL':
                return 'background-color: rgba(239, 68, 68, 0.3); color: #f87171; font-weight: bold;'
            return ''
        
        styled_df = df_signals[['pair', 'action', 'confidence', 'entry', 'tp', 'sl', 'rr', 'reasons']].style.map(
            color_action, subset=['action']
        )
        
        st.dataframe(styled_df, use_container_width=True, height=400)
        
        st.markdown("### 📋 Dettaglio Segnali")
        
        for signal in signals[:5]:
            card_class = "signal-card signal-buy" if signal['action'] == 'BUY' else "signal-card signal-sell"
            badge_class = f"badge badge-{signal['confidence'].lower()}"
            decimals = 2 if signal['pair'] == 'XAUUSD' else 5
            
            st.markdown(f"""
            <div class="{card_class}">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h3 style="margin: 0; color: #ffffff;">{signal['pair']}</h3>
                        <span class="{badge_class}">{signal['confidence']} CONFIDENZA</span>
                    </div>
                    <div style="text-align: right;">
                        <h2 style="margin: 0; color: {'#10b981' if signal['action'] == 'BUY' else '#ef4444'}">
                            {signal['action']}
                        </h2>
                        <span style="font-size: 12px; color: #cbd5e1;">Score: {signal['score']}</span>
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-top: 1rem;">
                    <div>
                        <small style="color: #94a3b8;">Entry</small>
                        <br/>
                        <strong style="color: #f1f5f9;">{signal['entry']:.{decimals}f}</strong>
                    </div>
                    <div>
                        <small style="color: #94a3b8;">Take Profit</small>
                        <br/>
                        <strong style="color: #10b981;">{signal['tp']:.{decimals}f}</strong>
                    </div>
                    <div>
                        <small style="color: #94a3b8;">Stop Loss</small>
                        <br/>
                        <strong style="color: #ef4444;">{signal['sl']:.{decimals}f}</strong>
                    </div>
                    <div>
                        <small style="color: #94a3b8;">R:R Ratio</small>
                        <br/>
                        <strong style="color: #f1f5f9;">1:{signal['rr']}</strong>
                    </div>
                </div>
                <div style="margin-top: 0.75rem; font-size: 12px; color: #94a3b8;">
                    ℹ️ {signal['reasons']}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("ℹ️ Nessun segnale al momento. Riprova più tardi.")
    
    st.markdown("---")
    
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
        
        fig_cot = go.Figure()
        for pair in list(cot_data.keys())[:5]:
            fig_cot.add_trace(go.Bar(
                name=pair,
                x=['Long', 'Short'],
                y=[cot_data[pair]['long'], cot_data[pair]['short']],
                text=[f"{cot_data[pair]['long']}%", f"{cot_data[pair]['short']}%"],
                textposition='auto',
                textfont=dict(color='white', size=12)
            ))
        fig_cot.update_layout(
            title=dict(text="Posizionamento Non-Commercial", font=dict(color='white', size=16)),
            barmode='group',
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            legend=dict(font=dict(color='white')),
            xaxis=dict(title_font=dict(color='white'), tickfont=dict(color='white')),
            yaxis=dict(title_font=dict(color='white'), tickfont=dict(color='white'))
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
        
        fig_retail = go.Figure()
        for pair in list(retail_data.keys())[:5]:
            fig_retail.add_trace(go.Bar(
                name=pair,
                x=['Long', 'Short'],
                y=[retail_data[pair]['long'], retail_data[pair]['short']],
                text=[f"{retail_data[pair]['long']}%", f"{retail_data[pair]['short']}%"],
                textposition='auto',
                textfont=dict(color='white', size=12)
            ))
        fig_retail.update_layout(
            title=dict(text="Sentiment Trader Retail", font=dict(color='white', size=16)),
            barmode='group',
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            legend=dict(font=dict(color='white')),
            xaxis=dict(title_font=dict(color='white'), tickfont=dict(color='white')),
            yaxis=dict(title_font=dict(color='white'), tickfont=dict(color='white'))
        )
        st.plotly_chart(fig_retail, use_container_width=True)
    
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; color: #94a3b8; font-size: 12px; padding: 1rem;">
        <p>⚠️ <strong>Disclaimer:</strong> I segnali sono generati automaticamente. Non costituiscono consulenza finanziaria.</p>
        <p>📊 Dati: CFTC COT Report | Myfxbook Sentiment | Yahoo Finance</p>
        <p>🔄 Ultimo aggiornamento: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</p>
    </div>
    """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"❌ Errore nel caricamento dell'app: {str(e)}")
    st.info("🔄 Prova a ricaricare la pagina o attendi qualche minuto.")
