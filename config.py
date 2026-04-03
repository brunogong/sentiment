import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Coppie forex monitorate
    FOREX_PAIRS = [
        'EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 
        'NZDUSD', 'USDCHF', 'EURGBP', 'EURJPY', 'GBPJPY'
    ]
    
    # Soglie per segnali
    THRESHOLDS = {
        'extreme_retail': 70,      # % oltre la quale è estremo
        'high_confidence': 65,      # % per alta confidenza
        'medium_confidence': 55     # % per media confidenza
    }
    
    # Cache TTL (secondi)
    CACHE_TTL = {
        'cot': 86400,           # 24 ore (COT è settimanale)
        'myfxbook': 3600,       # 1 ora
        'prices': 300           # 5 minuti
    }
    
    # API Keys (opzionali - per upgrade a pagamento)
    RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY', '')
    OANDA_API_KEY = os.getenv('OANDA_API_KEY', '')
    
    # Modalità sviluppo/produzione
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
