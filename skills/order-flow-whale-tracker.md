# Order Flow & Whale Tracker Skill

This skill defines the rules for processing market microstructure, orderbook dynamics, and institutional flows.

## Key Metrics & Thresholds

1. **Bid/Ask Imbalance**:
   - Ratio of aggregate bid depth to ask depth within top 20 levels.
   - Imbalance > 1.2 indicates strong passive buying support.
   - Imbalance < 0.8 indicates passive selling pressure.
2. **Open Interest (OI) & Price Divergence**:
   - `+OI` and `+Price`: Aggressive institutional long accumulation.
   - `+OI` and `-Price`: Aggressive institutional short position opening.
   - `-OI` and `+Price`: Short covering rally.
3. **Funding Rate Anomalies**:
   - High positive funding rate (> +0.03%) flags crowded long positioning.
