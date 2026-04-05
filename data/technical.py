import requests
import pandas as pd
import streamlit as st
from utils.mapping import MASSIVE_SYMBOLS

API_KEY = st.secrets["massive_api_key"]


# ---------------------------------------------------------
# DEBUG MASSIVE — MOSTRA RISPOSTA RAW
# ---------------------------------------------------------
def debug_massive():
    url = (
        f"https://api.massive.app/v1/forex/ohlc?"
        f"symbol=EURUSD&interval=1m&apiKey={API_KEY}"
    )

    st.subheader("🔍 DEBUG Massive API")

    st.write("URL chiamato:", url)

    try:
        r = requests.get(url, timeout=10)
        st.write("Status code:", r.status_code)
        st.write("Raw response (primi 500 caratteri):")
        st.code(r.text[:500])
    except Exception as e:
        st.error(f"Errore durante la chiamata Massive: {e}")


# ---------------------------------------------------------
# MASSIVE OHLC (con caching)
# ---------------------------------------------------------
@st.cache_data(ttl=60)
def load_all_ohlc():
    data = {}

    for pair, symbol in MASSIVE_SYMBOLS.items():

        url = (
            f"https://api.massive.app/v1/forex/ohlc?"
            f"symbol={symbol}&interval=1m&apiKey={API_KEY}"
        )

        try:
            response = requests.get(url, timeout=10)
            raw = response.json()

            if "data" not in raw or not raw["data"]:
                st.warning(f"⚠ Massive non ha restituito OHLC per {pair}.")
                data[pair] = pd.DataFrame()
                continue

            df = pd.DataFrame(raw["data"])
            df["datetime"] = pd.to_datetime(df["timestamp"], unit="s")

            df = df[["datetime", "open", "high", "low", "close"]]
            df = df.sort_values("datetime").reset_index(drop=True)

            data[pair] = df

        except Exception as e:
            st.error(f"❌ Errore Massive per {pair}: {e}")
            data[pair] = pd.DataFrame()

    return data


def get_ohlc(pair):
    all_data = load_all_ohlc()
    return all_data.get(pair, pd.DataFrame())


# ---------------------------------------------------------
# RSI MULTI-TF
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
