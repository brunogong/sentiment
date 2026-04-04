import streamlit as st

from data.cot import get_cot
from data.retail import myfxbook_login, get_retail_sentiment
from data.technical import get_ohlc, get_rsi_multi_tf_from_df
from data.volatility import get_atr_from_df
from utils.mapping import TWELVEDATA_MAPPING

from logic.signals import generate_signal
from ui.dashboard import render_signal_card
from ui.styles import load_styles


def main():
    load_styles()

    st.title("📊 Forex Sentinel PRO — Dati Reali (Versione Ottimizzata + AI)")

    # --- LOGIN MYFXBOOK ---
    email = st.secrets["myfxbook_email"]
    password = st.secrets["myfxbook_password"]

    session = myfxbook_login(email, password)
    retail = get_retail_sentiment(session)

    # --- COPPIE ANALIZZATE ---
    pairs = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"]

    # --- FIX: se MyFxBook non restituisce una coppia ---
    for pair in pairs:
        if pair not in retail:
            st.warning(f"⚠️ MyFxBook non ha dati per {pair}. Uso valori neutri.")
            retail[pair] = {"long": 50, "short": 50}

    # --- SOGLIE ---
    thresholds = {
        "retail_long": 70,
        "retail_short": 70,
        "rsi_overbought": 70,
        "rsi_oversold": 30
    }

    # --- CICLO PRINCIPALE ---
    for pair in pairs:

        # 1) COT reale
        cot = get_cot(pair)

        # 2) OHLC (1 sola chiamata Finnhub/TwelveData)
        symbol = TWELVEDATA_MAPPING[pair]
        df = get_ohlc(symbol, "60")  # 60 = 1H

        # 3) RSI multi‑TF locale
        rsi = get_rsi_multi_tf_from_df(df)

        # 4) ATR locale
        atr = get_atr_from_df(df)

        # 5) Generazione segnale AI-driven
        signal = generate_signal(pair, cot, retail[pair], rsi, atr, df)

        # 6) Rendering UI
        render_signal_card(signal)


if __name__ == "__main__":
    main()
