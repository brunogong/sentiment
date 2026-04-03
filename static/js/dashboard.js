// Dashboard JavaScript
let currentFilter = 'all';
let refreshInterval = null;

// Inizializzazione
document.addEventListener('DOMContentLoaded', function() {
    loadDashboardData();
    
    // Refresh automatico ogni 5 minuti
    refreshInterval = setInterval(loadDashboardData, 300000);
    
    // Event listener refresh button
    document.getElementById('refreshBtn').addEventListener('click', function() {
        manualRefresh();
    });
    
    // Event listener filtri
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            currentFilter = this.dataset.filter;
            renderSignalsTable(window.signalsData);
        });
    });
});

// Carica dati dashboard
async function loadDashboardData() {
    try {
        const response = await fetch('/api/dashboard');
        const data = await response.json();
        
        window.signalsData = data.signals;
        
        updateStats(data.signals);
        renderSignalsTable(data.signals);
        renderCOTAnalysis(data.cot);
        renderRetailSentiment(data.myfx);
        
        // Aggiorna timestamp
        if (data.last_update) {
            const date = new Date(data.last_update);
            document.getElementById('lastUpdate').innerHTML = 
                date.toLocaleDateString('it-IT') + ' ' + date.toLocaleTimeString('it-IT');
        }
        
        // Aggiorna status LED
        document.getElementById('statusLed').style.color = '#10b981';
        document.getElementById('statusText').innerHTML = 'Online';
        
    } catch (error) {
        console.error('Errore caricamento dati:', error);
        document.getElementById('statusLed').style.color = '#ef4444';
        document.getElementById('statusText').innerHTML = 'Errore';
    }
}

// Aggiorna statistiche
function updateStats(signals) {
    const total = signals.length;
    const buys = signals.filter(s => s.action === 'BUY').length;
    const sells = signals.filter(s => s.action === 'SELL').length;
    const avgConfidence = signals.length > 0 
        ? Math.round(signals.reduce((sum, s) => sum + s.score, 0) / signals.length)
        : 0;
    
    document.getElementById('totalSignals').innerHTML = total;
    document.getElementById('buySignals').innerHTML = buys;
    document.getElementById('sellSignals').innerHTML = sells;
    document.getElementById('avgConfidence').innerHTML = avgConfidence + '%';
}

// Renderizza tabella segnali
function renderSignalsTable(signals) {
    const filtered = currentFilter === 'all' 
        ? signals 
        : signals.filter(s => s.confidence === currentFilter);
    
    const tbody = document.getElementById('signalsTableBody');
    
    if (filtered.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" class="loading-row">Nessun segnale disponibile</td></tr>';
        return;
    }
    
    tbody.innerHTML = filtered.map(signal => `
        <tr>
            <td><strong>${signal.pair}</strong></td>
            <td>
                <span class="action-badge ${signal.action === 'BUY' ? 'action-buy' : 'action-sell'}">
                    ${signal.action}
                </span>
            </td>
            <td class="confidence-${signal.confidence}">${signal.confidence}</td>
            <td>${signal.entry || '-'}</td>
            <td>${signal.tp1 || '-'}</td>
            <td>${signal.tp2 || '-'}</td>
            <td>${signal.sl || '-'}</td>
            <td>${signal.risk_reward || '-'}</td>
            <td style="font-size: 12px; color: #a0a5c0;">${signal.reason || '-'}</td>
        </tr>
    `).join('');
}

// Renderizza analisi COT
function renderCOTAnalysis(cotData) {
    const container = document.getElementById('cotContent');
    
    if (!cotData || Object.keys(cotData).length === 0) {
        container.innerHTML = '<div class="loading-small">Dati COT non disponibili</div>';
        return;
    }
    
    container.innerHTML = Object.entries(cotData).map(([pair, data]) => `
        <div class="sentiment-item">
            <div class="pair-name">${pair}</div>
            <div class="sentiment-bars">
                <div class="bar-long">
                    <div class="bar-long-fill" style="width: ${data.noncommercial_long || 50}%"></div>
                </div>
                <div class="bar-short">
                    <div class="bar-short-fill" style="width: ${data.noncommercial_short || 50}%"></div>
                </div>
            </div>
            <div class="percentages">
                L:${data.noncommercial_long || 0}% / S:${data.noncommercial_short || 0}%
            </div>
            <div style="width: 80px; text-align: right;">
                <span style="color: ${data.bias === 'bullish' ? '#10b981' : data.bias === 'bearish' ? '#ef4444' : '#f59e0b'}">
                    ${data.bias === 'bullish' ? '🟢 Bull' : data.bias === 'bearish' ? '🔴 Bear' : '⚪ Neutro'}
                </span>
            </div>
        </div>
    `).join('');
}

// Renderizza sentiment retail
function renderRetailSentiment(retailData) {
    const container = document.getElementById('retailContent');
    
    if (!retailData || Object.keys(retailData).length === 0) {
        container.innerHTML = '<div class="loading-small">Dati Myfxbook non disponibili</div>';
        return;
    }
    
    container.innerHTML = Object.entries(retailData).map(([pair, data]) => `
        <div class="sentiment-item">
            <div class="pair-name">${pair}</div>
            <div class="sentiment-bars">
                <div class="bar-long">
                    <div class="bar-long-fill" style="width: ${data.long_percentage || 50}%"></div>
                </div>
                <div class="bar-short">
                    <div class="bar-short-fill" style="width: ${data.short_percentage || 50}%"></div>
                </div>
            </div>
            <div class="percentages">
                L:${data.long_percentage || 0}% / S:${data.short_percentage || 0}%
            </div>
            <div style="width: 80px; text-align: right;">
                <span style="color: ${data.contrarian_signal === 'buy' ? '#10b981' : data.contrarian_signal === 'sell' ? '#ef4444' : '#f59e0b'}">
                    ${data.contrarian_signal === 'buy' ? '🟢 Compra' : data.contrarian_signal === 'sell' ? '🔴 Vendi' : '⚪ Neutro'}
                </span>
            </div>
        </div>
    `).join('');
}

// Refresh manuale
async function manualRefresh() {
    const refreshBtn = document.getElementById('refreshBtn');
    const originalHtml = refreshBtn.innerHTML;
    
    refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Aggiornamento...';
    refreshBtn.disabled = true;
    
    try {
        const response = await fetch('/api/refresh', { method: 'POST' });
        const result = await response.json();
        
        if (result.success) {
            await loadDashboardData();
        } else {
            alert('Errore durante l\'aggiornamento dei dati');
        }
    } catch (error) {
        console.error('Errore refresh:', error);
        alert('Errore di connessione');
    } finally {
        refreshBtn.innerHTML = originalHtml;
        refreshBtn.disabled = false;
    }
}
