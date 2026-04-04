def generate_signal(pair, cot, retail, rsi, atr, df):
    """
    Sistema AI-driven con score 0–100.
    """

    score = 0
    conditions = []

    # -------------------------
    # 1. TREND FILTER (4H + 1D)
    # -------------------------
    try:
        ema50 = df["close"].ewm(span=50).mean().iloc[-1]
        ema200 = df["close"].ewm(span=200).mean().iloc[-1]
        price = df["close"].iloc[-1]

        trend_bias = None

        if price > ema200:
            score += 20
            trend_bias = "bullish"
            conditions.append("Trend macro rialzista")
        else:
            score += 10
            trend_bias = "bearish"
            conditions.append("Trend macro ribassista")

        if ema50 > ema200:
            score += 10
            conditions.append("Trend operativo forte")
        else:
            score += 5
            conditions.append("Trend operativo debole")

    except:
        conditions.append("Trend non disponibile")


    # -------------------------
    # 2. MOMENTUM FILTER (1H)
    # -------------------------
    try:
        roc = (df["close"].iloc[-1] - df["close"].iloc[-5]) / df["close"].iloc[-5] * 100

        if rsi["rsi_1h"] > 50 and roc > 0:
            score += 20
            conditions.append("Momentum positivo")
        elif rsi["rsi_1h"] < 50 and roc < 0:
            score += 20
            conditions.append("Momentum negativo")
        else:
            score += 5
            conditions.append("Momentum neutro")

    except:
        conditions.append("Momentum non disponibile")


    # -------------------------
    # 3. VOLATILITY REGIME
    # -------------------------
    if atr > 0:
        if atr < df["close"].iloc[-1] * 0.002:
            score += 15
            conditions.append("Volatilità bassa (regime pulito)")
        else:
            score += 5
            conditions.append("Volatilità alta (regime instabile)")
    else:
        conditions.append("ATR non disponibile")


    # -------------------------
    # 4. RETAIL SENTIMENT
    # -------------------------
    if retail["long"] > 60:
        score += 10
        conditions.append("Retail LONG → preferenza SELL")
    if retail["short"] > 60:
        score += 10
        conditions.append("Retail SHORT → preferenza BUY")


    # -------------------------
    # 5. COT BIAS
    # -------------------------
    if cot["bias"] == "bullish":
        score += 15
        conditions.append("COT bullish")
    elif cot["bias"] == "bearish":
        score += 15
        conditions.append("COT bearish")


    # -------------------------
    # DECISIONE FINALE
    # -------------------------
    if score >= 80:
        action = "BUY" if trend_bias == "bullish" else "SELL"
    elif score >= 60:
        action = "BUY" if trend_bias == "bullish" else "SELL"
    elif score >= 40:
        action = "WEAK"
    else:
        action = "WAIT"

    return {
        "pair": pair,
        "action": action,
        "score": score,
        "conditions": conditions
    }
