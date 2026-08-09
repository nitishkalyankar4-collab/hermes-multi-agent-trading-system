import json
import time
import os
from typing import Dict, List, Any

class LearningAgent:
    """
    Self-Learning & Continuous Improvement Sub-Agent
    Logs historical signals, evaluates post-signal performance, tracks Win Rate & Profit Factor,
    and dynamically tunes confluence thresholds daily to maximize profitability.
    """
    def __init__(self, db_path: str = None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, "learning_db.json")
        self.name = "Self-Learning & Performance Agent"
        self.db_path = db_path
        self._ensure_db()

    def _ensure_db(self):
        if not os.path.exists(self.db_path):
            initial_data = {
                "total_signals": 0,
                "winning_signals": 0,
                "losing_signals": 0,
                "win_rate_pct": 0.0,
                "min_confluence_threshold": 80,
                "signals": [],
                "learnings_log": [
                    {"timestamp": int(time.time()), "note": "Self-learning system initialized with baseline institutional confluence rules."}
                ]
            }
            with open(self.db_path, "w") as f:
                json.dump(initial_data, f, indent=2)

    def load_db(self) -> Dict[str, Any]:
        self._ensure_db()
        try:
            with open(self.db_path, "r") as f:
                return json.load(f)
        except Exception:
            return {"total_signals": 0, "winning_signals": 0, "win_rate_pct": 0.0, "min_confluence_threshold": 80, "signals": [], "learnings_log": []}

    def save_db(self, data: Dict[str, Any]):
        with open(self.db_path, "w") as f:
            json.dump(data, f, indent=2)

    def record_signal(self, signal: Dict[str, Any]):
        db = self.load_db()
        signal["recorded_at"] = int(time.time())
        signal["status"] = "OPEN"
        db["signals"].append(signal)
        db["total_signals"] = len(db["signals"])
        self.save_db(db)

    def evaluate_performance(self, current_tickers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compares past open signals against recent prices to update win rate and adjust thresholds."""
        db = self.load_db()
        ticker_map = {t["symbol"]: float(t.get("mark_price", t.get("close", 0))) for t in current_tickers if "symbol" in t}

        updated = False
        wins = db.get("winning_signals", 0)
        losses = db.get("losing_signals", 0)

        for sig in db.get("signals", []):
            if sig.get("status") == "OPEN":
                sym = sig.get("symbol")
                if sym in ticker_map:
                    cur_p = ticker_map[sym]
                    entry_p = float(sig.get("entry_price", cur_p))
                    tp2 = float(sig.get("tp2", cur_p))
                    sl = float(sig.get("stop_loss", cur_p))
                    direction = sig.get("direction")

                    # Check hit
                    if direction in ["BUY", "STRONG_BUY"]:
                        if cur_p >= tp2:
                            sig["status"] = "WIN"
                            wins += 1
                            updated = True
                        elif cur_p <= sl:
                            sig["status"] = "LOSS"
                            losses += 1
                            updated = True
                    else:
                        if cur_p <= tp2:
                            sig["status"] = "WIN"
                            wins += 1
                            updated = True
                        elif cur_p >= sl:
                            sig["status"] = "LOSS"
                            losses += 1
                            updated = True

        if updated:
            db["winning_signals"] = wins
            db["losing_signals"] = losses
            total_resolved = wins + losses
            if total_resolved > 0:
                win_rate = (wins / total_resolved) * 100.0
                db["win_rate_pct"] = round(win_rate, 2)

                # Adaptive Threshold Tuning
                if win_rate < 65.0 and total_resolved >= 5:
                    db["min_confluence_threshold"] = min(90, db.get("min_confluence_threshold", 80) + 2)
                    db["learnings_log"].append({
                        "timestamp": int(time.time()),
                        "note": f"Adjusted confluence threshold up to {db['min_confluence_threshold']}% to filter false signals after win rate fell to {win_rate:.1f}%."
                    })
                elif win_rate > 80.0 and total_resolved >= 5:
                    db["min_confluence_threshold"] = max(75, db.get("min_confluence_threshold", 80) - 1)

            self.save_db(db)

        return {
            "total_signals": db.get("total_signals", 0),
            "winning_signals": db.get("winning_signals", 0),
            "losing_signals": db.get("losing_signals", 0),
            "win_rate_pct": db.get("win_rate_pct", 0.0),
            "min_confluence_threshold": db.get("min_confluence_threshold", 80),
            "learnings_count": len(db.get("learnings_log", []))
        }
