from typing import Dict, Any

class MacroAgent:
    """
    Macro & Market Regime Sub-Agent
    Analyzes global market conditions, Bitcoin dominance, and relative strength
    to determine the macro trading environment.
    """
    def __init__(self):
        self.name = "Macro Regime Agent"

    def analyze(self, btc_ticker: Dict[str, Any], target_ticker: Dict[str, Any]) -> Dict[str, Any]:
        score = 0
        details = []

        btc_change = float(btc_ticker.get("price_change_percent_24h", 0))
        target_change = float(target_ticker.get("price_change_percent_24h", 0)) if target_ticker else 0

        # Market Regime
        if btc_change > 2.0:
            regime = "BULLISH_TREND"
            score += 25
            details.append(f"Macro Crypto Tide: Bullish (BTC {btc_change:+.2f}%)")
        elif btc_change < -2.0:
            regime = "BEARISH_TREND"
            score -= 25
            details.append(f"Macro Crypto Tide: Bearish (BTC {btc_change:+.2f}%)")
        else:
            regime = "RANGING"
            details.append(f"Macro Crypto Tide: Neutral/Ranging (BTC {btc_change:+.2f}%)")

        # Relative Strength vs BTC
        rel_strength = target_change - btc_change
        if rel_strength > 1.5:
            score += 20
            details.append(f"Outperforming BTC by {rel_strength:+.2f}% (Relative Strength)")
        elif rel_strength < -1.5:
            score -= 20
            details.append(f"Underperforming BTC by {rel_strength:+.2f}% (Relative Weakness)")

        return {
            "score": score,
            "regime": regime,
            "relative_strength": round(rel_strength, 2),
            "details": details
        }
