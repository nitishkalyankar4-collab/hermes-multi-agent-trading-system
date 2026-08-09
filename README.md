# Hermes Multi-Agent Trading System for Delta Exchange India

An institutional-grade multi-agent signal generation system for Delta Exchange India perpetual futures and spot markets.

## Architecture

Hermes uses a multi-agent framework designed around specialized quantitative and market-structure sub-agents:

1. **Head Agent (`agents/head_agent.py`)**: Chief Alpha Orchestrator that coordinates all sub-agents and calculates composite confluence scores.
2. **Order Flow & Whale Agent (`agents/orderflow_agent.py`)**: Ingests L2 order book depth, Cumulative Volume Delta (CVD), funding rate anomalies, and large trade clusters.
3. **Smart Money Concepts (SMC) Agent (`agents/smc_agent.py`)**: Detects Market Structure Shifts (MSS), Break of Structure (BOS), Change of Character (ChoCh), Order Blocks, and Fair Value Gaps (FVGs).
4. **Quant & Multi-Timeframe Agent (`agents/quant_agent.py`)**: Computes multi-timeframe alignment across 1H/4H/1D candles, RSI momentum, EMA ribbons, and ATR volatility.
5. **Risk Validator Agent (`agents/risk_agent.py`)**: Calculates ATR stop-loss levels, multi-target take-profits, risk/reward ratios, position sizing hints, and re-validates active positions.
6. **Macro Regime Agent (`agents/macro_agent.py`)**: Tracks broader market sentiment, Bitcoin dominance, and relative strength.
7. **Self-Learning Agent (`agents/learning_agent.py`)**: Logs historical signal outcomes, tracks win rates, and adaptively tunes minimum confluence thresholds.

## Features

- **Telegram Bot Integration (`bot.py`)**:
  - `/begin`: Starts autonomous background market scanner.
  - `/stopapp`: Safely halts background scanner daemon.
  - `/analyse <symbol>`: Triggers deep institutional AI scan for a specific asset (e.g., `BTCUSD`, `SOLUSD`).
  - `/crosscheck`: Re-evaluates all active open signals against live price action.
- **Institutional Web Dashboard (`web_dashboard/`)**:
  - Terminal dark-mode aesthetic served on port `8888`.
  - Real-time market metrics, win rates, active position cards, and interactive scan controls.
- **Automated Unit Tests (`tests/test_hermes.py`)**:
  - Full test suite verifying API integration, sub-agent evaluations, and bot command handlers.

## Getting Started

### Prerequisites

- Python 3.10+
- `httpx` / `urllib`

### Installation

```bash
git clone https://github.com/nitishkalyankar4-collab/hermes-multi-agent-trading-system.git
cd hermes-multi-agent-trading-system
pip install -r requirements.txt
```

### Running the System

1. **Start the Web Dashboard**:
   ```bash
   python3 -m delta_signal_bot.web_dashboard.server
   ```
   Access the dashboard at `http://localhost:8888`.

2. **Start the Telegram Bot**:
   ```bash
   export TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
   python3 -m delta_signal_bot.bot
   ```

3. **Run Unit Tests**:
   ```bash
   python3 -m unittest discover -s tests -v
   ```

## License

MIT License
