import requests
import pandas as pd
import streamlit as st
from utils.mapping import COT_MAPPING

CFTC_URL = "https://www.cftc.gov/files/dea/history/deacot{}.txt"


@st.cache_data(ttl=3600)
def fetch_cftc_report(code):
    url = CFTC_URL.format(code)

    try:
        df = pd.read_csv(url, sep="\t")
        return df

    except Exception as e:
        st.warning(f"⚠ Errore CFTC ({code}): {e}")
        return pd.DataFrame()


def parse_cot(df):
    if df.empty:
        return {
            "non_commercial": 0,
            "commercial": 0,
            "leveraged_funds": 0,
            "dealers": 0,
            "net": 0,
            "delta": 0,
            "sentiment": 50,
        }

    last = df.iloc[-1]

    nc = last.get("Noncommercial Long", 0) - last.get("Noncommercial Short", 0)
    lf = last.get("Leveraged Funds Long", 0) - last.get("Leveraged Funds Short", 0)
    comm = last.get("Commercial Long", 0) - last.get("Commercial Short", 0)
    dealers = last.get("Dealer Long", 0) - last.get("Dealer Short", 0)

    net = nc + lf

    if len(df) > 1:
        prev = df.iloc[-2]
        prev_net = (
            (prev.get("Noncommercial Long", 0) - prev.get("Noncommercial Short", 0))
            + (prev.get("Leveraged Funds Long", 0) - prev.get("Leveraged Funds Short", 0))
        )
        delta = net - prev_net
    else:
        delta = 0

    sentiment = max(0, min(100, 50 + (net / 50000) * 50))

    return {
        "non_commercial": int(nc),
        "commercial": int(comm),
        "leveraged_funds": int(lf),
        "dealers": int(dealers),
        "net": int(net),
        "delta": int(delta),
        "sentiment": round(sentiment, 2),
    }


def get_cot(pair):
    info = COT_MAPPING[pair]
    df = fetch_cftc_report(info["code"])
    return parse_cot(df)
