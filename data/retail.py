import requests

def get_retail_sentiment():
    """
    Restituisce sentiment retail reale (o mock).
    """
    try:
        # Placeholder MyFxBook API
        # url = "https://www.myfxbook.com/api/get-community-outlook.json"
        # data = requests.get(url).json()

        mock = {
            'EURUSD': {'long': 42, 'short': 58},
            'GBPUSD': {'long': 35, 'short': 65},
            'USDJPY': {'long': 72, 'short': 28},
            'XAUUSD': {'long': 32, 'short': 68},
        }

        return mock

    except:
        return {}
