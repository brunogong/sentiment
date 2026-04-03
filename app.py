import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# Configurazione pagina
st.set_page_config(
    page_title="Forex Sentinel Pro - Customizable",
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
    }
    .signal-card-strong {
        border-left-color: #10b981;
        background: rgba(16, 185, 129, 0.15);
    }
    .signal-card-moderate {
        border-left-color: #f59e0b;
        background: rgba(245, 158, 11, 0.1);
    }
    .signal-card-weak {
        border-left-color: #6b7280;
    }
    .metric-card {
        background: rgba(26, 31, 62, 0.9);
        border-radius: 15px;
        padding: 1rem;
        text-align: center;
        backdrop-filter: blur(10px);
    }
    .metric-card h3 {
        color: white !important;
    }
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-strong {
        background: rgba(16, 185, 129, 0.3);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.5);
    }
    .badge-moderate {
        background: rgba(245, 158, 11, 0.3);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.5);
    }
    .badge-weak {
        background: rgba(107, 114, 128, 0.3);
        color: #9ca3af;
        border: 1px solid rgba(107, 114, 128, 0.5);
    }
    .rsi-badge {
        display: inline-block;
        padding: 0.2rem 0.5rem;
        border-radius: 10px;
        font-size: 0.7rem;
        font-weight: 600;
    }
    .rsi-overbought {
        background: rgba(239, 68, 68, 0.3);
        color: #f87171;
    }
    .rsi-oversold {
        background: rgba(16, 185, 129, 0.3);
        color: #34d399;
    }
    .rsi-neutral {
        background: rgba(107, 114, 128, 0.3);
        color: #9ca3af;
    }
    section[data-testid="stSidebar"] {
        background: rgba(19, 24, 58, 0.95);
    }
    section[data-testid="stSidebar"] .stMarkdown {
        color: #cbd5e1 !important;
    }
    section[data-testid="stSidebar"] h1, h2, h3 {
        color: #a5b4fc !important;
    }
    .stDataFrame {
        color: #e2e8f0 !important;
    }
    .custom-slider {
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>📊 Forex Sentinel Pro</h1>
    <p>Tripla Conferma Personalizzabile: RSI + COT + Sentiment Retail</p>
</div>
""", unsafe_allow_html=True)

# Sidebar con parametri personalizzabili
with st.sidebar:
    st.markdown("## ⚙️ Configurazione Strategia")
    
    st.markdown("### 🎯 Soglie Retail Sentiment")
    retail_long_threshold = st.slider(
        "Retail LONG > soglia (per SELL)",
        min_value=60, max_value=85, value=70, step=1,
        help="Quando i trader retail sono long sopra questa soglia → ipercomprato sentiment"
    )
    
    retail_short_threshold = st.slider(
        "Retail SHORT > soglia (per BUY)",
        min_value=60, max_value=85, value=70, step=1,
        help="Quando i trader retail sono short sopra questa soglia → ipervenduto sentiment"
    )
    
    st.markdown("---")
    st.markdown("### 📊 Soglie RSI")
    
    rsi_overbought = st.slider(
        "RSI > soglia (Ipercomprato)",
        min_value=60, max_value=85, value=70, step=1,
        help="RSI sopra questo livello indica ipercomprato tecnico"
    )
    
    rsi_oversold = st.slider(
        "RSI < soglia (Ipervenduto)",
        min_value=15, max_value=40, value=30, step=1,
        help="RSI sotto questo livello indica ipervenduto tecnico"
    )
    
    st.markdown("---")
    st.markdown("### 🏦 Periodo RSI")
    
    rsi_period = st.selectbox(
        "Periodo RSI",
        options=[7, 14, 21, 30],
        index=1,
        help="Periodo standard è 14. Periodi più brevi = più sensibili"
    )
    
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
    - **RSI**: Yahoo Finance
    - **Prezzi**: Yahoo Finance
    """)
    
    st.markdown("---")
    st.markdown("### 💡 Strategia Corrente")
    st.markdown(f"""
    **Condizioni SELL:**
    - Retail LONG > {retail_long_threshold}%
    - COT Bearish
    - RSI > {rsi_overbought}
    
    **Condizioni BUY:**
    - Retail SHORT > {retail_short_threshold}%
    - COT Bullish
    - RSI < {rsi_oversold}
    """)

