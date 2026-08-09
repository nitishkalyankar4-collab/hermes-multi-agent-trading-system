from typing import Dict, Any

class RiskAgent:
    """
    Risk & Position Sizing Sub-Agent
    Calculates precise ATR-based stop losses, multi-target take profits (TP1, TP2, TP3),
    Risk/Reward ratios, and crosschecks active signals against live market price action.
    """
    def __init__(self):
        self.name = "Risk & Position Sizing Agent"

    def calculate_trade_parameters(
        self, 
        direction: str, 
        current_price: float, 
        atr: float, 
        smc_structures: Dict[str, Any]
    ) -> Dict[str, Any]:
        
        atr_buffer = atr * 1.5

        if "BUY" in direction:
            # Stop loss placed below recent low or ATR buffer
            recent_low = smc_structures.get("recent_low")
            if recent_low and (current_price - recent_low) < (atr * 3.0):
                stop_loss = round(recent_low - (atr * 0.5), 4)
            else:
                stop_loss = round(current_price - atr_buffer, 4)

            risk = current_price - stop_loss
            tp1 = round(current_price + (risk * 1.5), 4)
            tp2 = round(current_price + (risk * 2.5), 4)
            tp3 = round(current_price + (risk * 4.0), 4)
            rr_ratio = round((tp2 - current_price) / (current_price - stop_loss), 2) if risk > 0 else 2.0

        else:  # SELL / STRONG_SELL
            # Stop loss placed above recent high or ATR buffer
            recent_high = smc_structures.get("recent_high")
            if recent_high and (recent_high - current_price) < (atr * 3.0):
                stop_loss = round(recent_high + (atr * 0.5), 4)
            else:
                stop_loss = round(current_price + atr_buffer, 4)

            risk = stop_loss - current_price
            tp1 = round(current_price - (risk * 1.5), 4)
            tp2 = round(current_price - (risk * 2.5), 4)
            tp3 = round(current_price - (risk * 4.0), 4)
            rr_ratio = round((current_price - tp2) / (stop_loss - current_price), 2) if risk > 0 else 2.0

        risk_pct = round((abs(current_price - stop_loss) / current_price) * 100.0, 2)

        return {
            "entry_price": current_price,
            "stop_loss": stop_loss,
            "tp1": tp1,
            "tp2": tp2,
            "tp3": tp3,
            "risk_pct": risk_pct,
            "risk_reward_ratio": f"{rr_ratio}:1"
        }

    def crosscheck_active_trade(self, signal: Dict[str, Any], current_price: float, fresh_confluence_score: float) -> Dict[str, Any]:
        """Re-evaluates an active open signal against current market price."""
        direction = signal.get("direction")
        rp = signal.get("risk_params", {})
        entry = float(rp.get("entry_price", current_price))
        sl = float(rp.get("stop_loss", current_price))
        tp2 = float(rp.get("tp2", current_price))

        pnl_pct = ((current_price - entry) / entry) * 100.0 if "BUY" in direction else ((entry - current_price) / entry) * 100.0

        instruction = "HOLD"
        advice = "Trade structure intact; continue monitoring targets."

        if "BUY" in direction:
            if current_price <= sl:
                instruction = "STOP LOSS HIT (CLOSED)"
                advice = "Price hit stop loss level. Position liquidated safely."
            elif current_price >= tp2:
                instruction = "TAKE PROFIT 2 HIT (CLOSED)"
                advice = "Target 2 achieved. Lock in profits."
            elif fresh_confluence_score < 40:
                instruction = "INVALIDATED — EXIT EARLY"
                advice = "Confluence dropped significantly below baseline. Exit recommended."
        else:
            if current_price >= sl:
                instruction = "STOP LOSS HIT (CLOSED)"
                advice = "Price hit stop loss level. Position liquidated safely."
            elif current_price <= tp2:
                instruction = "TAKE PROFIT 2 HIT (CLOSED)"
                advice = "Target 2 achieved. Lock in profits."
            elif fresh_confluence_score > -40:
                instruction = "INVALIDATED — EXIT EARLY"
                advice = "Bearish confluence weakened. Exit recommended."

        return {
            "symbol": signal.get("symbol"),
            "entry_price": entry,
            "current_price": current_price,
            "pnl_pct": round(pnl_pct, 2),
            "instruction": instruction,
            "advice": advice
        }
