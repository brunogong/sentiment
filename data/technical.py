import requests
import pandas as pd
from utils.mapping import TWELVEDATA_MAPPING
import streamlit as st

API_KEY = st.secrets["twelvedata_api_key"]

def get_ohlc(symbol, interval="1h", outputsize=200):
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval={interval}&outputsize={outputsize}&apikey={API_KEY}"
    data = requests.get(url, timeout=5).json()

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
    url = f"https://api.twelvedata.com/rsi?symbol={symbol}&interval={interval}&time_period={period}&apikey={API_KEY}"
    data = requests.get(url, timeout=5).json()
    return float(data["values"][0]["rsi"])


def get_rsi_multi_tf(symbol):
    return {
        "rsi_1h": get_rsi(symbol, "1h"),
        "rsi_4h": get_rsi(symbol, "4h"),
        "rsi_1d": get_rsi(symbol, "1day")
    }
