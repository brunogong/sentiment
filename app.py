import streamlit as st

from data.cot import get_cot
from data.retail import myfxbook_login, get_retail_sentiment
from data.technical import get_ohlc, get_rsi_multi_tf_from_df
from data.volatility import get_atr_from_df

from logic.signals import generate_signal
from ui.dashboard import render_signal_card
from ui.overview import render_market_overview
from ui.styles import load_styles


def main():
    load_styles()

    st.title("📊 Forex Sentinel PRO — AI Signals (Massive Edition)")

    # --- LOGIN MYFXBOOK ---
    email = st.secrets["myfxbook_email"]
    password = st.secrets["myfxbook_password"]

    session = myfxbook_login(email, password)
    retail = get_retail_sentiment(session)

    pairs = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"]

    # Fallback retail neutro se manca una coppia
    for pair in pairs:
        if pair not in retail:
            st.warning(f"⚠ MyFxBook non ha dati per {pair}. Uso valori neutri.")
            retail[pair] = {"long": 50, "short": 50}

    signals_list = []

    # --- CICLO PRINCIPALE: genera tutti i segnali ---
    for pair in pairs:
        cot = get_cot(pair)
        df = get_ohlc(pair)
        rsi = get_rsi_multi_tf_from_df(df)
        atr = get_atr_from_df(df)

        signal = generate_signal(pair, cot, retail[pair], rsi, atr, df)
        signals_list.append(signal)

    # --- MARKET OVERVIEW (HEATMAP) ---
    render_market_overview(signals_list)

    # --- CARD DETTAGLIATE PER OGNI COPPIA ---
    for signal in signals_list:
        render_signal_card(signal)


if __name__ == "__main__":
    main()
