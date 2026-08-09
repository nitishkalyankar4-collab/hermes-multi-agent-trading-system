import http.server
import socketserver
import json
import os
import sys
import time
from urllib.parse import urlparse, parse_qs

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from delta_signal_bot.delta_api import DeltaExchangeAPI
from delta_signal_bot.agents.head_agent import HeadAgent

PORT = 8888
api = DeltaExchangeAPI()
head_agent = HeadAgent()

latest_scan_data = {
    "last_scan_time": "Not scanned yet",
    "total_scanned": 0,
    "buy_signals_count": 0,
    "sell_signals_count": 0,
    "strong_signals_count": 0,
    "win_rate_pct": 0.0,
    "signals": [],
    "market_overview": []
}

def perform_full_market_scan():
    global latest_scan_data
    tickers = api.get_tickers()
    btc_ticker = api.get_ticker("BTCUSD") or {"symbol": "BTCUSD", "price_change_percent_24h": "0"}

    results = []
    buy_count = 0
    sell_count = 0
    strong_count = 0

    target_symbols = [
        "BTCUSD", "ETHUSD", "SOLUSD", "XRPUSD", "DOGEUSD", 
        "AVAXUSD", "JUPUSD", "DOTUSD", "FILUSD", "INJUSD", 
        "WIFUSD", "OPUSD", "ARBUSD", "DYDXUSD", "UNIUSD", 
        "HBARUSD", "NEARUSD", "ADAUSD", "TIAUSD", "SUIUSD", "SEIUSD"
    ]

    for sym in target_symbols:
        t = api.get_ticker(sym) or {"symbol": sym}
        ob = api.get_orderbook(sym)
        kl_1h = api.get_klines(sym, "1h", 60)
        kl_4h = api.get_klines(sym, "4h", 60)
        trades = api.get_recent_trades(sym)

        res = head_agent.process_asset(sym, t, ob, kl_1h, kl_4h, trades, btc_ticker)
        results.append(res)

        direction = res["direction"]
        if "BUY" in direction:
            buy_count += 1
        if "SELL" in direction:
            sell_count += 1
        if "STRONG" in direction:
            strong_count += 1

    learning_stats = head_agent.learning_agent.evaluate_performance(tickers)

    latest_scan_data = {
        "last_scan_time": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "total_scanned": len(results),
        "buy_signals_count": buy_count,
        "sell_signals_count": sell_count,
        "strong_signals_count": strong_count,
        "win_rate_pct": learning_stats.get("win_rate_pct", 0.0),
        "signals": results,
        "market_overview": [api.get_ticker(s) for s in ["BTCUSD", "ETHUSD", "SOLUSD", "XRPUSD", "DOGEUSD"]]
    }
    return latest_scan_data

perform_full_market_scan()

class DashboardRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        if path == "/api/signals" or path == "/api/scan":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(latest_scan_data).encode("utf-8"))
            return

        if path == "/api/rescan":
            data = perform_full_market_scan()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode("utf-8"))
            return

        if path.startswith("/api/analyse/"):
            asset = path.split("/")[-1].upper()
            if not asset.endswith("USD"):
                asset += "USD"
            
            t = api.get_ticker(asset)
            ob = api.get_orderbook(asset)
            kl_1h = api.get_klines(asset, "1h", 60)
            kl_4h = api.get_klines(asset, "4h", 60)
            trades = api.get_recent_trades(asset)
            btc_t = api.get_ticker("BTCUSD")

            res = head_agent.process_asset(asset, t, ob, kl_1h, kl_4h, trades, btc_t)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(res).encode("utf-8"))
            return

        if path == "/" or path == "/index.html":
            DASHBOARD_DIR = os.path.dirname(os.path.abspath(__file__))
            html_path = os.path.join(DASHBOARD_DIR, "templates", "index.html")
            if os.path.exists(html_path):
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                with open(html_path, "rb") as f:
                    self.wfile.write(f.read())
                return

        if path.startswith("/static/"):
            DASHBOARD_DIR = os.path.dirname(os.path.abspath(__file__))
            static_file = os.path.join(DASHBOARD_DIR, path.lstrip("/"))
            if os.path.exists(static_file):
                self.send_response(200)
                if static_file.endswith(".css"):
                    self.send_header("Content-Type", "text/css")
                elif static_file.endswith(".js"):
                    self.send_header("Content-Type", "application/javascript")
                self.end_headers()
                with open(static_file, "rb") as f:
                    self.wfile.write(f.read())
                return

        self.send_response(404)
        self.end_headers()
        self.wfile.write(b"404 Not Found")

def run_server():
    server_address = ('0.0.0.0', PORT)
    httpd = socketserver.TCPServer(server_address, DashboardRequestHandler)
    print(f"Institutional Signal Dashboard Server running at http://localhost:{PORT}")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
