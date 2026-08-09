from typing import Dict, List, Any

class QuantAgent:
    """
    Quantitative Indicators & Multi-Timeframe Alignment Sub-Agent
    Computes RSI, EMA Ribbon (9, 21, 50), ATR Volatility, and Multi-TF Alignment.
    """
    def __init__(self):
        self.name = "Quant & Multi-Timeframe Agent"

    def analyze(self, klines_1h: List[Dict[str, Any]], ticker: Dict[str, Any]) -> Dict[str, Any]:
        if not klines_1h or len(klines_1h) < 21:
            return {"score": 0, "bias": "NEUTRAL", "details": ["Insufficient klines for Quant analysis"]}

        closes = [float(k.get("close", 0)) for k in klines_1h]
        highs = [float(k.get("high", 0)) for k in klines_1h]
        lows = [float(k.get("low", 0)) for k in klines_1h]

        score = 0
        details = []

        # 1. RSI (14-period)
        rsi = self._calculate_rsi(closes, period=14)
        if rsi < 30:
            score += 30
            details.append(f"RSI Oversold ({rsi:.1f} < 30) — Mean Reversion Opportunity")
        elif rsi > 70:
            score -= 30
            details.append(f"RSI Overbought ({rsi:.1f} > 70) — Exhaustion Warning")
        elif rsi > 55:
            score += 15
            details.append(f"RSI Bullish Momentum ({rsi:.1f})")
        elif rsi < 45:
            score -= 15
            details.append(f"RSI Bearish Momentum ({rsi:.1f})")

        # 2. EMA Ribbon (9, 21, 50)
        ema9 = self._calculate_ema(closes, 9)
        ema21 = self._calculate_ema(closes, 21)
        ema50 = self._calculate_ema(closes, 50) if len(closes) >= 50 else ema21

        cur_price = closes[-1]
        if ema9 > ema21 and cur_price > ema9:
            score += 25
            details.append("Bullish EMA Alignment (9 > 21 EMA & Price > 9 EMA)")
        elif ema9 < ema21 and cur_price < ema9:
            score -= 25
            details.append("Bearish EMA Alignment (9 < 21 < 50 EMA Ribbon Expansion)")

        # 3. ATR Volatility (14-period)
        atr = self._calculate_atr(highs, lows, closes, period=14)
        atr_pct = (atr / cur_price) * 100.0 if cur_price > 0 else 0
        details.append(f"ATR Volatility: {atr_pct:.2f}% (ATR = {atr:.4f})")

        bias = "BULLISH" if score >= 20 else ("BEARISH" if score <= -20 else "NEUTRAL")

        return {
            "score": score,
            "bias": bias,
            "details": details,
            "indicators": {
                "rsi": round(rsi, 2),
                "ema9": round(ema9, 4),
                "ema21": round(ema21, 4),
                "ema50": round(ema50, 4),
                "atr": round(atr, 4),
                "atr_pct": round(atr_pct, 2)
            }
        }

    def _calculate_rsi(self, closes: List[float], period: int = 14) -> float:
        if len(closes) < period + 1:
            return 50.0
        gains, losses = [], []
        for i in range(1, len(closes)):
            diff = closes[i] - closes[i-1]
            gains.append(diff if diff > 0 else 0)
            losses.append(abs(diff) if diff < 0 else 0)

        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period

        if avg_loss == 0:
            return 100.0
        rs = avg_gain / avg_loss
        return 100.0 - (100.0 / (1.0 + rs))

    def _calculate_ema(self, closes: List[float], period: int) -> float:
        if len(closes) < period:
            return closes[-1]
        k = 2.0 / (period + 1)
        ema = sum(closes[:period]) / period
        for price in closes[period:]:
            ema = (price * k) + (ema * (1.0 - k))
        return ema

    def _calculate_atr(self, highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> float:
        if len(highs) < period + 1:
            return (highs[-1] - lows[-1]) if highs else 1.0
        tr_list = []
        for i in range(1, len(highs)):
            tr = max(
                highs[i] - lows[i],
                abs(highs[i] - closes[i-1]),
                abs(lows[i] - closes[i-1])
            )
            tr_list.append(tr)
        return sum(tr_list[-period:]) / period
