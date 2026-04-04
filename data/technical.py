import requests
import pandas as pd
import streamlit as st

API_KEY = st.secrets["finnhub_api_key"]

BASE = "https://finnhub.io/api/v1"


def get_ohlc(symbol, resolution="60", candles=500):
    """
    resolution:
        1 = 1m
        5 = 5m
        15 = 15m
        30 = 30m
        60 = 1h
        D = 1d
    """
    url = f"{BASE}/forex/candle?symbol={symbol}&resolution={resolution}&count={candles}&token={API_KEY}"

    try:
        data = requests.get(url, timeout=5).json()

        if data.get("s") != "ok":
            st.warning(f"⚠️ Nessun OHLC Finnhub per {symbol}.")
            return pd.DataFrame()

        df = pd.DataFrame({
            "datetime": pd.to_datetime(data["t"], unit="s"),
            "open": data["o"],
            "high": data["h"],
            "low": data["l"],
            "close": data["c"]
        })

        return df

    except Exception as e:
        st.warning(f"⚠️ Errore OHLC Finnhub {symbol}: {e}")
        return pd.DataFrame()


def calc_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def get_rsi_multi_tf_from_df(df):
    if df.empty:
        return {"rsi_1h": 50, "rsi_4h": 50, "rsi_1d": 50}

    rsi_1h = calc_rsi(df["close"], 14).iloc[-1]

    df_4h = df.iloc[::4]
    rsi_4h = calc_rsi(df_4h["close"], 14).iloc[-1]

    df_1d = df.iloc[::24]
    rsi_1d = calc_rsi(df_1d["close"], 14).iloc[-1]

    return {
        "rsi_1h": round(rsi_1h, 2),
        "rsi_4h": round(rsi_4h, 2),
        "rsi_1d": round(rsi_1d, 2)
    }
