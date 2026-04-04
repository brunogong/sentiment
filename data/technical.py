import requests
import pandas as pd
import streamlit as st

API_KEY = st.secrets["twelvedata_api_key"]

def _safe_twelvedata_get(url: str):
    try:
        resp = requests.get(url, timeout=5)
        data = resp.json()

        # Se TwelveData risponde con errore
        if "status" in data and data["status"] == "error":
            st.warning(f"⚠️ TwelveData error: {data.get('message', 'Unknown error')}")
            return None

        return data

    except Exception as e:
        st.warning(f"⚠️ Errore richiesta TwelveData: {e}")
        return None


def get_ohlc(symbol, interval="1h", outputsize=200):
    url = (
        f"https://api.twelvedata.com/time_series"
        f"?symbol={symbol}&interval={interval}&outputsize={outputsize}&apikey={API_KEY}"
    )

    data = _safe_twelvedata_get(url)

    if not data or "values" not in data:
        st.warning(f"⚠️ Nessun dato OHLC per {symbol} ({interval}). Ritorno DF vuoto.")
        return pd.DataFrame()

    df = pd.DataFrame(data["values"])
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.sort_values("datetime")

    df = df.astype({
        "open": float,
        "high": float,
        "low": float,
        "close": float
    })

    return df


def get_rsi(symbol, interval="1h", period=14):
    url = (
        f"https://api.twelvedata.com/rsi"
        f"?symbol={symbol}&interval={interval}&time_period={period}&apikey={API_KEY}"
    )

    data = _safe_twelvedata_get(url)

    if not data or "values" not in data:
        st.warning(f"⚠️ Nessun RSI per {symbol} ({interval}). Uso RSI=50.")
        return 50.0

    try:
        return float(data["values"][0]["rsi"])
    except:
        st.warning(f"⚠️ Errore parsing RSI per {symbol} ({interval}). Uso RSI=50.")
        return 50.0


def get_rsi_multi_tf(symbol):
    return {
        "rsi_1h": get_rsi(symbol, "1h"),
        "rsi_4h": get_rsi(symbol, "4h"),
        "rsi_1d": get_rsi(symbol, "1day")
    }
