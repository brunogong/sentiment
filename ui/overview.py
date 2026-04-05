import streamlit as st
import pandas as pd


def color_score(val):
    if val >= 65:
        return "background-color: #0f5132; color: white;"   # verde
    elif val <= 35:
        return "background-color: #842029; color: white;"   # rosso
    return "background-color: #343a40; color: white;"       # neutro


def color_bias(val):
    if val == "bullish":
        return "background-color: #0f5132; color: white;"
    elif val == "bearish":
        return "background-color: #842029; color: white;"
    return "background-color: #343a40; color: white;"


def render_market_overview(signals):
    st.subheader("🌍 Market Overview — Heatmap AI")

    rows = []
    for s in signals:
        rows.append({
            "Pair": s["pair"],
            "Signal": s["action"],
            "Score": s["score"],
            "Trend": s["trend"],
            "Momentum": s["momentum"],
            "COT Bias": s["cot_bias"],
            "COT Sentiment": s["cot_sentiment"],
            "Retail Long %": s["retail"]["long"],
            "RSI 1H": s["rsi"]["rsi_1h"],
            "RSI 4H": s["rsi"]["rsi_4h"],
            "ATR": s["atr"],
        })

    df = pd.DataFrame(rows)

    styled = df.style.applymap(color_score, subset=["Score"]) \
                     .applymap(color_bias, subset=["Trend", "Momentum", "COT Bias"])

    st.dataframe(styled, use_container_width=True)
