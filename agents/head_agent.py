from typing import Dict, List, Any
import time

from delta_signal_bot.agents.smc_agent import SMCAgent
from delta_signal_bot.agents.orderflow_agent import OrderFlowAgent
from delta_signal_bot.agents.quant_agent import QuantAgent
from delta_signal_bot.agents.risk_agent import RiskAgent
from delta_signal_bot.agents.macro_agent import MacroAgent
from delta_signal_bot.agents.learning_agent import LearningAgent

class HeadAgent:
    """
    Chief Alpha Orchestrator / Head Agent
    Synthesizes outputs from all specialized sub-agents to calculate a final
    institutional confluence index and produce trade execution parameters.
    """
    def __init__(self):
        self.smc_agent = SMCAgent()
        self.orderflow_agent = OrderFlowAgent()
        self.quant_agent = QuantAgent()
        self.risk_agent = RiskAgent()
        self.macro_agent = MacroAgent()
        self.learning_agent = LearningAgent()

    def process_asset(
        self, 
        symbol: str, 
        ticker: Dict[str, Any], 
        orderbook: Dict[str, Any], 
        klines_1h: List[Dict[str, Any]], 
        klines_4h: List[Dict[str, Any]], 
        trades: List[Dict[str, Any]],
        btc_ticker: Dict[str, Any]
    ) -> Dict[str, Any]:
        
        cur_price = float(ticker.get("mark_price", ticker.get("close", 0))) if ticker else 0.0

        # Sub-agent evaluations
        smc_res = self.smc_agent.analyze(klines_1h, klines_4h)
        of_res = self.orderflow_agent.analyze(ticker, orderbook, trades)
        quant_res = self.quant_agent.analyze(klines_1h, ticker)
        macro_res = self.macro_agent.analyze(btc_ticker, ticker)

        # Composite score calculation (Weighted alpha model)
        composite_score = (
            (smc_res["score"] * 0.35) +
            (of_res["score"] * 0.30) +
            (quant_res["score"] * 0.25) +
            (macro_res["score"] * 0.10)
        )

        # Get adaptive confluence threshold from Learning Agent
        learning_stats = self.learning_agent.load_db()
        min_threshold = learning_stats.get("min_confluence_threshold", 80)

        # Normalize score to 0-100 confidence
        confidence_pct = min(100.0, round(abs(composite_score), 1))

        # Direction determination
        if composite_score >= min_threshold:
            direction = "STRONG_BUY" if composite_score >= 85 else "BUY"
        elif composite_score <= -min_threshold:
            direction = "STRONG_SELL" if composite_score <= -85 else "SELL"
        else:
            direction = "NEUTRAL"

        # Calculate trade parameters via Risk Agent
        atr = quant_res.get("indicators", {}).get("atr", cur_price * 0.01)
        risk_params = {}
        if direction != "NEUTRAL":
            risk_params = self.risk_agent.calculate_trade_parameters(
                direction=direction,
                current_price=cur_price,
                atr=atr,
                smc_structures=smc_res.get("structures", {})
            )

        signal_output = {
            "symbol": symbol,
            "direction": direction,
            "confidence_pct": confidence_pct,
            "composite_score": round(composite_score, 2),
            "current_price": cur_price,
            "timestamp": int(time.time()),
            "risk_params": risk_params,
            "agent_breakdowns": {
                "smc": smc_res,
                "order_flow": of_res,
                "quant": quant_res,
                "macro": macro_res
            }
        }

        # Log signal to learning database if valid trade
        if direction != "NEUTRAL":
            self.learning_agent.record_signal({
                "symbol": symbol,
                "direction": direction,
                "confidence_pct": confidence_pct,
                "entry_price": risk_params.get("entry_price"),
                "stop_loss": risk_params.get("stop_loss"),
                "tp1": risk_params.get("tp1"),
                "tp2": risk_params.get("tp2"),
                "tp3": risk_params.get("tp3")
            })

        return signal_output
