# Smart Money Concepts (SMC) Analyzer Skill

This skill defines the rules for detecting institutional market structure shifts and liquidity dynamics.

## Key Indicators & Rules

1. **Market Structure Shifts (MSS)**:
   - **Bullish BOS**: Candle close above the previous 20-period swing high.
   - **Bearish BOS**: Candle close below the previous 20-period swing low.
2. **Fair Value Gaps (FVG)**:
   - Imbalance created when the high of candle 1 does not overlap with the low of candle 3.
   - Serves as a high-probability mitigation zone for limit orders.
3. **Order Blocks (OB)**:
   - The final down-candle prior to a strong upward expansion (Bullish OB).
   - The final up-candle prior to a strong downward expansion (Bearish OB).
4. **Liquidity Sweeps**:
   - Wick rejection taking out equal highs/lows before an aggressive reversal.
