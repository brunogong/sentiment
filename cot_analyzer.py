import pandas as pd
import requests
from datetime import datetime, timedelta
from io import StringIO
import json
import os

class COTAnalyzer:
    """
    Analizzatore dei report COT della CFTC
    Fonte ufficiale: https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm
    """
    
    def __init__(self, cache_dir='data/cache'):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        
        # Mappatura coppie forex ai simboli COT
        self.cot_mapping = {
            'EURUSD': '099741',   # Euro FX
            'GBPUSD': '096742',   # British Pound
            'USDJPY': '097741',   # Japanese Yen
            'AUDUSD': '232741',   # Australian Dollar
            'USDCAD': '090741',   # Canadian Dollar
            'NZDUSD': '112741',   # New Zealand Dollar
            'USDCHF': '092741',   # Swiss Franc
        }
    
    def fetch_cot_data(self):
        """
        Recupera i dati COT più recenti
        """
        cache_file = f"{self.cache_dir}/cot_data.json"
        
        # Controlla cache
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                cached = json.load(f)
                cache_age = datetime.now() - datetime.fromisoformat(cached['timestamp'])
                if cache_age.seconds < 86400:  # 24 ore
                    return cached['data']
        
        try:
            # URL dati CFTC (formato CSV)
            base_url = "https://www.cftc.gov/files/dea/history/futures_disagg_xls_2024.zip"
            
            # Per demo, usiamo dati simulati realistici
            # In produzione, usare: pd.read_csv() con download vero
            
            cot_data = self._get_simulated_cot()
            
            # Salva in cache
            with open(cache_file, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'data': cot_data
                }, f)
            
            return cot_data
            
        except Exception as e:
            print(f"Errore COT: {e}")
            return self._get_fallback_cot()
    
    def _get_simulated_cot(self):
        """Dati COT simulati basati su pattern reali"""
        return {
            'EURUSD': {
                'commercial_long': 35,
                'commercial_short': 48,
                'noncommercial_long': 62,
                'noncommercial_short': 28,
                'bias': 'bullish',
                'net_position': 34,  # noncommercial_long - noncommercial_short
                'signal_strength': 'strong'
            },
            'GBPUSD': {
                'commercial_long': 42,
                'commercial_short': 41,
                'noncommercial_long': 45,
                'noncommercial_short': 44,
                'bias': 'neutral',
                'net_position': 1,
                'signal_strength': 'weak'
            },
            'USDJPY': {
                'commercial_long': 52,
                'commercial_short': 33,
                'noncommercial_long': 38,
                'noncommercial_short': 55,
                'bias': 'bearish',
                'net_position': -17,
                'signal_strength': 'moderate'
            },
            'AUDUSD': {
                'commercial_long': 28,
                'commercial_short': 58,
                'noncommercial_long': 58,
                'noncommercial_short': 29,
                'bias': 'bullish',
                'net_position': 29,
                'signal_strength': 'strong'
            },
            'USDCAD': {
                'commercial_long': 45,
                'commercial_short': 40,
                'noncommercial_long': 44,
                'noncommercial_short': 47,
                'bias': 'neutral',
                'net_position': -3,
                'signal_strength': 'weak'
            }
        }
    
    def _get_fallback_cot(self):
        """Dati di fallback in caso di errore"""
        return self._get_simulated_cot()
