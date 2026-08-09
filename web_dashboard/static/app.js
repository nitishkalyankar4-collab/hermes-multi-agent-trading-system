let allSignalsData = [];

document.addEventListener('DOMContentLoaded', () => {
    fetchSignals();

    document.getElementById('rescan-btn').addEventListener('click', () => {
        const btn = document.getElementById('rescan-btn');
        btn.innerText = '⚡ SCANNING...';
        btn.disabled = true;

        fetch('/api/rescan')
            .then(res => res.json())
            .then(data => {
                updateDashboard(data);
                btn.innerText = '⚡ FORCE RE-SCAN';
                btn.disabled = false;
            })
            .catch(err => {
                console.error(err);
                btn.innerText = '⚡ FORCE RE-SCAN';
                btn.disabled = false;
            });
    });

    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            filterAndRender();
        });
    });

    document.getElementById('search-input').addEventListener('input', () => {
        filterAndRender();
    });
});

function fetchSignals() {
    fetch('/api/signals')
        .then(res => res.json())
        .then(data => updateDashboard(data))
        .catch(err => console.error('Error fetching signals:', err));
}

function updateDashboard(data) {
    document.getElementById('scan-time').innerText = `LAST SCAN: ${data.last_scan_time || 'JUST NOW'}`;
    document.getElementById('stat-total').innerText = data.total_scanned || 0;
    document.getElementById('stat-buy').innerText = data.buy_signals_count || 0;
    document.getElementById('stat-sell').innerText = data.sell_signals_count || 0;
    document.getElementById('stat-winrate').innerText = `${data.win_rate_pct || 0.0}%`;

    allSignalsData = data.signals || [];
    filterAndRender();
}

function filterAndRender() {
    const activeFilter = document.querySelector('.filter-btn.active').dataset.filter;
    const searchQuery = document.getElementById('search-input').value.toUpperCase().trim();

    let filtered = allSignalsData.filter(item => {
        const matchSymbol = item.symbol.includes(searchQuery);
        if (!matchSymbol) return false;

        if (activeFilter === 'ALL') return true;
        if (activeFilter === 'BUY') return item.direction.includes('BUY');
        if (activeFilter === 'SELL') return item.direction.includes('SELL');
        if (activeFilter === 'STRONG') return item.direction.includes('STRONG');
        return true;
    });

    renderSignals(filtered);
}

function renderSignals(signals) {
    const container = document.getElementById('signals-container');
    if (!signals || signals.length === 0) {
        container.innerHTML = '<div style="grid-column: 1/-1; text-align: center; color: var(--text-muted); padding: 40px;">No matching signals found.</div>';
        return;
    }

    container.innerHTML = signals.map(s => {
        const rp = s.risk_params || {};
        const smc = s.agent_breakdowns?.smc || {};
        const of = s.agent_breakdowns?.order_flow || {};
        const quant = s.agent_breakdowns?.quant || {};

        return `
            <div class="signal-card">
                <div class="card-header">
                    <span class="asset-symbol">${s.symbol}</span>
                    <span class="badge-direction ${s.direction}">${s.direction}</span>
                </div>

                <div class="confluence-bar-container">
                    <div class="confluence-label">
                        <span>CONFLUENCE INDEX</span>
                        <span>${s.confidence_pct}%</span>
                    </div>
                    <div class="confluence-progress">
                        <div class="confluence-fill" style="width: ${s.confidence_pct}%"></div>
                    </div>
                </div>

                <div class="subagent-breakdown">
                    <div class="breakdown-row">
                        <span>Smart Money Structure (SMC):</span>
                        <span style="color: ${smc.score >= 0 ? 'var(--accent-bull)' : 'var(--accent-bear)'}">${smc.score || 0}/100</span>
                    </div>
                    <div class="breakdown-row">
                        <span>Order Flow & Whale Delta:</span>
                        <span style="color: ${of.score >= 0 ? 'var(--accent-bull)' : 'var(--accent-bear)'}">${of.score || 0}/100</span>
                    </div>
                    <div class="breakdown-row">
                        <span>Quant & Multi-Timeframe:</span>
                        <span style="color: ${quant.score >= 0 ? 'var(--accent-bull)' : 'var(--accent-bear)'}">${quant.score || 0}/100</span>
                    </div>
                </div>

                ${rp.entry_price ? `
                    <div class="trade-params">
                        <div class="param-item">
                            <span>ENTRY:</span> <span>$${rp.entry_price}</span>
                        </div>
                        <div class="param-item">
                            <span>STOP LOSS:</span> <span style="color: var(--accent-bear)">$${rp.stop_loss}</span>
                        </div>
                        <div class="param-item">
                            <span>TARGET 2 (TP2):</span> <span style="color: var(--accent-bull)">$${rp.tp2}</span>
                        </div>
                        <div class="param-item">
                            <span>R/R RATIO:</span> <span>${rp.risk_reward_ratio}</span>
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
    }).join('');
}
