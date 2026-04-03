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

# CSS migliorato per contrasto e grafica
st.markdown("""
<style>
    /* Sfondo principale */
    .stApp {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 100%);
    }
    
    /* Sidebar migliorata */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0a1a 0%, #12122e 100%);
        border-right: 1px solid rgba(102, 126, 234, 0.2);
    }
    
    section[data-testid="stSidebar"] .stMarkdown {
        color: #e2e8f0 !important;
    }
    
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {
        color: #a5b4fc !important;
        font-weight: 600;
    }
    
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] li {
        color: #cbd5e1 !important;
    }
    
    /* Widget sidebar */
    section[data-testid="stSidebar"] .stSlider label,
    section[data-testid="stSidebar"] .stSelectbox label {
        color: #a5b4fc !important;
        font-weight: 500;
    }
    
    /* Bottoni */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Metriche */
    div[data-testid="stMetric"] {
        background: rgba(26, 31, 62, 0.8);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 15px;
        border: 1px solid rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
    }
    
    div[data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        border-color: rgba(102, 126, 234, 0.6);
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }
    
    div[data-testid="stMetric"] label {
        color: #a5b4fc !important;
        font-weight: 500;
    }
    
    div[data-testid="stMetric"] .stMetricValue {
        color: white !important;
        font-size: 2rem !important;
        font-weight: 700;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, rgba(26, 31, 62, 0.9), rgba(19, 24, 58, 0.9));
        border-radius: 12px;
        border: 1px solid rgba(102, 126, 234, 0.3);
        color: white !important;
        font-weight: 600;
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2));
        border-color: rgba(102, 126, 234, 0.6);
    }
    
    /* Dataframe */
    .stDataFrame {
        background: rgba(26, 31, 62, 0.6);
        border-radius: 12px;
        border: 1px solid rgba(102, 126, 234, 0.2);
    }
    
    .stDataFrame thead th {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white !important;
        font-weight: 600;
        padding: 12px;
    }
    
    .stDataFrame tbody td {
        color: #e2e8f0 !important;
        padding: 10px;
    }
    
    .stDataFrame tbody tr:hover {
        background: rgba(102, 126, 234, 0.1);
    }
    
    /* Testi generali */
    h1, h2, h3, h4, h5, h6 {
        background: linear-gradient(135deg, #fff 0%, #a5b4fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
    }
    
    .stMarkdown p, .stMarkdown li {
        color: #e2e8f0 !important;
    }
    
    /* Info box */
    .stAlert {
        background: rgba(26, 31, 62, 0.9);
        border-left: 4px solid #667eea;
        color: #e2e8f0;
    }
    
    /* Spinner */
    .stSpinner {
        color: #667eea;
    }
    
    /* Divisori */
    hr {
        border-color: rgba(102, 126, 234, 0.3);
        margin: 1.5rem 0;
    }
    
    /* Card per i dettagli dentro expander */
    .trade-details {
        background: rgba(0,0,0,0.2);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
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
    
    st.markdown("### 🎯 Soglie Retail")
    retail_long_threshold = st.slider("📈 Retail LONG > soglia (per SELL)", 60, 85, 70)
    retail_short_threshold = st.slider("📉 Retail SHORT > soglia (per BUY)", 60, 85, 70)
    st.markdown("---")
    
    st.markdown("### 📊 Soglie RSI")
    rsi_overbought = st.slider("🔥 RSI > soglia (Ipercomprato)", 60, 85, 70)
    rsi_oversold = st.slider("💚 RSI < soglia (Ipervenduto)", 15, 40, 30)
    rsi_period = st.selectbox("📈 Periodo RSI", [7, 14, 21, 30], index=1)
    st.markdown("---")
    
    if st.button("🔄 Aggiorna Dati", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 🎯 Strategia Corrente")
    st.markdown(f"""
    **🔴 SELL (Tripla):**
    - Retail LONG > {retail_long_threshold}%
    - COT Bearish
    - RSI > {rsi_overbought}
    
    **🟢 BUY (Tripla):**
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
    
    # Metriche migliorate
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
            # Icona e colore in base all'azione
            icon = "🔴" if signal['action'] == 'SELL' else "🟢"
            color = "#ef4444" if signal['action'] == 'SELL' else "#10b981"
            
            with st.expander(f"{icon} {signal['pair']} - {signal['action']} | Score: {signal['score']}/3 | Confidenza: {signal['confidence']}", expanded=i==0):
                
                # Info principali in 3 colonne
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown(f"**🏦 COT**")
                    st.markdown(f":blue[{signal['cot_bias'].upper()}]")
                with c2:
                    st.markdown(f"**👥 Retail**")
                    st.markdown(f"LONG: :green[{signal['retail_long']}%] / SHORT: :red[{signal['retail_short']}%]")
                with c3:
                    st.markdown(f"**📊 RSI ({rsi_period})**")
                    if signal['rsi'] > rsi_overbought:
                        st.markdown(f":red[🔥 {signal['rsi']} (Overbought)]")
                    elif signal['rsi'] < rsi_oversold:
                        st.markdown(f":green[💚 {signal['rsi']} (Oversold)]")
                    else:
                        st.markdown(f":white[{signal['rsi']} (Neutrale)]")
                
                st.markdown("---")
                
                # Condizioni
                st.markdown(f"**✅ Condizioni verificate:** :violet[{signal['conditions']}]")
                
                # Dettagli trade in 4 colonne
                col_entry, col_tp, col_sl, col_rr = st.columns(4)
                with col_entry:
                    st.metric("📌 Entry", format_price(signal['pair'], signal['entry']))
                with col_tp:
                    st.metric("🎯 Take Profit", format_price(signal['pair'], signal['tp']), delta="TP")
                with col_sl:
                    st.metric("🛑 Stop Loss", format_price(signal['pair'], signal['sl']), delta="SL", delta_color="inverse")
                with col_rr:
                    st.metric("📈 R:R Ratio", f"1:{signal['rr']}")
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
    
    # Grafico RSI
    st.markdown("---")
    st.markdown("## 📈 RSI - Situazione Attuale")
    
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
    
    # Colori in base alla condizione RSI
    colors = []
    for rsi_val in rsi_df['RSI']:
        if rsi_val > rsi_overbought:
            colors.append('#ef4444')
        elif rsi_val < rsi_oversold:
            colors.append('#10b981')
        else:
            colors.append('#667eea')
    
    fig.add_trace(go.Bar(
        x=rsi_df['Coppia'],
        y=rsi_df['RSI'],
        name='RSI',
        marker_color=colors,
        text=rsi_df['RSI'],
        textposition='auto',
        textfont=dict(color='white', size=12),
        hovertemplate='<b>%{x}</b><br>RSI: %{y}<extra></extra>'
    ))
    
    fig.add_hline(y=rsi_overbought, line_dash="dash", line_color="#ef4444", 
                  annotation_text=f"Overbought ({rsi_overbought})", annotation_font_color="#ef4444")
    fig.add_hline(y=rsi_oversold, line_dash="dash", line_color="#10b981", 
                  annotation_text=f"Oversold ({rsi_oversold})", annotation_font_color="#10b981")
    fig.add_hline(y=50, line_dash="dot", line_color="#64748b")
    
    fig.update_layout(
        title=dict(text="RSI per Coppia", font=dict(color='white', size=20)),
        yaxis_title="RSI",
        yaxis=dict(range=[0, 100], gridcolor='rgba(255,255,255,0.1)'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#e2e8f0',
        height=450,
        hovermode='closest',
        bargap=0.3
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, rgba(102,126,234,0.1), rgba(118,75,162,0.1)); border-radius: 15px;'>
        <p style='color: #94a3b8; margin: 0;'>⚠️ Disclaimer: Solo a scopo educativo. I segnali sono generati automaticamente.</p>
        <p style='color: #64748b; margin: 5px 0 0 0; font-size: 12px;'>🔄 Ultimo aggiornamento: {}</p>
    </div>
    """.format(datetime.now().strftime('%d/%m/%Y %H:%M:%S')), unsafe_allow_html=True)

except Exception as e:
    st.error(f"❌ Errore: {str(e)}")
    st.info("🔄 Ricarica la pagina o attendi qualche minuto.")