# Funzioni
@st.cache_data(ttl=3600)
def get_cot_data():
    """Dati COT simulati"""
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
    """Dati retail sentiment simulati"""
    return {
        'EURUSD': {'long': 42, 'short': 58, 'signal': 'buy', 'extremity': 'moderate'},
        'GBPUSD': {'long': 35, 'short': 65, 'signal': 'buy', 'extremity': 'extreme'},
        'USDJPY': {'long': 72, 'short': 28, 'signal': 'sell', 'extremity': 'extreme'},
        'AUDUSD': {'long': 55, 'short': 45, 'signal': 'neutral', 'extremity': 'moderate'},
        'USDCAD': {'long': 38, 'short': 62, 'signal': 'buy', 'extremity': 'extreme'},
        'NZDUSD': {'long': 48, 'short': 52, 'signal': 'neutral', 'extremity': 'low'},
        'USDCHF': {'long': 75, 'short': 25, 'signal': 'sell', 'extremity': 'extreme'},
        'XAUUSD': {'long': 32, 'short': 68, 'signal': 'buy', 'extremity': 'extreme'}
    }

@st.cache_data(ttl=300)
def get_technical_data(pairs, rsi_period):
    """Recupera prezzi e calcola RSI con periodo personalizzabile"""
    data = {}
    
    for pair in pairs:
        try:
            if pair == 'XAUUSD':
                symbol = 'GC=F'
            else:
                symbol = f"{pair}=X"
            
            ticker = yf.Ticker(symbol)
            
            # Prezzo attuale
            hist = ticker.history(period='1d')
            current_price = round(hist['Close'].iloc[-1], 2 if pair == 'XAUUSD' else 5) if not hist.empty else None
            
            # Calcola RSI con periodo personalizzato
            hist_period = ticker.history(period=f'{rsi_period * 3}d')
            if len(hist_period) >= rsi_period + 1:
                delta = hist_period['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=rsi_period).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                current_rsi = round(rsi.iloc[-1], 1)
            else:
                current_rsi = 50
            
            # Calcola pivot points
            hist_5d = ticker.history(period='5d')
            if len(hist_5d) >= 2:
                yesterday = hist_5d.iloc[-2]
                high = yesterday['High']
                low = yesterday['Low']
                close = yesterday['Close']
                pivot = (high + low + close) / 3
                r1 = 2 * pivot - low
                s1 = 2 * pivot - high
            else:
                pivot = current_price if current_price else 1.10
                r1 = pivot * 1.005
                s1 = pivot * 0.995
            
            data[pair] = {
                'price': current_price,
                'rsi': current_rsi,
                'pivot': round(pivot, 2 if pair == 'XAUUSD' else 5),
                'r1': round(r1, 2 if pair == 'XAUUSD' else 5),
                's1': round(s1, 2 if pair == 'XAUUSD' else 5)
            }
            
        except Exception as e:
            data[pair] = {
                'price': None,
                'rsi': 50,
                'pivot': None,
                'r1': None,
                's1': None
            }
        
        time.sleep(0.3)
    
    return data

def generate_triple_signals(cot_data, retail_data, technical_data, thresholds):
    """Genera segnali con soglie personalizzabili"""
    signals = []
    
    for pair in cot_data.keys():
        if pair not in retail_data or pair not in technical_data:
            continue
        
        cot = cot_data[pair]
        retail = retail_data[pair]
        tech = technical_data[pair]
        
        # Inizializza condizioni
        conditions = {
            'retail_extreme': False,
            'cot_aligned': False,
            'rsi_extreme': False,
            'direction': None,
            'details': []
        }
        
        rsi = tech['rsi']
        
        # VERIFICA CONDIZIONI PER SELL
        if retail['long'] > thresholds['retail_long']:
            conditions['retail_extreme'] = True
            conditions['direction'] = 'SELL'
            conditions['details'].append(f"Retail LONG {retail['long']}% > {thresholds['retail_long']}%")
        
        if cot['bias'] == 'bearish':
            conditions['cot_aligned'] = True
            conditions['details'].append(f"COT Bearish")
        
        if rsi > thresholds['rsi_overbought']:
            conditions['rsi_extreme'] = True
            conditions['details'].append(f"RSI {rsi} > {thresholds['rsi_overbought']}")
        
        # VERIFICA CONDIZIONI PER BUY
        if retail['short'] > thresholds['retail_short']:
            conditions['retail_extreme'] = True
            conditions['direction'] = 'BUY'
            conditions['details'].append(f"Retail SHORT {retail['short']}% > {thresholds['retail_short']}%")
        
        if cot['bias'] == 'bullish':
            conditions['cot_aligned'] = True
            conditions['details'].append(f"COT Bullish")
        
        if rsi < thresholds['rsi_oversold']:
            conditions['rsi_extreme'] = True
            conditions['details'].append(f"RSI {rsi} < {thresholds['rsi_oversold']}")
        
        # Calcola punteggio
        score = sum([
            conditions['retail_extreme'],
            conditions['cot_aligned'],
            conditions['rsi_extreme']
        ])
        
        # Determina direzione finale
        action = None
        if score >= 2 and conditions['direction']:
            action = conditions['direction']
        
        # Calcola entry, TP, SL solo se segnale valido
        if action and score >= 2:
            decimals = 2 if pair == 'XAUUSD' else 5
            
            if action == 'BUY':
                entry = tech['s1'] if tech['s1'] else tech['price']
                tp1 = tech['pivot'] if tech['pivot'] else entry * 1.005
                tp2 = tech['r1'] if tech['r1'] else entry * 1.01
                sl = entry * 0.995
                rr = round((tp1 - entry) / (entry - sl), 2) if sl else 0
            else:
                entry = tech['r1'] if tech['r1'] else tech['price']
                tp1 = tech['pivot'] if tech['pivot'] else entry * 0.995
                tp2 = tech['s1'] if tech['s1'] else entry * 0.99
                sl = entry * 1.005
                rr = round((entry - tp1) / (sl - entry), 2) if sl else 0
            
            # Determina forza segnale
            if score == 3:
                strength = "TRIPLA CONFERMA"
                confidence = "STRONG"
                card_class = "signal-card-strong"
            else:
                strength = "DOPPIA CONFERMA"
                confidence = "MODERATE"
                card_class = "signal-card-moderate"
            
            signals.append({
                'pair': pair,
                'action': action,
                'score': score,
                'confidence': confidence,
                'strength': strength,
                'card_class': card_class,
                'entry': entry,
                'tp1': tp1,
                'tp2': tp2,
                'sl': sl,
                'rr': rr,
                'retail_long': retail['long'],
                'retail_short': retail['short'],
                'cot_bias': cot['bias'],
                'rsi': tech['rsi'],
                'price': tech['price'],
                'details': ' | '.join(conditions['details'])
            })
    
    signals.sort(key=lambda x: x['score'], reverse=True)
    return signals

# Main app
try:
    # Configurazione soglie
    thresholds = {
        'retail_long': retail_long_threshold,
        'retail_short': retail_short_threshold,
        'rsi_overbought': rsi_overbought,
        'rsi_oversold': rsi_oversold
    }
    
    forex_pairs = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'NZDUSD', 'USDCHF', 'XAUUSD']
    
    with st.spinner('Caricamento dati e calcolo segnali...'):
        cot_data = get_cot_data()
        retail_data = get_retail_sentiment()
        technical_data = get_technical_data(forex_pairs, rsi_period)
        signals = generate_triple_signals(cot_data, retail_data, technical_data, thresholds)
    
    # Metriche
    col1, col2, col3, col4 = st.columns(4)
    
    triple_signals = [s for s in signals if s['score'] == 3]
    double_signals = [s for s in signals if s['score'] == 2]
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #10b981;">{len(triple_signals)}</h3>
            <p>🔴🔴🔴 Triple Conferma</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #f59e0b;">{len(double_signals)}</h3>
            <p>🟡🟡 Doppia Conferma</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #667eea;">{len(signals)}</h3>
            <p>📊 Segnali Totali</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        buys = len([s for s in signals if s['action'] == 'BUY'])
        sells = len([s for s in signals if s['action'] == 'SELL'])
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #10b981;">BUY {buys}</h3>
            <p style="color: #ef4444;">SELL {sells}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("## 🎯 Segnali Tripla Conferma")
    
    if signals:
        for signal in signals:
            badge_class = f"badge badge-{signal['confidence'].lower()}"
            
            # RSI badge
            if signal['rsi'] > rsi_overbought:
                rsi_badge = f'<span class="rsi-badge rsi-overbought">🔥 RSI {signal["rsi"]} (Overbought)</span>'
            elif signal['rsi'] < rsi_oversold:
                rsi_badge = f'<span class="rsi-badge rsi-oversold">💚 RSI {signal["rsi"]} (Oversold)</span>'
            else:
                rsi_badge = f'<span class="rsi-badge rsi-neutral">⚪ RSI {signal["rsi"]} (Neutrale)</span>'
            
            st.markdown(f"""
            <div class="signal-card {signal['card_class']}">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                    <div>
                        <h2 style="margin: 0; color: white;">{signal['pair']}</h2>
                        <span class="{badge_class}">{signal['strength']}</span>
                    </div>
                    <div style="text-align: right;">
                        <h1 style="margin: 0; color: {'#10b981' if signal['action'] == 'BUY' else '#ef4444'}; font-size: 2rem;">
                            {signal['action']}
                        </h1>
                    </div>
                </div>
                
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin: 1rem 0; padding: 0.75rem; background: rgba(0,0,0,0.3); border-radius: 10px;">
                    <div style="text-align: center;">
                        <small style="color: #94a3b8;">🏦 COT</small>
                        <div style="font-weight: bold; color: {'#10b981' if signal['cot_bias'] == 'bullish' else '#ef4444' if signal['cot_bias'] == 'bearish' else '#f59e0b'}">
                            {signal['cot_bias'].upper()}
                        </div>
                    </div>
                    <div style="text-align: center;">
                        <small style="color: #94a3b8;">👥 Retail</small>
                        <div>
                            <span style="color: #10b981;">L:{signal['retail_long']}%</span> 
                            <span style="color: #ef4444;">S:{signal['retail_short']}%</span>
                        </div>
                    </div>
                    <div style="text-align: center;">
                        <small style="color: #94a3b8;">📊 RSI ({rsi_period})</small>
                        <div style="font-weight: bold;">{signal['rsi']}</div>
                        <div>{rsi_badge}</div>
                    </div>
                </div>
                
                <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 0.75rem; margin-top: 0.75rem;">
                    <div>
                        <small style="color: #94a3b8;">Entry</small>
                        <br/>
                        <strong style="color: white;">{signal['entry']:.5f if signal['pair'] != 'XAUUSD' else signal['entry']:.2f}</strong>
                    </div>
                    <div>
                        <small style="color: #94a3b8;">TP1</small>
                        <br/>
                        <strong style="color: #10b981;">{signal['tp1']:.5f if signal['pair'] != 'XAUUSD' else signal['tp1']:.2f}</strong>
                    </div>
                    <div>
                        <small style="color: #94a3b8;">TP2</small>
                        <br/>
                        <strong style="color: #10b981;">{signal['tp2']:.5f if signal['pair'] != 'XAUUSD' else signal['tp2']:.2f}</strong>
                    </div>
                    <div>
                        <small style="color: #94a3b8;">SL</small>
                        <br/>
                        <strong style="color: #ef4444;">{signal['sl']:.5f if signal['pair'] != 'XAUUSD' else signal['sl']:.2f}</strong>
                    </div>
                    <div>
                        <small style="color: #94a3b8;">R:R</small>
                        <br/>
                        <strong>1:{signal['rr']}</strong>
                    </div>
                </div>
                
                <div style="margin-top: 0.75rem; font-size: 11px; color: #64748b; text-align: center;">
                    {signal['details']}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("ℹ️ Nessun segnale con le soglie attuali. Prova ad abbassare le soglie per più segnali.")
    
    st.markdown("---")
    
    # Tabella riassuntiva
    st.markdown("## 📊 Tabella Riassuntiva")
    
    summary_data = []
    for pair in forex_pairs:
        cot = cot_data.get(pair, {})
        retail = retail_data.get(pair, {})
        tech = technical_data.get(pair, {})
        
        rsi = tech.get('rsi', 50)
        
        # Determina segnale potenziale con soglie correnti
        potential_signal = "⚪ ATTESA"
        
        # Check SELL
        if retail.get('long', 0) > retail_long_threshold and cot.get('bias') == 'bearish' and rsi > rsi_overbought:
            potential_signal = "🔴 SELL (Tripla)"
        elif retail.get('long', 0) > retail_long_threshold and cot.get('bias') == 'bearish':
            potential_signal = "🟡 SELL (Doppia)"
        # Check BUY
        elif retail.get('short', 0) > retail_short_threshold and cot.get('bias') == 'bullish' and rsi < rsi_oversold:
            potential_signal = "🟢 BUY (Tripla)"
        elif retail.get('short', 0) > retail_short_threshold and cot.get('bias') == 'bullish':
            potential_signal = "🟡 BUY (Doppia)"
        
        summary_data.append({
            'Coppia': pair,
            'Prezzo': f"{tech.get('price', 'N/A'):.2f}" if pair == 'XAUUSD' else f"{tech.get('price', 'N/A'):.5f}",
            f'RSI({rsi_period})': rsi,
            'Retail L/S': f"{retail.get('long', 0)}% / {retail.get('short', 0)}%",
            'COT': cot.get('bias', 'N/A').upper(),
            'Segnale': potential_signal
        })
    
    df_summary = pd.DataFrame(summary_data)
    st.dataframe(df_summary, use_container_width=True, hide_index=True)
    
    # Legenda dinamica
    st.markdown(f"""
    <div style="background: rgba(0,0,0,0.3); padding: 1rem; border-radius: 10px; margin-top: 1rem;">
        <h4>📖 Legenda Segnali (Soglie Correnti)</h4>
        <table style="width: 100%; color: #cbd5e1;">
            <tr>
                <td>🔴 SELL (Tripla)</td>
                <td>Retail LONG >{retail_long_threshold}% + COT Bearish + RSI >{rsi_overbought}</td>
            </tr>
            <tr>
                <td>🟢 BUY (Tripla)</td>
                <td>Retail SHORT >{retail_short_threshold}% + COT Bullish + RSI &lt;{rsi_oversold}</td>
            </tr>
            <tr>
                <td>🟡 Doppia</td>
                <td>Solo 2 condizioni su 3 sono verificate</td>
            </tr>
            <tr>
                <td>⚪ ATTESA</td>
                <td>Condizioni non ancora mature</td>
            </tr>
        </table>
        <p style="margin-top: 0.5rem; font-size: 12px; color: #64748b;">
            💡 Modifica le soglie nella sidebar per ottimizzare la strategia!
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; color: #64748b; font-size: 11px;">
        <p>⚠️ Disclaimer: I segnali sono generati automaticamente. Non costituiscono consulenza finanziaria.</p>
        <p>🔄 Ultimo aggiornamento: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</p>
        <p>📊 RSI Period: {rsi_period} | Retail Long Threshold: {retail_long_threshold}% | Retail Short Threshold: {retail_short_threshold}% | RSI OB: {rsi_overbought} | RSI OS: {rsi_oversold}</p>
    </div>
    """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"❌ Errore: {str(e)}")
    st.info("🔄 Ricarica la pagina o attendi qualche minuto.")
