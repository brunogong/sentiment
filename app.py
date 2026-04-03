import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
import time

# Configurazione pagina
st.set_page_config(
    page_title="Forex Sentinel Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS completo con contrasto ottimale
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
        font-size: 2.5rem;
    }
    .main-header p {
        color: rgba(255,255,255,0.95) !important;
        font-size: 1.1rem;
    }
    .signal-card {
        background: rgba(26, 31, 62, 0.95);
        border-radius: 15px;
        padding: 1.25rem;
        margin: 0.75rem 0;
        border-left: 5px solid;
        backdrop-filter: blur(10px);
    }
    .signal-card-strong {
        border-left-color: #10b981;
        background: rgba(16, 185, 129, 0.12);
    }
    .signal-card-moderate {
        border-left-color: #f59e0b;
        background: rgba(245, 158, 11, 0.1);
    }
    .metric-card {
        background: rgba(26, 31, 62, 0.9);
        border-radius: 15px;
        padding: 1.25rem;
        text-align: center;
        backdrop-filter: blur(10px);
    }
    .metric-card h3 {
        color: white !important;
        font-size: 2rem;
        margin: 0;
    }
    .metric-card p {
        color: #cbd5e1 !important;
        margin: 0;
        font-size: 0.9rem;
    }
    .badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-strong {
        background: rgba(16, 185, 129, 0.25);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.5);
    }
    .badge-moderate {
        background: rgba(245, 158, 11, 0.25);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.5);
    }
    .rsi-badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
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
    /* Sidebar leggibile */
    section[data-testid="stSidebar"] {
        background: rgba(19, 24, 58, 0.97);
    }
    section[data-testid="stSidebar"] .stMarkdown {
        color: #e2e8f0 !important;
    }
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {
        color: #a5b4fc !important;
    }
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] li {
        color: #cbd5e1 !important;
    }
    .stDataFrame {
        color: #e2e8f0 !important;
    }
    .stDataFrame thead th {
        color: #a5b4fc !important;
        background: rgba(26, 31, 62, 0.8) !important;
    }
    .stDataFrame tbody td {
        color: #cbd5e1 !important;
    }
    /* Testo generale */
    .stMarkdown {
        color: #e2e8f0 !important;
    }
    label, .stSelectbox label, .stSlider label {
        color: #cbd5e1 !important;
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

# Sidebar
with st.sidebar:
    st.markdown("## ⚙️ Configurazione Strategia")
    
    st.markdown("### 🎯 Soglie Retail Sentiment")
    retail_long_threshold = st.slider(
        "Retail LONG > soglia (per SELL)",
        min_value=60, max_value=85, value=70, step=1
    )
    retail_short_threshold = st.slider(
        "Retail SHORT > soglia (per BUY)",
        min_value=60, max_value=85, value=70, step=1
    )
    
    st.markdown("---")
    st.markdown("### 📊 Soglie RSI")
    rsi_overbought = st.slider("RSI > soglia (Ipercomprato)", 60, 85, 70)
    rsi_oversold = st.slider("RSI < soglia (Ipervenduto)", 15, 40, 30)
    rsi_period = st.selectbox("Periodo RSI", [7, 14, 21, 30], index=1)
    
    st.markdown("---")
    if st.button("🔄 Aggiorna Dati", type="primary", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("---")
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

# Funzioni dati
@st.cache_data(ttl=3600)
def get_cot_data():
    return {
        'EURUSD': {'bias': 'bullish', 'long': 62, 'short': 28},
        'GBPUSD': {'bias': 'neutral', 'long': 45, 'short': 44},
        'USDJPY': {'bias': 'bearish', 'long': 38, 'short': 55},
        'AUDUSD': {'bias': 'bullish', 'long': 58, 'short': 29},
        'USDCAD': {'bias': 'neutral', 'long': 44, 'short': 47},
        'NZDUSD': {'bias': 'bullish', 'long': 52, 'short': 38},
        'USDCHF': {'bias': 'bearish', 'long': 35, 'short': 54},
        'XAUUSD': {'bias': 'bullish', 'long': 68, 'short': 22}
    }

@st.cache_data(ttl=1800)
def get_retail_sentiment():
    return {
        'EURUSD': {'long': 42, 'short': 58},
        'GBPUSD': {'long': 35, 'short': 65},
        'USDJPY': {'long': 72, 'short': 28},
        'AUDUSD': {'long': 55, 'short': 45},
        'USDCAD': {'long': 38, 'short': 62},
        'NZDUSD': {'long': 48, 'short': 52},
        'USDCHF': {'long': 75, 'short': 25},
        'XAUUSD': {'long': 32, 'short': 68}
    }

@st.cache_data(ttl=300)
def get_technical_data(pairs, rsi_period):
    data = {}
    for pair in pairs:
        try:
            symbol = 'GC=F' if pair == 'XAUUSD' else f"{pair}=X"
            ticker = yf.Ticker(symbol)
            
            hist = ticker.history(period='1d')
            if not hist.empty:
                price = round(hist['Close'].iloc[-1], 2 if pair == 'XAUUSD' else 5)
            else:
                price = None
            
            hist_rsi = ticker.history(period=f'{max(rsi_period * 3, 30)}d')
            if len(hist_rsi) >= rsi_period + 1:
                delta = hist_rsi['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=rsi_period).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                current_rsi = round(rsi.iloc[-1], 1)
            else:
                current_rsi = 50
            
            hist_pivot = ticker.history(period='5d')
            if len(hist_pivot) >= 2:
                yesterday = hist_pivot.iloc[-2]
                pivot = (yesterday['High'] + yesterday['Low'] + yesterday['Close']) / 3
                r1 = 2 * pivot - yesterday['Low']
                s1 = 2 * pivot - yesterday['High']
                decimals = 2 if pair == 'XAUUSD' else 5
                pivot = round(pivot, decimals)
                r1 = round(r1, decimals)
                s1 = round(s1, decimals)
            else:
                pivot = price if price else 1.10
                if pair == 'XAUUSD':
                    r1 = round(pivot * 1.005, 2)
                    s1 = round(pivot * 0.995, 2)
                else:
                    r1 = round(pivot * 1.005, 5)
                    s1 = round(pivot * 0.995, 5)
            
            data[pair] = {
                'price': price,
                'rsi': current_rsi,
                'pivot': pivot,
                'r1': r1,
                's1': s1
            }
        except Exception as e:
            data[pair] = {'price': None, 'rsi': 50, 'pivot': None, 'r1': None, 's1': None}
        time.sleep(0.3)
    return data

def format_price(pair, value):
    if value is None:
        return "N/A"
    if pair == 'XAUUSD':
        return f"{value:.2f}"
    return f"{value:.5f}"

def generate_signals(cot_data, retail_data, tech_data, thresholds):
    signals = []
    for pair in cot_data:
        if pair not in retail_data or pair not in tech_data:
            continue
        
        cot = cot_data[pair]
        retail = retail_data[pair]
        tech = tech_data[pair]
        
        conditions = []
        action = None
        
        # Check SELL
        if retail['long'] > thresholds['retail_long']:
            conditions.append(f"📊 Retail LONG {retail['long']}% > {thresholds['retail_long']}%")
            if cot['bias'] == 'bearish':
                conditions.append(f"🏦 COT Bearish")
            if tech['rsi'] > thresholds['rsi_overbought']:
                conditions.append(f"📈 RSI {tech['rsi']} > {thresholds['rsi_overbought']}")
            
            if len([c for c in conditions if 'COT' in c or 'RSI' in c]) >= 2:
                action = 'SELL'
        
        # Reset per BUY
        conditions = []
        if retail['short'] > thresholds['retail_short']:
            conditions.append(f"📊 Retail SHORT {retail['short']}% > {thresholds['retail_short']}%")
            if cot['bias'] == 'bullish':
                conditions.append(f"🏦 COT Bullish")
            if tech['rsi'] < thresholds['rsi_oversold']:
                conditions.append(f"📉 RSI {tech['rsi']} < {thresholds['rsi_oversold']}")
            
            if len([c for c in conditions if 'COT' in c or 'RSI' in c]) >= 2:
                action = 'BUY'
        
        if action:
            if action == 'BUY':
                entry = tech['s1'] if tech['s1'] else tech['price']
                tp = tech['pivot'] if tech['pivot'] else (entry * 1.005 if entry else None)
                sl = entry * 0.995 if entry else None
            else:
                entry = tech['r1'] if tech['r1'] else tech['price']
                tp = tech['pivot'] if tech['pivot'] else (entry * 0.995 if entry else None)
                sl = entry * 1.005 if entry else None
            
            rr = round(abs((tp - entry) / (entry - sl)), 2) if entry and sl and entry != sl else 0
            score = len([c for c in conditions if 'COT' in c or 'RSI' in c]) + 1
            
            signals.append({
                'pair': pair,
                'action': action,
                'score': score,
                'confidence': 'STRONG' if score >= 3 else 'MODERATE',
                'entry': entry,
                'tp': tp,
                'sl': sl,
                'rr': rr,
                'retail_long': retail['long'],
                'retail_short': retail['short'],
                'cot_bias': cot['bias'],
                'rsi': tech['rsi'],
                'conditions': ' + '.join(conditions)
            })
    
    return sorted(signals, key=lambda x: x['score'], reverse=True)

# Main
try:
    forex_pairs = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'NZDUSD', 'USDCHF', 'XAUUSD']
    thresholds = {
        'retail_long': retail_long_threshold,
        'retail_short': retail_short_threshold,
        'rsi_overbought': rsi_overbought,
        'rsi_oversold': rsi_oversold
    }
    
    with st.spinner('Caricamento dati in corso...'):
        cot_data = get_cot_data()
        retail_data = get_retail_sentiment()
        tech_data = get_technical_data(forex_pairs, rsi_period)
        signals = generate_signals(cot_data, retail_data, tech_data, thresholds)
    
    # Metriche
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #10b981;">{len([s for s in signals if s['score'] >= 3])}</h3>
            <p>🔴🔴🔴 Triple Conferma</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #f59e0b;">{len([s for s in signals if 2 <= s['score'] < 3])}</h3>
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
    st.markdown("## 🎯 Segnali di Trading")
    
    if signals:
        for signal in signals:
            card_class = "signal-card-strong" if signal['score'] >= 3 else "signal-card-moderate"
            badge_class = "badge-strong" if signal['confidence'] == 'STRONG' else "badge-moderate"
            
            # Determina classe RSI
            if signal['rsi'] > rsi_overbought:
                rsi_class = "rsi-overbought"
                rsi_text = f"🔥 RSI {signal['rsi']} (Overbought)"
            elif signal['rsi'] < rsi_oversold:
                rsi_class = "rsi-oversold"
                rsi_text = f"💚 RSI {signal['rsi']} (Oversold)"
            else:
                rsi_class = "rsi-neutral"
                rsi_text = f"⚪ RSI {signal['rsi']} (Neutrale)"
            
            st.markdown(f"""
            <div class="signal-card {card_class}">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; margin-bottom: 1rem;">
                    <div>
                        <h2 style="margin: 0; color: white; font-size: 1.5rem;">{signal['pair']}</h2>
                        <span class="badge {badge_class}">{signal['confidence']}</span>
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
                        <div style="font-weight: bold; color: white;">{signal['rsi']}</div>
                        <div><span class="rsi-badge {rsi_class}">{rsi_text}</span></div>
                    </div>
                </div>
                
                <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 0.75rem; margin-top: 0.75rem;">
                    <div>
                        <small style="color: #94a3b8;">Entry</small>
                        <br/>
                        <strong style="color: white;">{format_price(signal['pair'], signal['entry'])}</strong>
                    </div>
                    <div>
                        <small style="color: #94a3b8;">Take Profit</small>
                        <br/>
                        <strong style="color: #10b981;">{format_price(signal['pair'], signal['tp'])}</strong>
                    </div>
                    <div>
                        <small style="color: #94a3b8;">Stop Loss</small>
                        <br/>
                        <strong style="color: #ef4444;">{format_price(signal['pair'], signal['sl'])}</strong>
                    </div>
                    <div>
                        <small style="color: #94a3b8;">R:R Ratio</small>
                        <br/>
                        <strong style="color: white;">1:{signal['rr']}</strong>
                    </div>
                    <div>
                        <small style="color: #94a3b8;">Score</small>
                        <br/>
                        <strong style="color: #f59e0b;">{signal['score']}/3</strong>
                    </div>
                </div>
                
                <div style="margin-top: 0.75rem; font-size: 11px; color: #64748b; text-align: center;">
                    {signal['conditions']}
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
        tech = tech_data.get(pair, {})
        
        rsi = tech.get('rsi', 50)
        
        # Determina segnale potenziale
        potential_signal = "⚪ ATTESA"
        if retail.get('long', 0) > retail_long_threshold and cot.get('bias') == 'bearish' and rsi > rsi_overbought:
            potential_signal = "🔴 SELL (Tripla)"
        elif retail.get('long', 0) > retail_long_threshold and cot.get('bias') == 'bearish':
            potential_signal = "🟡 SELL (Doppia)"
        elif retail.get('short', 0) > retail_short_threshold and cot.get('bias') == 'bullish' and rsi < rsi_oversold:
            potential_signal = "🟢 BUY (Tripla)"
        elif retail.get('short', 0) > retail_short_threshold and cot.get('bias') == 'bullish':
            potential_signal = "🟡 BUY (Doppia)"
        
        price = tech.get('price')
        if price:
            price_str = f"{price:.2f}" if pair == 'XAUUSD' else f"{price:.5f}"
        else:
            price_str = "N/A"
        
        summary_data.append({
            'Coppia': pair,
            'Prezzo': price_str,
            f'RSI({rsi_period})': rsi,
            'Retail L/S': f"{retail.get('long', 0)}% / {retail.get('short', 0)}%",
            'COT': cot.get('bias', 'N/A').upper(),
            'Segnale': potential_signal
        })
    
    df_summary = pd.DataFrame(summary_data)
    st.dataframe(df_summary, use_container_width=True, hide_index=True)
    
    # Legenda
    st.markdown(f"""
    <div style="background: rgba(0,0,0,0.3); padding: 1rem; border-radius: 10px; margin-top: 1rem;">
        <h4 style="color: white;">📖 Legenda Segnali</h4>
        <table style="width: 100%; color: #cbd5e1;">
            <tr><td>🔴 SELL (Tripla)</td><td>Retail LONG >{retail_long_threshold}% + COT Bearish + RSI >{rsi_overbought}</td></tr>
            <tr><td>🟢 BUY (Tripla)</td><td>Retail SHORT >{retail_short_threshold}% + COT Bullish + RSI &lt;{rsi_oversold}</td></tr>
            <tr><td>🟡 Doppia</td><td>Solo 2 condizioni su 3 sono verificate</td></tr>
            <tr><td>⚪ ATTESA</td><td>Condizioni non ancora mature</td></tr>
        </table>
    </div>
    """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; color: #64748b; font-size: 11px; padding: 1rem;">
        <p>⚠️ Disclaimer: I segnali sono generati automaticamente. Non costituiscono consulenza finanziaria.</p>
        <p>🔄 Ultimo aggiornamento: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</p>
    </div>
    """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"❌ Errore: {str(e)}")
    st.info("🔄 Ricarica la pagina o attendi qualche minuto.")
