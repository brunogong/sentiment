from data.technical import get_ohlc
import streamlit as st

def get_atr(symbol, interval="1h", period=14):
    df = get_ohlc(symbol, interval, outputsize=period * 3)

    # Se il DF è vuoto → ATR non calcolabile
    if df.empty:
        st.warning(f"⚠️ ATR non disponibile per {symbol}. Uso ATR=0.")
        return 0.0

    try:
        df["H-L"] = df["high"] - df["low"]
        df["H-PC"] = abs(df["high"] - df["close"].shift(1))
        df["L-PC"] = abs(df["low"] - df["close"].shift(1))

        tr = df[["H-L", "H-PC", "L-PC"]].max(axis=1)
        atr = tr.rolling(period).mean().iloc[-1]

        return float(atr)

    except Exception as e:
        st.warning(f"⚠️ Errore calcolo ATR per {symbol}: {e}. Uso ATR=0.")
        return 0.0
