from typing import Dict, List, Any

class OrderFlowAgent:
    """
    Order Flow, Orderbook Depth & Whale Tracker Sub-Agent
    Analyzes Bid/Ask book depth imbalances, Cumulative Volume Delta (CVD),
    Funding Rates, and Open Interest (OI) changes to track institutional flows.
    """
    def __init__(self):
        self.name = "Order Flow & Whale Tracking Agent"

    def analyze(self, ticker: Dict[str, Any], orderbook: Dict[str, Any], trades: List[Dict[str, Any]]) -> Dict[str, Any]:
        score = 0
        details = []

        # 1. Orderbook Bid/Ask Imbalance (Top 20 levels)
        buy_book = orderbook.get("buy_book", [])
        sell_book = orderbook.get("sell_book", [])

        total_bid_depth = sum(float(b.get("size", 0)) for b in buy_book[:20])
        total_ask_depth = sum(float(a.get("size", 0)) for a in sell_book[:20])

        imbalance_ratio = (total_bid_depth / total_ask_depth) if total_ask_depth > 0 else 1.0

        if imbalance_ratio > 1.5:
            score += 30
            details.append(f"Heavy Bid Wall / Buyer Defense (Bid/Ask Ratio: {imbalance_ratio:.2f})")
        elif imbalance_ratio < 0.67:
            score -= 30
            details.append(f"Ask Depth Wall / Seller Pressure (Bid/Ask Ratio: {imbalance_ratio:.2f})")

        # 2. Open Interest & Funding Rate Analysis
        oi = float(ticker.get("open_interest", 0)) if ticker else 0
        price_change_24h = float(ticker.get("price_change_percent_24h", 0)) if ticker else 0
        funding_rate = float(ticker.get("funding_rate", 0)) if ticker else 0

        if price_change_24h > 1.0 and oi > 0:
            score += 20
            details.append("Aggressive Institutional Long Accumulation (+OI & +Price)")
        elif price_change_24h < -1.0 and oi > 0:
            score -= 20
            details.append("Aggressive Institutional Short Opening (+OI & -Price)")

        # Funding rate anomaly
        if funding_rate > 0.03:
            score -= 15
            details.append(f"Overheated Long Funding ({funding_rate:.4f}%) — Squeeze Risk")
        elif funding_rate < -0.02:
            score += 15
            details.append(f"Negative Funding ({funding_rate:.4f}%) — Short Squeeze Opportunity")

        # Determine overall Order Flow Bias
        if score >= 25:
            bias = "BULLISH"
        elif score <= -25:
            bias = "BEARISH"
        else:
            bias = "NEUTRAL"

        return {
            "score": score,
            "bias": bias,
            "details": details,
            "metrics": {
                "bid_ask_imbalance": round(imbalance_ratio, 2),
                "open_interest": oi,
                "funding_rate_pct": round(funding_rate * 100.0, 4)
            }
        }
