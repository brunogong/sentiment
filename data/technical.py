import requests
import pandas as pd
import streamlit as st

API_KEY = st.secrets["twelvedata_api_key"]

def get_ohlc(symbol, interval="1h", outputsize=500):
    url = (
        f"https://api.twelvedata.com/time_series"
        f"?symbol={symbol}&interval={interval}&outputsize={outputsize}&apikey={API_KEY}"
    )

    try:
        data = requests.get(url, timeout=5).json()

        if "values" not in data:
            st.warning(f"⚠️ Nessun OHLC per {symbol}.")
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

    except Exception as e:
        st.warning(f"⚠️ Errore OHLC {symbol}: {e}")
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
