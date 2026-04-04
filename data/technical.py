import requests
import pandas as pd
import streamlit as st

API_KEY = st.secrets["twelvedata_api_key"]

def _safe_twelvedata_get(url: str):
    try:
        resp = requests.get(url, timeout=5)
        data = resp.json()
        # Debug opzionale:
        # st.write("DEBUG TwelveData:", data)
        return data
    except Exception as e:
        st.warning(f"Errore richiesta TwelveData: {e}")
        return None


def get_ohlc(symbol, interval="1h", outputsize=200):
    """
    Restituisce un DataFrame OHLC da TwelveData.
    Se fallisce, restituisce un DataFrame vuoto.
    """
    url = (
        f"https://api.twelvedata.com/time_series"
        f"?symbol={symbol}&interval={interval}&outputsize={outputsize}&apikey={API_KEY}"
    )
    data = _safe_twelvedata_get(url)
    if not data or "values" not in data:
        st.warning(f"⚠️ Nessun dato OHLC da TwelveData per {symbol} ({interval}).")
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
    """
    Restituisce RSI da TwelveData.
    Se fallisce, restituisce 50 come valore neutro.
    """
    url = (
        f"https://api.twelvedata.com/rsi"
        f"?symbol={symbol}&interval={interval}&time_period={period}&apikey={API_KEY}"
    )
    data = _safe_twelvedata_get(url)
    if not data or "values" not in data:
        st.warning(f"⚠️ Nessun dato RSI da TwelveData per {symbol} ({interval}). Uso RSI=50.")
        return 50.0

    try:
        return float(data["values"][0]["rsi"])
    except Exception as e:
        st.warning(f"⚠️ Errore parsing RSI per {symbol} ({interval}): {e}. Uso RSI=50.")
        return 50.0


def get_rsi_multi_tf(symbol):
    """
    Restituisce un dict con RSI multi-timeframe.
    Usa fallback 50 se qualche TF fallisce.
    """
    return {
        "rsi_1h": get_rsi(symbol, "1h"),
        "rsi_4h": get_rsi(symbol, "4h"),
        "rsi_1d": get_rsi(symbol, "1day")
    }
