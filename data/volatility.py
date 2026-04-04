from data.technical import get_ohlc

def get_atr(symbol, interval="1h", period=14):
    df = get_ohlc(symbol, interval, outputsize=period*3)

    df["H-L"] = df["high"] - df["low"]
    df["H-PC"] = abs(df["high"] - df["close"].shift(1))
    df["L-PC"] = abs(df["low"] - df["close"].shift(1))

    tr = df[["H-L", "H-PC", "L-PC"]].max(axis=1)
    atr = tr.rolling(period).mean().iloc[-1]

    return float(atr)
