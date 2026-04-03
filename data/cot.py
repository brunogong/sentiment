import requests

def get_cot(symbol):
    """
    Restituisce COT reale (o mock se API non configurata).
    Output:
        { 'long': int, 'short': int, 'bias': 'bullish/bearish/neutral' }
    """
    try:
        # Placeholder API reale (Tradingster, Quandl, ecc.)
        # url = f"https://api.tradingster.com/cot/legacy_fut/{symbol}"
        # data = requests.get(url).json()

        # MOCK PRO (finché non inserisci API reale)
        mock = {
            'EURUSD': {'long': 62000, 'short': 28000},
            'GBPUSD': {'long': 45000, 'short': 44000},
            'USDJPY': {'long': 38000, 'short': 55000},
            'XAUUSD': {'long': 68000, 'short': 22000},
        }

        long = mock[symbol]['long']
        short = mock[symbol]['short']

        if long > short:
            bias = "bullish"
        elif short > long:
            bias = "bearish"
        else:
            bias = "neutral"

        return {"long": long, "short": short, "bias": bias}

    except:
        return {"long": 0, "short": 0, "bias": "neutral"}
