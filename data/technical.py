import requests
import pandas as pd

def get_price_history(symbol, interval="1h", outputsize=200):
    """
    Scarica dati OHLC multi-timeframe.
    """
    # Placeholder TwelveData / AlphaVantage
    return pd.DataFrame()  # da sostituire con API reali


def calc_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = -delta.where(delta < 0, 0).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def get_rsi_multi_tf(symbol):
    """
    Restituisce RSI su 1H, 4H, 1D.
    """
    return {
        "rsi_1h": 50,
        "rsi_4h": 50,
        "rsi_1d": 50
    }
