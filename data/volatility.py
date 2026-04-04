import streamlit as st

def get_atr_from_df(df, period=14):
    if df.empty:
        st.warning("⚠️ ATR non disponibile. Uso 0.")
        return 0.0

    df["H-L"] = df["high"] - df["low"]
    df["H-PC"] = abs(df["high"] - df["close"].shift(1))
    df["L-PC"] = abs(df["low"] - df["close"].shift(1))

    tr = df[["H-L", "H-PC", "L-PC"]].max(axis=1)
    atr = tr.rolling(period).mean().iloc[-1]

    return float(atr)
