import requests
import pandas as pd
import streamlit as st

API_KEY = st.secrets["eodhd_api_key"]

# Mappa simboli Forex per EODHD
EODHD_SYMBOLS = {
    "EURUSD": "EURUSD.FOREX",
    "GBPUSD": "GBPUSD.FOREX",
    "USDJPY": "USDJPY.FOREX",
    "XAUUSD": "XAUUSD.FOREX",
}


# ---------------------------------------------------------
# DEBUG EODHD
# ---------------------------------------------------------
def debug_eodhd():
    url = (
        f"https://eodhd.com/api/intraday/EURUSD.FOREX"
        f"?interval=1m&api_token={API_KEY}&fmt=json"
    )

    st.subheader("🔍 DEBUG EODHD API")
    st.write("URL chiamato:", url)

    try:
        r = requests.get(url, timeout=10)
        st.write("Status code:", r.status_code)
        st.code(r.text[:500])
    except Exception as e:
        st.error(f"Errore EODHD: {e}")


# ---------------------------------------------------------
# OHLC MULTI-TIMEFRAME
# ---------------------------------------------------------
def fetch_ohlc(pair, interval="1m"):
    symbol = EODHD_SYMBOLS[pair]

    url = (
        f"https://eodhd.com/api/intraday/{symbol}"
        f"?interval={interval}&api_token={API_KEY}&fmt=json"
    )

    try:
        r = requests.get(url, timeout=10)
        data = r.json()

        if not isinstance(data, list) or len(data) == 0:
            return pd.DataFrame()

        df = pd.DataFrame(data)
        df["datetime"] = pd.to_datetime(df["datetime"])
        df = df.rename(columns={
            "open": "open",
            "high": "high",
            "low": "low",
            "close": "close"
        })

        return df[["datetime", "open", "high", "low", "close"]]

    except Exception as e:
        st.error(f"Errore OHLC {pair}: {e}")
        return pd.DataFrame()


def get_ohlc(pair):
    return fetch_ohlc(pair, interval="1m")


# ---------------------------------------------------------
# RSI
# ---------------------------------------------------------
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
    rsi_4h = calc_rsi(df["close"].iloc[::240], 14).iloc[-1]
    rsi_1d = calc_rsi(df["close"].iloc[::1440], 14).iloc[-1]

    return {
        "rsi_1h": round(rsi_1h, 2),
        "rsi_4h": round(rsi_4h, 2),
        "rsi_1d": round(rsi_1d, 2)
    }
