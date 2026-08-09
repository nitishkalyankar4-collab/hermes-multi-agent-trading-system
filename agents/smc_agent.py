from typing import Dict, List, Any

class SMCAgent:
    """
    Smart Money Concepts (SMC) & Market Structure Sub-Agent
    Analyzes swing highs/lows, Market Structure Shifts (MSS), Break of Structure (BOS),
    Order Blocks (OB), Fair Value Gaps (FVG), and Liquidity Sweeps.
    """
    def __init__(self):
        self.name = "Smart Money Concepts Agent"

    def analyze(self, klines_1h: List[Dict[str, Any]], klines_4h: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not klines_1h or len(klines_1h) < 20:
            return {"score": 0, "bias": "NEUTRAL", "details": ["Insufficient kline data for SMC structure analysis"]}

        score = 0
        details = []

        closes = [float(k.get("close", 0)) for k in klines_1h]
        highs = [float(k.get("high", 0)) for k in klines_1h]
        lows = [float(k.get("low", 0)) for k in klines_1h]

        recent_high = max(highs[-20:-1])
        recent_low = min(lows[-20:-1])
        current_close = closes[-1]

        # Break of Structure (BOS)
        bos_bullish = current_close > recent_high
        bos_bearish = current_close < recent_low

        if bos_bullish:
            score += 35
            details.append(f"Bullish BOS (Break of Structure): Closed above 20-bar high (${recent_high:.2f})")
        elif bos_bearish:
            score -= 35
            details.append(f"Bearish BOS (Break of Structure): Closed below 20-bar low (${recent_low:.2f})")

        # Fair Value Gap (FVG) Detection (3-candle imbalance)
        bullish_fvg = False
        bearish_fvg = False
        if len(highs) >= 3:
            # Bullish FVG: Low of candle 3 > High of candle 1
            if lows[-1] > highs[-3]:
                bullish_fvg = True
                score += 25
                details.append(f"Bullish FVG (Fair Value Gap) detected at ${highs[-3]:.2f} - ${lows[-1]:.2f}")
            # Bearish FVG: High of candle 3 < Low of candle 1
            elif highs[-1] < lows[-3]:
                bearish_fvg = True
                score -= 25
                details.append(f"Bearish FVG (Fair Value Gap) detected at ${lows[-3]:.2f} - ${highs[-1]:.2f}")

        # Order Block (OB) Detection
        bullish_ob = False
        bearish_ob = False
        if len(closes) >= 5:
            # Bullish OB: Red candle before strong up move
            if closes[-3] < float(klines_1h[-3].get("open", 0)) and closes[-1] > highs[-3]:
                bullish_ob = True
                score += 20
                details.append(f"Institutional Bullish Order Block mitigated near ${lows[-3]:.2f}")
            elif closes[-3] > float(klines_1h[-3].get("open", 0)) and closes[-1] < lows[-3]:
                bearish_ob = True
                score -= 20
                details.append(f"Institutional Bearish Order Block mitigated near ${highs[-3]:.2f}")

        # Determine overall SMC Bias
        if score >= 30:
            bias = "BULLISH"
        elif score <= -30:
            bias = "BEARISH"
        else:
            bias = "NEUTRAL"

        return {
            "score": score,
            "bias": bias,
            "details": details,
            "structures": {
                "bos_bullish": bos_bullish,
                "bos_bearish": bos_bearish,
                "bullish_fvg": bullish_fvg,
                "bearish_fvg": bearish_fvg,
                "bullish_ob": bullish_ob,
                "bearish_ob": bearish_ob,
                "ob_price": lows[-3] if bullish_ob else (highs[-3] if bearish_ob else None),
                "recent_high": recent_high,
                "recent_low": recent_low
            }
        }
