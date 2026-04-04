import requests

def myfxbook_login(email, password):
    url = f"https://www.myfxbook.com/api/login.json?email={email}&password={password}"
    return requests.get(url).json()["session"]


def get_retail_sentiment(session):
    try:
        url = f"https://www.myfxbook.com/api/get-community-outlook.json?session={session}"
        data = requests.get(url, timeout=5).json()

        sentiment = {}
        for item in data["symbols"]:
            pair = item["name"]
            sentiment[pair] = {
                "long": float(item["longPercentage"]),
                "short": float(item["shortPercentage"])
            }

        return sentiment

    except:
        return {}
