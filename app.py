from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from datetime import datetime
import json
import os

from config import Config
from cot_analyzer import COTAnalyzer
from myfxbook_scraper import MyFxBookScraper
from price_fetcher import PriceFetcher
from signal_generator import SignalGenerator

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
CORS(app)

# Inizializza componenti
cot_analyzer = COTAnalyzer()
myfx_scraper = MyFxBookScraper()
price_fetcher = PriceFetcher()
signal_gen = SignalGenerator(Config.THRESHOLDS)

# Cache globale per i dati
data_cache = {
    'cot': None,
    'myfx': None,
    'prices': None,
    'levels': None,
    'signals': None,
    'last_update': None
}

def refresh_data():
    """Aggiorna tutti i dati"""
    try:
        # Recupera COT
        cot_data = cot_analyzer.fetch_cot_data()
        
        # Recupera sentiment Myfxbook
        myfx_data = myfx_scraper.get_sentiment()
        
        # Recupera prezzi attuali
        prices = price_fetcher.get_current_prices(Config.FOREX_PAIRS)
        
        # Calcola livelli pivot
        levels = {}
        for pair in Config.FOREX_PAIRS:
            level = price_fetcher.calculate_pivot_levels(pair, prices.get(pair))
            if level:
                levels[pair] = level
        
        # Genera segnali
        signals = signal_gen.generate_signals(cot_data, myfx_data, levels, prices)
        
        # Aggiorna cache
        data_cache['cot'] = cot_data
        data_cache['myfx'] = myfx_data
        data_cache['prices'] = prices
        data_cache['levels'] = levels
        data_cache['signals'] = signals
        data_cache['last_update'] = datetime.now().isoformat()
        
        return True
    except Exception as e:
        print(f"Errore refresh dati: {e}")
        return False

@app.route('/')
def index():
    """Pagina principale"""
    if not data_cache['last_update']:
        refresh_data()
    
    return render_template('index.html', 
                         pairs=Config.FOREX_PAIRS,
                         last_update=data_cache['last_update'])

@app.route('/api/dashboard')
def api_dashboard():
    """API per dashboard (dati in JSON)"""
    if not data_cache['last_update']:
        refresh_data()
    
    return jsonify({
        'signals': data_cache['signals'],
        'cot': data_cache['cot'],
        'myfx': data_cache['myfx'],
        'levels': data_cache['levels'],
        'prices': data_cache['prices'],
        'last_update': data_cache['last_update']
    })

@app.route('/api/refresh', methods=['POST'])
def api_refresh():
    """Forza refresh dei dati"""
    success = refresh_data()
    return jsonify({'success': success, 'last_update': data_cache['last_update']})

@app.route('/api/signals')
def api_signals():
    """Solo segnali"""
    if not data_cache['last_update']:
        refresh_data()
    
    return jsonify({
        'signals': data_cache['signals'],
        'count': len(data_cache['signals']),
        'last_update': data_cache['last_update']
    })

if __name__ == '__main__':
    # Primo refresh all'avvio
    refresh_data()
    
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=5000)
