import requests
from utils.mapping import COT_MAPPING

def get_cot(pair):
    try:
        code = COT_MAPPING[pair]
        url = f"https://api.tradingster.com/cot/legacy_fut/{code}"
        data = requests.get(url, timeout=5).json()

        latest = data["data"][-1]

        long = latest["noncomm_positions_long"]
        short = latest["noncomm_positions_short"]

        if long > short:
            bias = "bullish"
        elif short > long:
            bias = "bearish"
        else:
            bias = "neutral"

        return {"long": long, "short": short, "bias": bias}

    except:
        return {"long": 0, "short": 0, "bias": "neutral"}
