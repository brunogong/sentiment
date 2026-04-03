import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
import time
import plotly.graph_objects as go

# Configurazione pagina
st.set_page_config(
    page_title="Forex Sentinel Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS solo per colori di base (nessun HTML complesso)
st.markdown("""
<style>
    /* Solo colori di base - niente HTML personalizzato */
    .stApp {
        background: #0a0e27;
    }
    section[data-testid="stSidebar"] {
        background: #13183a;
    }
    .stMarkdown, .stText, .stDataFrame {
        color: #e2e8f0 !important;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #a5b4fc !important;
    }
    .st-bb {
        color: #cbd5e1 !important;
    }
</style>
""", unsafe_allow_html=True)

# Header con st.markdown semplice
st.markdown("# 📊 Forex Sentinel Pro")
st.markdown("### Tripla Conferma: RSI + COT + Sentiment Retail")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.markdown("## ⚙️ Configurazione")
    
    retail_long_threshold = st.slider("📈 Retail LONG > soglia (per SELL)", 60, 85, 70)
    retail_short_threshold = st.slider("📉 Retail SHORT > soglia (per BUY)", 60, 85, 70)
    st.markdown("---")
    rsi_overbought = st.slider("🔥 RSI > soglia (Ipercomprato)", 60, 85, 70)
    rsi_oversold = st.slider("💚 RSI < soglia (Ipervenduto)", 15, 40, 30)
    rsi_period = st.selectbox("📊 Periodo RSI", [7, 14, 21, 30], index=1)
    st.markdown("---")
    
    if st.button("🔄 Aggiorna Dati", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 🎯 Strategia Corrente")
    st.markdown(f"""
    **SELL (Tripla):**
    - Retail LONG > {retail_long_threshold}%
    - COT Bearish
    - RSI > {rsi_overbought}
    
    **BUY (Tripla):**
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
            price = round(hist['Close'].iloc[-1], 2 if pair == 'XAUUSD' else 5) if not hist.empty else None
            
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
            
            data[pair] = {'price': price, 'rsi': current_rsi, 'pivot': pivot, 'r1': r1, 's1': s1}
        except:
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
        
        # Check SELL
        sell_conditions = []
        if retail['long'] > thresholds['retail_long']:
            sell_conditions.append("Retail LONG")
        if cot['bias'] == 'bearish':
            sell_conditions.append("COT Bearish")
        if tech['rsi'] > thresholds['rsi_overbought']:
            sell_conditions.append("RSI Overbought")
        
        # Check BUY
        buy_conditions = []
        if retail['short'] > thresholds['retail_short']:
            buy_conditions.append("Retail SHORT")
        if cot['bias'] == 'bullish':
            buy_conditions.append("COT Bullish")
        if tech['rsi'] < thresholds['rsi_oversold']:
            buy_conditions.append("RSI Oversold")
        
        action = None
        conditions = []
        score = 0
        
        if len(sell_conditions) >= 2:
            action = 'SELL'
            conditions = sell_conditions
            score = len(sell_conditions)
        elif len(buy_conditions) >= 2:
            action = 'BUY'
            conditions = buy_conditions
            score = len(buy_conditions)
        
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
                'conditions': ' + '.join(conditions),
                'price': tech['price']
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
    
    # Metriche con st.metric nativo
    col1, col2, col3, col4 = st.columns(4)
    
    triple = len([s for s in signals if s['score'] >= 3])
    double = len([s for s in signals if 2 <= s['score'] < 3])
    buys = len([s for s in signals if s['action'] == 'BUY'])
    sells = len([s for s in signals if s['action'] == 'SELL'])
    
    with col1:
        st.metric("🔴🔴🔴 Triple Conferma", triple)
    with col2:
        st.metric("🟡🟡 Doppia Conferma", double)
    with col3:
        st.metric("📊 Segnali Totali", len(signals))
    with col4:
        st.metric("🟢 BUY", buys, delta=f"🔴 SELL {sells}")
    
    st.markdown("---")
    st.markdown("## 🎯 Segnali di Trading")
    
    if signals:
        for i, signal in enumerate(signals):
            # Usiamo expander per ogni segnale (più pulito)
            with st.expander(f"{'🔴' if signal['action'] == 'SELL' else '🟢'} {signal['pair']} - {signal['action']} - Score: {signal['score']}/3", expanded=i==0):
                
                # Colonne per info principali
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown(f"**🏦 COT:** {signal['cot_bias'].upper()}")
                with c2:
                    st.markdown(f"**👥 Retail:** LONG {signal['retail_long']}% / SHORT {signal['retail_short']}%")
                with c3:
                    rsi_color = "🔴" if signal['rsi'] > rsi_overbought else "🟢" if signal['rsi'] < rsi_oversold else "⚪"
                    st.markdown(f"**📊 RSI ({rsi_period}):** {rsi_color} {signal['rsi']}")
                
                st.markdown(f"**✅ Condizioni:** {signal['conditions']}")
                st.markdown(f"**🎯 Confidenza:** {signal['confidence']}")
                
                st.markdown("---")
                
                # Dettagli trade
                col_entry, col_tp, col_sl, col_rr = st.columns(4)
                with col_entry:
                    st.metric("Entry", format_price(signal['pair'], signal['entry']))
                with col_tp:
                    st.metric("Take Profit", format_price(signal['pair'], signal['tp']), delta="TP")
                with col_sl:
                    st.metric("Stop Loss", format_price(signal['pair'], signal['sl']), delta="SL", delta_color="inverse")
                with col_rr:
                    st.metric("R:R Ratio", f"1:{signal['rr']}")
    else:
        st.info("ℹ️ Nessun segnale con le soglie attuali. Prova ad abbassare le soglie.")
    
    st.markdown("---")
    st.markdown("## 📊 Tabella Riassuntiva")
    
    # Tabella con pandas styling
    summary_data = []
    for pair in forex_pairs:
        cot = cot_data.get(pair, {})
        retail = retail_data.get(pair, {})
        tech = tech_data.get(pair, {})
        
        rsi = tech.get('rsi', 50)
        
        if retail.get('long', 0) > retail_long_threshold and cot.get('bias') == 'bearish' and rsi > rsi_overbought:
            signal_text = "🔴 SELL (Tripla)"
        elif retail.get('long', 0) > retail_long_threshold and cot.get('bias') == 'bearish':
            signal_text = "🟡 SELL (Doppia)"
        elif retail.get('short', 0) > retail_short_threshold and cot.get('bias') == 'bullish' and rsi < rsi_oversold:
            signal_text = "🟢 BUY (Tripla)"
        elif retail.get('short', 0) > retail_short_threshold and cot.get('bias') == 'bullish':
            signal_text = "🟡 BUY (Doppia)"
        else:
            signal_text = "⚪ ATTESA"
        
        price = tech.get('price')
        price_str = format_price(pair, price)
        
        summary_data.append({
            'Coppia': pair,
            'Prezzo': price_str,
            f'RSI({rsi_period})': rsi,
            'Retail L/S': f"{retail.get('long', 0)}% / {retail.get('short', 0)}%",
            'COT': cot.get('bias', 'N/A').upper(),
            'Segnale': signal_text
        })
    
    df = pd.DataFrame(summary_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Grafico RSI per le principali coppie
    st.markdown("---")
    st.markdown("## 📈 RSI - Situazione Attuale")
    
    # Crea grafico a barre RSI
    rsi_data = []
    pairs_for_chart = [p for p in forex_pairs if p in tech_data]
    for pair in pairs_for_chart:
        rsi_data.append({
            'Coppia': pair,
            'RSI': tech_data[pair]['rsi'],
            'Soglia OB': rsi_overbought,
            'Soglia OS': rsi_oversold
        })
    
    rsi_df = pd.DataFrame(rsi_data)
    
    fig = go.Figure()
    
    # Aggiungi barre RSI
    fig.add_trace(go.Bar(
        x=rsi_df['Coppia'],
        y=rsi_df['RSI'],
        name='RSI',
        marker_color=['#ef4444' if x > rsi_overbought else '#10b981' if x < rsi_oversold else '#667eea' for x in rsi_df['RSI']],
        text=rsi_df['RSI'],
        textposition='auto',
        textfont=dict(color='white')
    ))
    
    # Linee soglie
    fig.add_hline(y=rsi_overbought, line_dash="dash", line_color="#ef4444", annotation_text=f"Overbought ({rsi_overbought})")
    fig.add_hline(y=rsi_oversold, line_dash="dash", line_color="#10b981", annotation_text=f"Oversold ({rsi_oversold})")
    fig.add_hline(y=50, line_dash="dot", line_color="#64748b")
    
    fig.update_layout(
        title="RSI per Coppia",
        yaxis_title="RSI",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#e2e8f0',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.caption(f"⚠️ Disclaimer: Solo a scopo educativo. I segnali sono generati automaticamente.")
    st.caption(f"🔄 Ultimo aggiornamento: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

except Exception as e:
    st.error(f"❌ Errore: {str(e)}")
    st.info("🔄 Ricarica la pagina")
