# utils/mapping.py

# Mappatura logica delle coppie usate nell'app
PAIRS = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"]

# (Opzionale) Mappatura per Alpha Vantage, se vuoi tenerlo come fallback
ALPHA_MAPPING = {
    "EURUSD": ("EUR", "USD"),
    "GBPUSD": ("GBP", "USD"),
    "USDJPY": ("USD", "JPY"),
    "XAUUSD": ("XAU", "USD"),
}

# Mappatura simboli per Massive
# Se Massive usa lo stesso formato simbolo (es. "EURUSD"), basta questo:
MASSIVE_SYMBOLS = {
    "EURUSD": "EURUSD",
    "GBPUSD": "GBPUSD",
    "USDJPY": "USDJPY",
    "XAUUSD": "XAUUSD",
}
