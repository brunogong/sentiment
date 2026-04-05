import requests
import pandas as pd
import streamlit as st
from utils.mapping import MASSIVE_SYMBOLS

API_KEY = st.secrets["massive_api_key"]


# ---------------------------------------------------------
# MASSIVE — OHLC 1m (1 chiamata/minuto grazie al caching)
# ---------------------------------------------------------
@st.cache_data(ttl=60)
def load_all_ohlc():
    """
    Carica TUTTE le coppie in una sola chiamata logica.
    In realtà Massive non ha un endpoint batch, quindi
    facciamo 4 chiamate ma solo 1 volta al minuto.
    """
    data = {}

    for pair, symbol in MASSIVE_SYMBOLS.items():

        url = (
            f"https://api.massive.app/v1/forex/ohlc?"
            f"symbol={symbol}&interval=1m&apiKey={API_KEY}"
        )

        try:
            response = requests.get(url, timeout=10)

            # Massive restituisce JSON valido → se non è JSON, errore
            raw = response.json()

            if "data" not in raw or not raw["data"]:
                st.warning(f"⚠ Massive non ha restituito OHLC per {pair}.")
                data[pair] = pd.DataFrame()
                continue

            df = pd.DataFrame(raw["data"])

            # Massive timestamp → secondi
            df["datetime"] = pd.to_datetime(df["timestamp"], unit="s")

            df = df.rename(columns={
                "open": "open",
                "high": "high",
                "low": "low",
                "close": "close"
            })

            df = df[["datetime", "open", "high", "low", "close"]]
            df = df.sort_values("datetime").reset_index(drop=True)

            data[pair] = df

        except Exception as e:
            st.error(f"❌ Errore Massive per {pair}: {e}")
            data[pair] = pd.DataFrame()

    return data


def get_ohlc(pair):
    """
    Restituisce il DataFrame OHLC per una singola coppia.
    """
    all_data = load_all_ohlc()
    return all_data.get(pair, pd.DataFrame())


# ---------------------------------------------------------
# RSI MULTI-TIMEFRAME
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

    df_4h = df.iloc[::240]  # 1m → 240 = 4h
    rsi_4h = calc_rsi(df_4h["close"], 14).iloc[-1]

    df_1d = df.iloc[::1440]  # 1m → 1440 = 1d
    rsi_1d = calc_rsi(df_1d["close"], 14).iloc[-1]

    return {
        "rsi_1h": round(rsi_1h, 2),
        "rsi_4h": round(rsi_4h, 2),
        "rsi_1d": round(rsi_1d, 2)
    }
