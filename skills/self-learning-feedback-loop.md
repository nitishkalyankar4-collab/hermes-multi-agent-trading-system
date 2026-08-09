# Self-Learning Feedback Loop Skill

This skill defines the rules for logging signal history, tracking win rates, and adaptively tuning confluence thresholds.

## Evaluation Process

1. **Outcome Tracking**:
   - Evaluates active signals against real-time ticker prices.
   - A signal is marked `WIN` if price reaches Target 2 (`TP2`).
   - A signal is marked `LOSS` if price touches Stop Loss (`SL`).
2. **Adaptive Threshold Adjustment**:
   - If historical win rate drops below 65%, increase minimum confluence index threshold by +2% (up to 90%).
   - If historical win rate exceeds 80%, relax confluence index threshold by -1% (down to 75%).
