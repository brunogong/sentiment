# utils/mapping.py

# Coppie usate nell'app
PAIRS = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"]


# -----------------------------
# MASSIVE (provider OHLC)
# -----------------------------
MASSIVE_SYMBOLS = {
    "EURUSD": "EURUSD",
    "GBPUSD": "GBPUSD",
    "USDJPY": "USDJPY",
    "XAUUSD": "XAUUSD",
}


# -----------------------------
# ALPHA VANTAGE (fallback)
# -----------------------------
ALPHA_MAPPING = {
    "EURUSD": ("EUR", "USD"),
    "GBPUSD": ("GBP", "USD"),
    "USDJPY": ("USD", "JPY"),
    "XAUUSD": ("XAU", "USD"),
}


# -----------------------------
# COT MAPPING (CFTC)
# -----------------------------
# Ogni coppia Forex viene collegata al future corretto
# per estrarre il Commitment of Traders (COT)
COT_MAPPING = {
    "EURUSD": {
        "market": "EURO FX",
        "code": "099741",
        "symbol": "6E",
        "exchange": "CME",
    },
    "GBPUSD": {
        "market": "BRITISH POUND STERLING",
        "code": "096742",
        "symbol": "6B",
        "exchange": "CME",
    },
    "USDJPY": {
        "market": "JAPANESE YEN",
        "code": "097741",
        "symbol": "6J",
        "exchange": "CME",
    },
    "XAUUSD": {
        "market": "GOLD",
        "code": "088691",
        "symbol": "GC",
        "exchange": "COMEX",
    },
}
