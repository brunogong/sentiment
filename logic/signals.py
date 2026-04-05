import numpy as np


# ---------------------------------------------------------
# TREND (EMA 50/200)
# ---------------------------------------------------------
def get_trend(df):
    if df.empty or len(df) < 200:
        return "neutral"

    df["ema50"] = df["close"].ewm(span=50).mean()
    df["ema200"] = df["close"].ewm(span=200).mean()

    if df["ema50"].iloc[-1] > df["ema200"].iloc[-1]:
        return "bullish"
    elif df["ema50"].iloc[-1] < df["ema200"].iloc[-1]:
        return "bearish"
    else:
        return "neutral"


# ---------------------------------------------------------
# MOMENTUM (ROC 14)
# ---------------------------------------------------------
def get_momentum(df, period=14):
    if df.empty or len(df) < period + 1:
        return "neutral"

    roc = (df["close"].iloc[-1] - df["close"].iloc[-period]) / df["close"].iloc[-period] * 100

    if roc > 0.2:
        return "bullish"
    elif roc < -0.2:
        return "bearish"
    else:
        return "neutral"


# ---------------------------------------------------------
# COT BIAS (VERSIONE PRO)
# ---------------------------------------------------------
def get_cot_bias(cot):
    if cot["sentiment"] > 55:
        return "bullish"
    elif cot["sentiment"] < 45:
        return "bearish"
    else:
        return "neutral"


# ---------------------------------------------------------
# SCORE AI-DRIVEN 0–100
# ---------------------------------------------------------
def compute_score(trend, momentum, cot_bias, retail, rsi, atr):
    score = 50  # base neutra

    # Trend
    if trend == "bullish":
        score += 10
    elif trend == "bearish":
        score -= 10

    # Momentum
    if momentum == "bullish":
        score += 10
    elif momentum == "bearish":
        score -= 10

    # COT istituzionale
    if cot_bias == "bullish":
        score += 15
    elif cot_bias == "bearish":
        score -= 15

    # Retail sentiment (contrarian)
    if retail["long"] > 60:
        score -= 10
    elif retail["short"] > 60:
        score += 10

    # RSI multi‑TF
    if rsi["rsi_1h"] < 30:
        score += 5
    elif rsi["rsi_1h"] > 70:
        score -= 5

    if rsi["rsi_4h"] < 30:
        score += 5
    elif rsi["rsi_4h"] > 70:
        score -= 5

    # ATR (volatilità)
    if atr > 0:
        score += 5

    return max(0, min(100, score))


# ---------------------------------------------------------
# GENERATORE DI SEGNALE
# ---------------------------------------------------------
def generate_signal(pair, cot, retail, rsi, atr, df):
    trend = get_trend(df)
    momentum = get_momentum(df)
    cot_bias = get_cot_bias(cot)

    score = compute_score(trend, momentum, cot_bias, retail, rsi, atr)

    # Decisione finale
    if score >= 65:
        action = "BUY"
    elif score <= 35:
        action = "SELL"
    else:
        action = "WAIT"

    return {
        "pair": pair,
        "action": action,
        "score": score,
        "trend": trend,
        "momentum": momentum,
        "cot_bias": cot_bias,
        "cot_sentiment": cot["sentiment"],
        "retail": retail,
        "rsi": rsi,
        "atr": atr,
    }
