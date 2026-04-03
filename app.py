import streamlit as st

from data.cot import get_cot
from data.retail import get_retail_sentiment
from data.technical import get_rsi_multi_tf
from data.volatility import calc_atr

from logic.signals import generate_signal
from ui.dashboard import render_signal_card
from ui.styles import load_styles

def main():
    load_styles()

    st.title("📊 Forex Sentinel PRO — Versione Istituzionale")

    pairs = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"]

    retail = get_retail_sentiment()

    thresholds = {
        "retail_long": 70,
        "retail_short": 70,
        "rsi_overbought": 70,
        "rsi_oversold": 30
    }

    for pair in pairs:
        cot = get_cot(pair)
        rsi = get_rsi_multi_tf(pair)
        atr = 1.0  # placeholder

        signal = generate_signal(pair, cot, retail[pair], rsi, atr, thresholds)
        render_signal_card(signal)

if __name__ == "__main__":
    main()
