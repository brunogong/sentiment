from datetime import datetime

class SignalGenerator:
    """
    Generatore di segnali di trading basati su:
    - COT (posizionamento istituzionale)
    - Myfxbook (sentiment retail)
    - Livelli tecnici
    """
    
    def __init__(self, thresholds):
        self.thresholds = thresholds
    
    def generate_signals(self, cot_data, myfx_data, levels, prices):
        """
        Genera segnali con scoring
        """
        signals = []
        
        for pair in cot_data.keys():
            if pair not in myfx_data or pair not in levels:
                continue
            
            cot = cot_data[pair]
            retail = myfx_data[pair]
            level = levels[pair]
            price = prices.get(pair)
            
            # Calcola score combinato (0-100)
            score, signal_type, reason = self._calculate_score(cot, retail, level, price)
            
            if score > 60:  # Solo segnali con score > 60
                # Determina entry, TP, SL in base al livello
                if signal_type == 'BUY':
                    entry = level['s1']
                    tp1 = level['pivot']
                    tp2 = level['r1']
                    sl = level['s2']
                else:
                    entry = level['r1']
                    tp1 = level['pivot']
                    tp2 = level['s1']
                    sl = level['r2']
                
                signals.append({
                    'pair': pair,
                    'action': signal_type,
                    'confidence': self._get_confidence_level(score),
                    'score': score,
                    'reason': reason,
                    'entry': entry,
                    'tp1': tp1,
                    'tp2': tp2,
                    'sl': sl,
                    'current_price': price,
                    'risk_reward': self._calculate_rr(entry, tp1, sl, signal_type),
                    'timestamp': datetime.now().isoformat()
                })
        
        # Ordina per score decrescente
        signals.sort(key=lambda x: x['score'], reverse=True)
        return signals
    
    def _calculate_score(self, cot, retail, level, price):
        """Calcola score combinato (0-100)"""
        score = 0
        reasons = []
        
        # 1. COT bias (max 40 punti)
        if cot['bias'] == 'bullish':
            if cot['signal_strength'] == 'strong':
                score += 40
                reasons.append("COT fortemente rialzista")
            else:
                score += 25
                reasons.append("COT moderatamente rialzista")
        elif cot['bias'] == 'bearish':
            if cot['signal_strength'] == 'strong':
                score += 40
                reasons.append("COT fortemente ribassista")
            else:
                score += 25
                reasons.append("COT moderatamente ribassista")
        
        # 2. Contrarian signal (max 40 punti)
        if retail['contrarian_signal'] == 'buy':
            if retail['retail_extremity'] == 'extreme':
                score += 40
                reasons.append("Retail estremamente short (segnale rialzista)")
            else:
                score += 25
                reasons.append("Retail short (segnale rialzista moderato)")
        elif retail['contrarian_signal'] == 'sell':
            if retail['retail_extremity'] == 'extreme':
                score += 40
                reasons.append("Retail estremamente long (segnale ribassista)")
            else:
                score += 25
                reasons.append("Retail long (segnale ribassista moderato)")
        
        # 3. Posizione rispetto ai livelli (max 20 punti)
        if price and level:
            if price < level['s1']:
                score += 20
                reasons.append("Prezzo sotto supporto chiave")
            elif price > level['r1']:
                score += 20
                reasons.append("Prezzo sopra resistenza chiave")
            elif price < level['pivot']:
                score += 10
                reasons.append("Prezzo sotto pivot")
            elif price > level['pivot']:
                score += 10
                reasons.append("Prezzo sopra pivot")
        
        # Determina direzione del segnale
        signal_type = None
        if cot['bias'] == 'bullish' and retail['contrarian_signal'] == 'buy':
            signal_type = 'BUY'
        elif cot['bias'] == 'bearish' and retail['contrarian_signal'] == 'sell':
            signal_type = 'SELL'
        elif score > 60:
            # Fallback basato sul bias dominante
            if cot['bias'] == 'bullish' or retail['contrarian_signal'] == 'buy':
                signal_type = 'BUY'
            else:
                signal_type = 'SELL'
        
        reason_text = ' | '.join(reasons[:3])
        return score, signal_type, reason_text
    
    def _get_confidence_level(self, score):
        if score >= 80:
            return 'HIGH'
        elif score >= 65:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _calculate_rr(self, entry, tp, sl, action):
        """Calcola rapporto rischio/rendimento"""
        try:
            if action == 'BUY':
                risk = entry - sl
                reward = tp - entry
            else:
                risk = sl - entry
                reward = entry - tp
            
            if risk > 0:
                return round(reward / risk, 2)
        except:
            pass
        return 0
