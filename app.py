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

# CSS minimale
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
    }
    .metric-card {
        background: rgba(26, 31, 62, 0.9);
        border-radius: 15px;
        padding: 1rem;
        text-align: center;
    }
    section[data-testid="stSidebar"] {
        background: rgba(19, 24, 58, 0.95);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>📊 Forex Sentinel Pro</h1>
    <p>Tripla Conferma: RSI + COT + Sentiment Retail</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## ⚙️ Configurazione")
    
    retail_long_threshold = st.slider("Retail LONG > soglia (per SELL)", 60, 85, 70)
    retail_short_threshold = st.slider("Retail SHORT > soglia (per BUY)", 60, 85, 70)
    rsi_overbought = st.slider("RSI > soglia (Ipercomprato)", 60, 85, 70)
    rsi_oversold = st.slider("RSI < soglia (Ipervenduto)", 15, 40, 30)
    rsi_period = st.selectbox("Periodo RSI", [7, 14, 21, 30], index=1)
    
    if st.button("🔄 Aggiorna Dati", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

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
            
            hist_rsi = ticker.history(period=f'{rsi_period * 3}d')
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
                r1 = round(pivot * 1.005, 2 if pair == 'XAUUSD' else 5)
                s1 = round(pivot * 0.995, 2 if pair == 'XAUUSD' else 5)
            
            data[pair] = {'price': price, 'rsi': current_rsi, 'pivot': pivot, 'r1': r1, 's1': s1}
        except:
            data[pair] = {'price': None, 'rsi': 50, 'pivot': None, 'r1': None, 's1': None}
        time.sleep(0.3)
    return data

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
                tp = tech['pivot'] if tech['pivot'] else entry * 1.005
                sl = entry * 0.995
            else:
                entry = tech['r1'] if tech['r1'] else tech['price']
                tp = tech['pivot'] if tech['pivot'] else entry * 0.995
                sl = entry * 1.005
            
            rr = round(abs((tp - entry) / (entry - sl)), 2) if entry and sl else 0
            score = len([c for c in conditions if 'COT' in c or 'RSI' in c]) + 1
            
            signals.append({
                'pair': pair,
                'action': action,
                'score': score,
                'confidence': 'ALTA' if score >= 3 else 'MEDIA',
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
    
    with st.spinner('Caricamento dati...'):
        cot_data = get_cot_data()
        retail_data = get_retail_sentiment()
        tech_data = get_technical_data(forex_pairs, rsi_period)
        signals = generate_signals(cot_data, retail_data, tech_data, thresholds)
    
    # Metriche
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🔴 Triple Conferma", len([s for s in signals if s['score'] >= 3]))
    with col2:
        st.metric("🟡 Doppia Conferma", len([s for s in signals if 2 <= s['score'] < 3]))
    with col3:
        st.metric("📊 Segnali Totali", len(signals))
    with col4:
        st.metric("🟢 BUY / 🔴 SELL", f"{len([s for s in signals if s['action'] == 'BUY'])} / {len([s for s in signals if s['action'] == 'SELL'])}")
    
    st.markdown("---")
    st.markdown("## 🎯 Segnali di Trading")
    
    if signals:
        for signal in signals:
            # Usa container di Streamlit invece di HTML personalizzato
            with st.container():
                col_left, col_right = st.columns([3, 1])
                
                with col_left:
                    st.markdown(f"### {signal['pair']}")
                    st.markdown(f"**{signal['action']}** - Confidenza: {signal['confidence']}")
                    st.markdown(f"_{signal['conditions']}_")
                
                with col_right:
                    st.metric("Score", f"{signal['score']}/3")
                
                # Dettagli in colonne
                c1, c2, c3, c4, c5 = st.columns(5)
                with c1:
                    st.metric("Entry", f"{signal['entry']:.5f}" if signal['pair'] != 'XAUUSD' else f"{signal['entry']:.2f}")
                with c2:
                    st.metric("Take Profit", f"{signal['tp']:.5f}" if signal['pair'] != 'XAUUSD' else f"{signal['tp']:.2f}", delta="TP")
                with c3:
                    st.metric("Stop Loss", f"{signal['sl']:.5f}" if signal['pair'] != 'XAUUSD' else f"{signal['sl']:.2f}", delta="SL", delta_color="inverse")
                with c4:
                    st.metric("R:R Ratio", f"1:{signal['rr']}")
                with c5:
                    st.metric("RSI", signal['rsi'])
                
                st.markdown("---")
    else:
        st.info("ℹ️ Nessun segnale con le soglie attuali. Prova ad abbassare le soglie.")
    
    # Tabella riassuntiva
    st.markdown("## 📊 Tabella Riassuntiva")
    
    summary = []
    for pair in forex_pairs:
        cot = cot_data.get(pair, {})
        retail = retail_data.get(pair, {})
        tech = tech_data.get(pair, {})
        
        signal_text = "⚪ ATTESA"
        if retail.get('long', 0) > retail_long_threshold and cot.get('bias') == 'bearish' and tech.get('rsi', 50) > rsi_overbought:
            signal_text = "🔴 SELL (Tripla)"
        elif retail.get('short', 0) > retail_short_threshold and cot.get('bias') == 'bullish' and tech.get('rsi', 50) < rsi_oversold:
            signal_text = "🟢 BUY (Tripla)"
        elif retail.get('long', 0) > retail_long_threshold and cot.get('bias') == 'bearish':
            signal_text = "🟡 SELL (Doppia)"
        elif retail.get('short', 0) > retail_short_threshold and cot.get('bias') == 'bullish':
            signal_text = "🟡 BUY (Doppia)"
        
        price = tech.get('price')
        price_str = f"{price:.2f}" if price and pair == 'XAUUSD' else f"{price:.5f}" if price else "N/A"
        
        summary.append({
            'Coppia': pair,
            'Prezzo': price_str,
            f'RSI({rsi_period})': tech.get('rsi', 50),
            'Retail L/S': f"{retail.get('long', 0)}% / {retail.get('short', 0)}%",
            'COT': cot.get('bias', 'N/A').upper(),
            'Segnale': signal_text
        })
    
    st.dataframe(pd.DataFrame(summary), use_container_width=True, hide_index=True)
    
    # Footer
    st.markdown("---")
    st.caption(f"⚠️ Disclaimer: Solo a scopo educativo. Ultimo aggiornamento: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

except Exception as e:
    st.error(f"❌ Errore: {str(e)}")
    st.info("🔄 Ricarica la pagina")
