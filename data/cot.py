import requests
import pandas as pd
import streamlit as st
from utils.mapping import COT_MAPPING


CFTC_URL = "https://www.cftc.gov/files/dea/history/deacot{}.txt"


def fetch_cftc_report(code):
    """
    Scarica il report CFTC storico per un future specifico.
    """
    url = CFTC_URL.format(code)
    try:
        df = pd.read_csv(url, sep="\t")
        return df
    except Exception as e:
        st.warning(f"⚠ Errore CFTC ({code}): {e}")
        return pd.DataFrame()


def parse_cot(df):
    """
    Estrae i valori principali dal report COT:
    - Non-Commercial
    - Commercial
    - Leveraged Funds
    - Dealer/Intermediary
    - Net Positions
    - Delta settimanale
    """
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

    # Prendi l’ultima riga (report più recente)
    last = df.iloc[-1]

    # Campi standard CFTC
    nc_long = last.get("Noncommercial Long", 0)
    nc_short = last.get("Noncommercial Short", 0)

    comm_long = last.get("Commercial Long", 0)
    comm_short = last.get("Commercial Short", 0)

    lev_long = last.get("Leveraged Funds Long", 0)
    lev_short = last.get("Leveraged Funds Short", 0)

    dealer_long = last.get("Dealer Long", 0)
    dealer_short = last.get("Dealer Short", 0)

    # Net positions istituzionali
    net = (nc_long - nc_short) + (lev_long - lev_short)

    # Delta settimanale (variazione net)
    if len(df) > 1:
        prev = df.iloc[-2]
        prev_net = (
            (prev.get("Noncommercial Long", 0) - prev.get("Noncommercial Short", 0))
            + (prev.get("Leveraged Funds Long", 0) - prev.get("Leveraged Funds Short", 0))
        )
        delta = net - prev_net
    else:
        delta = 0

    # Sentiment istituzionale 0–100
    sentiment = 50
    if net != 0:
        sentiment = max(0, min(100, 50 + (net / 50000) * 50))

    return {
        "non_commercial": int(nc_long - nc_short),
        "commercial": int(comm_long - comm_short),
        "leveraged_funds": int(lev_long - lev_short),
        "dealers": int(dealer_long - dealer_short),
        "net": int(net),
        "delta": int(delta),
        "sentiment": round(sentiment, 2),
    }


def get_cot(pair):
    """
    Funzione principale chiamata da app.py
    """
    info = COT_MAPPING[pair]
    df = fetch_cftc_report(info["code"])
    return parse_cot(df)
