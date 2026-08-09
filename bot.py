import urllib.request
import urllib.parse
import json
import time
import threading
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from delta_signal_bot.delta_api import DeltaExchangeAPI
from delta_signal_bot.agents.head_agent import HeadAgent

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN_HERE")
SCAN_INTERVAL_SECONDS = 7200  # 2 Hours (default)

class DeltaTelegramBot:
    def __init__(self, token: str):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.api = DeltaExchangeAPI()
        self.head_agent = HeadAgent()
        self.is_scanning = False
        self.active_signals = {}  # {symbol: signal_dict}
        self.last_update_id = 0

    def send_message(self, chat_id: int, text: str, parse_mode: str = "HTML"):
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode
        }
        req = urllib.request.Request(
            url, 
            data=json.dumps(payload).encode('utf-8'),
            headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read().decode('utf-8'))
        except Exception as e:
            print(f"[Telegram Bot Error] Failed to send message: {e}")
            return None

    def get_updates(self):
        url = f"{self.base_url}/getUpdates?offset={self.last_update_id + 1}&timeout=5"
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as resp:
                res = json.loads(resp.read().decode('utf-8'))
                if res.get("ok"):
                    return res.get("result", [])
        except Exception:
            pass
        return []

    def handle_command(self, chat_id: int, text: str):
        parts = text.strip().split()
        cmd = parts[0].lower()

        if cmd == "/start":
            msg = (
                "🤖 <b>Delta Exchange Institutional Signal Bot</b>\n\n"
                "✅ <i>Connected & Operational!</i>\n\n"
                "📊 <b>Dashboard:</b> http://localhost:8888\n"
                "⏱ <b>Scan Cadence:</b> Active Scanning Engine\n\n"
                "<b>Available Commands:</b>\n"
                "• <code>/begin</code> - Start autonomous market scanner\n"
                "• <code>/stopapp</code> - Stop market scanner\n"
                "• <code>/analyse [symbol]</code> - Full AI Institutional Scan\n"
                "• <code>/crosscheck</code> - Live re-check of active signals"
            )
            self.send_message(chat_id, msg)

        elif cmd == "/begin":
            if self.is_scanning:
                self.send_message(chat_id, "⚙️ <b>Scanner is already running in background!</b>")
            else:
                self.is_scanning = True
                self.send_message(chat_id, "🚀 <b>Delta Exchange Signal Bot STARTED!</b>\n\nAutonomous institutional market scanning active.")
                threading.Thread(target=self._background_scan_loop, args=(chat_id,), daemon=True).start()

        elif cmd == "/stopapp":
            if not self.is_scanning:
                self.send_message(chat_id, "🛑 <b>Scanner is currently stopped.</b>")
            else:
                self.is_scanning = False
                self.send_message(chat_id, "🛑 <b>Delta Exchange Signal Bot STOPPED!</b>\n\nBackground scanner daemon safely halted.")

        elif cmd == "/analyse" or cmd == "/analyze":
            if len(parts) < 2:
                self.send_message(chat_id, "⚠️ Usage: <code>/analyse BTCUSD</code> or <code>/analyse SOLUSD</code>")
                return

            symbol = parts[1].upper()
            if not symbol.endswith("USD"):
                symbol += "USD"

            self.send_message(chat_id, f"🔍 <i>Performing deep institutional scan on {symbol}...</i>")

            t = self.api.get_ticker(symbol)
            ob = self.api.get_orderbook(symbol)
            kl_1h = self.api.get_klines(symbol, "1h", 60)
            kl_4h = self.api.get_klines(symbol, "4h", 60)
            trades = self.api.get_recent_trades(symbol)
            btc_t = self.api.get_ticker("BTCUSD")

            res = self.head_agent.process_asset(symbol, t, ob, kl_1h, kl_4h, trades, btc_t)

            dir_emoji = "🟢" if "BUY" in res["direction"] else ("🔴" if "SELL" in res["direction"] else "⚪")
            rp = res.get("risk_params", {})

            smc = res["agent_breakdowns"]["smc"]
            of = res["agent_breakdowns"]["order_flow"]
            quant = res["agent_breakdowns"]["quant"]

            msg = (
                f"📊 <b>INSTITUTIONAL AI SCAN REPORT: {symbol}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"⚡ <b>Direction:</b> {dir_emoji} {res['direction']}\n"
                f"🎯 <b>Confluence Index:</b> {res['confidence_pct']}%\n"
                f"💵 <b>Current Price:</b> ${res['current_price']}\n\n"
                f"🏛 <b>Smart Money Structure (SMC):</b>\n"
                f"• Score: {smc['score']}/100 ({smc['bias']})\n" +
                "".join([f"• {d}\n" for d in smc['details']]) + "\n"
                f"🌊 <b>Order Flow & Whale Activity:</b>\n"
                f"• Score: {of['score']}/100 ({of['bias']})\n" +
                "".join([f"• {d}\n" for d in of['details']]) + "\n"
                f"📈 <b>Quant & Multi-Timeframe Alignment:</b>\n"
                f"• Score: {quant['score']}/100 ({quant['bias']})\n" +
                "".join([f"• {d}\n" for d in quant['details']])
            )

            if rp.get("entry_price"):
                msg += (
                    f"\n🛡 <b>Trade Execution Parameters:</b>\n"
                    f"• Entry Range: ${rp['entry_price']}\n"
                    f"• Stop Loss: ${rp['stop_loss']} ({rp['risk_pct']}% Risk)\n"
                    f"• Target 1 (TP1): ${rp['tp1']}\n"
                    f"• Target 2 (TP2): ${rp['tp2']}\n"
                    f"• Target 3 (TP3): ${rp['tp3']}\n"
                    f"• Risk/Reward Ratio: {rp['risk_reward_ratio']}\n"
                )

            self.send_message(chat_id, msg)

        elif cmd == "/crosscheck":
            if not self.active_signals:
                self.send_message(chat_id, "📋 <b>No open/active signals to crosscheck right now.</b>")
                return

            self.send_message(chat_id, "🔄 <b>Re-checking active signal conditions against live market data...</b>")

            tickers = self.api.get_tickers()
            t_map = {t["symbol"]: float(t.get("mark_price", t.get("close", 0))) for t in tickers}

            reports = []
            for sym, sig in list(self.active_signals.items()):
                cur_p = t_map.get(sym, sig["current_price"])
                # Get fresh agent evaluation
                t = self.api.get_ticker(sym)
                ob = self.api.get_orderbook(sym)
                kl_1h = self.api.get_klines(sym, "1h", 60)
                kl_4h = self.api.get_klines(sym, "4h", 60)
                trades = self.api.get_recent_trades(sym)
                btc_t = self.api.get_ticker("BTCUSD")

                fresh_res = self.head_agent.process_asset(sym, t, ob, kl_1h, kl_4h, trades, btc_t)
                check_res = self.head_agent.risk_agent.crosscheck_active_trade(sig, cur_p, fresh_res["composite_score"])

                reports.append(
                    f"🔹 <b>{sym} ({sig['direction']})</b>\n"
                    f"• Entry: ${check_res['entry_price']} | Current: ${check_res['current_price']}\n"
                    f"• PnL: <b>{check_res['pnl_pct']:+.2f}%</b>\n"
                    f"• Action: <b>{check_res['instruction']}</b>\n"
                    f"• Note: <i>{check_res['advice']}</i>\n"
                )

                if "CLOSED" in check_res["instruction"] or "TAKE PROFIT" in check_res["instruction"]:
                    del self.active_signals[sym]

            msg = "⚡ <b>LIVE CROSSCHECK REPORT</b>\n━━━━━━━━━━━━━━━━━━━━━━━\n\n" + "\n".join(reports)
            self.send_message(chat_id, msg)

    def _background_scan_loop(self, chat_id: int):
        while self.is_scanning:
            tickers = self.api.get_tickers()
            btc_ticker = self.api.get_ticker("BTCUSD") or {"symbol": "BTCUSD", "price_change_percent_24h": "0"}

            buy_signals = []
            sell_signals = []

            target_symbols = [
                "BTCUSD", "ETHUSD", "SOLUSD", "XRPUSD", "DOGEUSD", 
                "AVAXUSD", "JUPUSD", "DOTUSD", "FILUSD", "INJUSD", 
                "WIFUSD", "OPUSD", "ARBUSD", "DYDXUSD", "UNIUSD", 
                "HBARUSD", "NEARUSD", "ADAUSD", "TIAUSD", "SUIUSD", "SEIUSD"
            ]

            for sym in target_symbols:
                if not self.is_scanning:
                    break
                t = self.api.get_ticker(sym) or {"symbol": sym}
                ob = self.api.get_orderbook(sym)
                kl_1h = self.api.get_klines(sym, "1h", 60)
                kl_4h = self.api.get_klines(sym, "4h", 60)
                trades = self.api.get_recent_trades(sym)

                res = self.head_agent.process_asset(sym, t, ob, kl_1h, kl_4h, trades, btc_ticker)

                if res["direction"] in ["BUY", "STRONG_BUY"]:
                    buy_signals.append(res)
                    self.active_signals[sym] = res
                elif res["direction"] in ["SELL", "STRONG_SELL"]:
                    sell_signals.append(res)
                    self.active_signals[sym] = res

            if self.is_scanning:
                now_str = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())
                msg = f"📊 <b>Delta Exchange v2 Scan</b>\n⏱ {now_str}\n\n"

                if buy_signals:
                    msg += "🟢 <b>BUY SIGNALS:</b>\n"
                    for s in buy_signals:
                        rp = s.get("risk_params", {})
                        msg += f"• <b>{s['symbol']}</b> — {s['direction']} ({s['confidence_pct']}% Confluence)\n  Entry: ${rp.get('entry_price')} | SL: ${rp.get('stop_loss')} | TP2: ${rp.get('tp2')}\n"
                    msg += "\n"

                if sell_signals:
                    msg += "🔴 <b>SELL SIGNALS:</b>\n"
                    for s in sell_signals:
                        rp = s.get("risk_params", {})
                        msg += f"• <b>{s['symbol']}</b> — {s['direction']} ({s['confidence_pct']}% Confluence)\n  Entry: ${rp.get('entry_price')} | SL: ${rp.get('stop_loss')} | TP2: ${rp.get('tp2')}\n"
                    msg += "\n"

                if not buy_signals and not sell_signals:
                    msg += "⚪ <b>No high-confluence institutional signals found — market neutral.</b>\n"

                msg += f"📋 {len(target_symbols)} scanned | {len(buy_signals)} buy | {len(sell_signals)} sell"
                self.send_message(chat_id, msg)

            time.sleep(SCAN_INTERVAL_SECONDS)

    def poll_telegram_updates(self):
        print("Telegram Bot Polling loop started...")
        while True:
            updates = self.get_updates()
            for u in updates:
                self.last_update_id = u["update_id"]
                msg = u.get("message", {})
                chat_id = msg.get("chat", {}).get("id")
                text = msg.get("text", "")
                if chat_id and text:
                    self.handle_command(chat_id, text)
            time.sleep(1)

if __name__ == "__main__":
    bot = DeltaTelegramBot(TELEGRAM_BOT_TOKEN)
    bot.poll_telegram_updates()
