import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
import json
import os

class PriceFetcher:
    """
    Recupera prezzi e calcola livelli chiave
    """
    
    def __init__(self, cache_dir='data/cache'):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def get_current_prices(self, pairs):
        """Recupera prezzi attuali per tutte le coppie"""
        prices = {}
        
        for pair in pairs:
            try:
                # Formatta per Yahoo Finance
                symbol = f"{pair}=X"
                ticker = yf.Ticker(symbol)
                
                # Prezzo attuale
                data = ticker.history(period='1d', interval='1m')
                if not data.empty:
                    current_price = data['Close'].iloc[-1]
                    prices[pair] = current_price
                else:
                    prices[pair] = None
                    
            except Exception as e:
                print(f"Errore prezzo {pair}: {e}")
                prices[pair] = None
        
        return prices
    
    def calculate_pivot_levels(self, pair, current_price):
        """
        Calcola pivot points basati su daily
        """
        try:
            symbol = f"{pair}=X"
            ticker = yf.Ticker(symbol)
            
            # Prezzi giornalieri (ultimi 5 giorni)
            hist = ticker.history(period='5d')
            
            if len(hist) >= 2:
                yesterday = hist.iloc[-2]
                high = yesterday['High']
                low = yesterday['Low']
                close = yesterday['Close']
                
                # Pivot points formula standard
                pivot = (high + low + close) / 3
                r1 = 2 * pivot - low
                r2 = pivot + (high - low)
                r3 = high + 2 * (pivot - low)
                s1 = 2 * pivot - high
                s2 = pivot - (high - low)
                s3 = low - 2 * (high - pivot)
                
                return {
                    'pivot': round(pivot, 5),
                    'r1': round(r1, 5),
                    'r2': round(r2, 5),
                    'r3': round(r3, 5),
                    's1': round(s1, 5),
                    's2': round(s2, 5),
                    's3': round(s3, 5),
                    'current': round(current_price, 5) if current_price else None
                }
            
        except Exception as e:
            print(f"Errore pivot {pair}: {e}")
        
        # Fallback: livelli simulati
        if current_price:
            return {
                'pivot': round(current_price, 5),
                'r1': round(current_price * 1.005, 5),
                'r2': round(current_price * 1.01, 5),
                'r3': round(current_price * 1.02, 5),
                's1': round(current_price * 0.995, 5),
                's2': round(current_price * 0.99, 5),
                's3': round(current_price * 0.98, 5),
                'current': round(current_price, 5)
            }
        
        return None
