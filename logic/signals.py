def generate_signal(pair, cot, retail, rsi, atr, thresholds):
    score = 0
    conditions = []

    # COT
    if cot['bias'] == "bullish":
        score += 1
        conditions.append("COT Bullish")
    elif cot['bias'] == "bearish":
        score += 1
        conditions.append("COT Bearish")

    # Retail
    if retail['long'] > thresholds['retail_long']:
        score += 1
        conditions.append("Retail LONG eccessivo")
    if retail['short'] > thresholds['retail_short']:
        score += 1
        conditions.append("Retail SHORT eccessivo")

    # RSI multi-TF
    if rsi['rsi_1h'] < thresholds['rsi_oversold']:
        score += 1
        conditions.append("RSI 1H Oversold")
    if rsi['rsi_1h'] > thresholds['rsi_overbought']:
        score += 1
        conditions.append("RSI 1H Overbought")

    # Direzione finale
    if score >= 4:
        action = "BUY" if retail['short'] > retail['long'] else "SELL"
    else:
        action = "WAIT"

    return {
        "pair": pair,
        "action": action,
        "score": score,
        "conditions": conditions,
        "atr": atr
    }
