import requests
import pandas as pd
import streamlit as st

API_KEY = st.secrets["alpha_vantage_key"]


def get_ohlc(symbol_tuple, interval="60min"):
    """
    Ottiene OHLC Forex da Alpha Vantage.
    symbol_tuple = ("EUR", "USD")
    """

    base, quote = symbol_tuple

    url = (
        "https://www.alphavantage.co/query?"
        f"function=FX_INTRADAY&from_symbol={base}&to_symbol={quote}"
        f"&interval={interval}&outputsize=full&apikey={API_KEY}"
    )

    try:
        data = requests.get(url, timeout=10).json()

        if "Time Series FX" not in data:
            st.warning(f"⚠️ Nessun OHLC Alpha Vantage per {base}{quote}.")
            return pd.DataFrame()

        ts = data["Time Series FX (60min)"]

        df = pd.DataFrame([
            {
                "datetime": pd.to_datetime(t),
                "open": float(v["1. open"]),
                "high": float(v["2. high"]),
                "low": float(v["3. low"]),
                "close": float(v["4. close"])
            }
            for t, v in ts.items()
        ])

        df = df.sort_values("datetime").reset_index(drop=True)
        return df

    except Exception as e:
        st.warning(f"⚠️ Errore Alpha Vantage: {e}")
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
