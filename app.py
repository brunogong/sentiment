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

# CSS minimale ma efficace
st.markdown("""
<style>
    /* Sfondo */
    .stApp {
        background: #0a0e27;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #0f1233;
    }
    
    /* Testi sidebar */
    section[data-testid="stSidebar"] .stMarkdown {
        color: #ffffff !important;
    }
    
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {
        color: #a5b4fc !important;
    }
    
    /* Bottoni - TESTI BIANCHI */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        font-weight: bold !important;
        font-size: 16px !important;
        border: none;
        border-radius: 10px;
    }
    
    /* Metriche */
    div[data-testid="stMetric"] {
        background: #1a1f3e;
        border-radius: 15px;
        padding: 15px;
    }
    
    div[data-testid="stMetric"] label {
        color: #a5b4fc !important;
    }
    
    div[data-testid="stMetric"] .stMetricValue {
        color: white !important;
        font-size: 1.8rem !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: #1a1f3e;
        border-radius: 12px;
        color: white !important;
        font-weight: bold;
    }
    
    /* Tabella */
    .stDataFrame {
        background: #1a1f3e;
        border-radius: 12px;
    }
    
    .stDataFrame thead th {
        background: #667eea;
        color: white !important;
    }
    
    .stDataFrame tbody td {
        color: white !important;
    }
    
    /* Testi generali */
    h1, h2, h3, h4, h5, h6 {
        color: white !important;
    }
    
    .stMarkdown p {
        color: #e2e8f0 !important;
    }
    
    /* Info box */
    .stAlert {
        background: #1a1f3e;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Header
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
    rsi_period = st.selectbox("📈 Periodo RSI", [7, 14, 21, 30], index=1)
    st.markdown("---")
    
    if st.button("🔄 Aggiorna Dati", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 🎯 Strategia")
    st.markdown(f"""
    **🔴 SELL:** Retail LONG > {retail_long_threshold}% + COT Bearish + RSI > {rsi_overbought}
    
    **🟢 BUY:** Retail SHORT > {retail_short_threshold}% + COT Bullish + RSI < {rsi_oversold}
    """)

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
    """Genera segnali - OGNI segnale viene mostrato individualmente"""
    signals = []
    
    for pair in cot_data:
        if pair not in retail_data or pair not in tech_data:
            continue
        
        cot = cot_data[pair]
        retail = retail_data[pair]
        tech = tech_data[pair]
        
        # Verifica condizioni SELL
        sell_conditions = []
        if retail['long'] > thresholds['retail_long']:
            sell_conditions.append("Retail LONG")
        if cot['bias'] == 'bearish':
            sell_conditions.append("COT Bearish")
        if tech['rsi'] > thresholds['rsi_overbought']:
            sell_conditions.append("RSI Overbought")
        
        # Verifica condizioni BUY
        buy_conditions = []
        if retail['short'] > thresholds['retail_short']:
            buy_conditions.append("Retail SHORT")
        if cot['bias'] == 'bullish':
            buy_conditions.append("COT Bullish")
        if tech['rsi'] < thresholds['rsi_oversold']:
            buy_conditions.append("RSI Oversold")
        
        # Aggiungi segnale SELL se almeno 2 condizioni
        if len(sell_conditions) >= 2:
            entry = tech['r1'] if tech['r1'] else tech['price']
            tp = tech['pivot'] if tech['pivot'] else (entry * 0.995 if entry else None)
            sl = entry * 1.005 if entry else None
            rr = round(abs((tp - entry) / (entry - sl)), 2) if entry and sl and entry != sl else 0
            
            signals.append({
                'pair': pair,
                'action': 'SELL',
                'score': len(sell_conditions),
                'conditions': ' + '.join(sell_conditions),
                'entry': entry,
                'tp': tp,
                'sl': sl,
                'rr': rr,
                'retail_long': retail['long'],
                'retail_short': retail['short'],
                'cot_bias': cot['bias'],
                'rsi': tech['rsi']
            })
        
        # Aggiungi segnale BUY se almeno 2 condizioni
        if len(buy_conditions) >= 2:
            entry = tech['s1'] if tech['s1'] else tech['price']
            tp = tech['pivot'] if tech['pivot'] else (entry * 1.005 if entry else None)
            sl = entry * 0.995 if entry else None
            rr = round(abs((tp - entry) / (entry - sl)), 2) if entry and sl and entry != sl else 0
            
            signals.append({
                'pair': pair,
                'action': 'BUY',
                'score': len(buy_conditions),
                'conditions': ' + '.join(buy_conditions),
                'entry': entry,
                'tp': tp,
                'sl': sl,
                'rr': rr,
                'retail_long': retail['long'],
                'retail_short': retail['short'],
                'cot_bias': cot['bias'],
                'rsi': tech['rsi']
            })
    
    # Ordina per score
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
    
    # Metriche - mostra i conti corretti
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
    st.markdown(f"## 🎯 Segnali di Trading ({len(signals)} trovati)")
    
    if signals:
        for i, signal in enumerate(signals):
            # Icone e colori
            if signal['action'] == 'BUY':
                icon = "🟢"
                arrow = "↑"
                action_color = "#10b981"
            else:
                icon = "🔴"
                arrow = "↓"
                action_color = "#ef4444"
            
            # Determina livello confidenza
            if signal['score'] >= 3:
                confidence = "🔴🔴🔴 ALTA"
            else:
                confidence = "🟡🟡 MEDIA"
            
            with st.expander(f"{icon} {signal['pair']} - {signal['action']} {arrow} | Score: {signal['score']}/3 | {confidence}", expanded=i==0):
                
                # 3 colonne info
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.write("**🏦 COT**")
                    st.write(f"**{signal['cot_bias'].upper()}**")
                with col_b:
                    st.write("**👥 Retail**")
                    st.write(f"LONG: {signal['retail_long']}% / SHORT: {signal['retail_short']}%")
                with col_c:
                    st.write("**📊 RSI**")
                    st.write(f"{signal['rsi']}")
                
                st.write("---")
                st.write(f"**✅ Condizioni:** {signal['conditions']}")
                
                # Dettagli trade
                col_e, col_f, col_g, col_h = st.columns(4)
                with col_e:
                    st.metric("Entry", format_price(signal['pair'], signal['entry']))
                with col_f:
                    st.metric("Take Profit", format_price(signal['pair'], signal['tp']))
                with col_g:
                    st.metric("Stop Loss", format_price(signal['pair'], signal['sl']))
                with col_h:
                    st.metric("R:R Ratio", f"1:{signal['rr']}")
    else:
        st.info("ℹ️ Nessun segnale con le soglie attuali. Prova ad abbassare le soglie.")
    
    st.markdown("---")
    st.markdown("## 📊 Tabella Riassuntiva")
    
    # Tabella riassuntiva - mostra TUTTE le coppie
    summary_data = []
    for pair in forex_pairs:
        # Cerca se c'è un segnale per questa coppia
        signal = next((s for s in signals if s['pair'] == pair), None)
        
        cot = cot_data.get(pair, {})
        retail = retail_data.get(pair, {})
        tech = tech_data.get(pair, {})
        
        rsi = tech.get('rsi', 50)
        
        if signal:
            if signal['action'] == 'SELL':
                signal_text = f"🔴 SELL (Score {signal['score']}/3)"
            else:
                signal_text = f"🟢 BUY (Score {signal['score']}/3)"
        else:
            # Verifica se ci sono condizioni parziali
            sell_cond = (retail.get('long', 0) > retail_long_threshold) + (cot.get('bias') == 'bearish') + (rsi > rsi_overbought)
            buy_cond = (retail.get('short', 0) > retail_short_threshold) + (cot.get('bias') == 'bullish') + (rsi < rsi_oversold)
            
            if sell_cond >= 2:
                signal_text = "🟡 SELL (parziale)"
            elif buy_cond >= 2:
                signal_text = "🟡 BUY (parziale)"
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
    
    rsi_chart_data = []
    for pair in forex_pairs:
        if pair in tech_data:
            rsi_chart_data.append({
                'Coppia': pair,
                'RSI': tech_data[pair]['rsi']
            })
    
    rsi_df = pd.DataFrame(rsi_chart_data)
    
    fig = go.Figure()
    
    # Colori in base al valore RSI
    bar_colors = []
    for rsi_val in rsi_df['RSI']:
        if rsi_val > rsi_overbought:
            bar_colors.append('#ef4444')
        elif rsi_val < rsi_oversold:
            bar_colors.append('#10b981')
        else:
            bar_colors.append('#667eea')
    
    fig.add_trace(go.Bar(
        x=rsi_df['Coppia'],
        y=rsi_df['RSI'],
        marker_color=bar_colors,
        text=rsi_df['RSI'],
        textposition='auto',
        textfont=dict(color='white')
    ))
    
    fig.add_hline(y=rsi_overbought, line_dash="dash", line_color="#ef4444", 
                  annotation_text=f"Overbought ({rsi_overbought})")
    fig.add_hline(y=rsi_oversold, line_dash="dash", line_color="#10b981", 
                  annotation_text=f"Oversold ({rsi_oversold})")
    fig.add_hline(y=50, line_dash="dot", line_color="#64748b")
    
    fig.update_layout(
        title="RSI per Coppia",
        yaxis_title="RSI",
        yaxis=dict(range=[0, 100]),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.caption(f"⚠️ Disclaimer: Solo a scopo educativo. Ultimo aggiornamento: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

except Exception as e:
    st.error(f"❌ Errore: {str(e)}")
    st.info("🔄 Ricarica la pagina")
