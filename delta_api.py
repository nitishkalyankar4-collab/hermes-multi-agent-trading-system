import urllib.request
import urllib.parse
import json
import time
from typing import Dict, List, Any, Optional

class DeltaExchangeAPI:
    """
    Delta Exchange India REST API Connector
    Provides methods to fetch market tickers, L2 orderbook depth, historical OHLCV klines,
    and recent trade histories for perpetual futures and spot pairs.
    """
    BASE_URL = "https://api.india.delta.exchange"

    def __init__(self):
        self.headers = {
            "User-Agent": "Hermes-Trading-Agent/1.0",
            "Accept": "application/json"
        }

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        url = f"{self.BASE_URL}{endpoint}"
        if params:
            query_string = urllib.parse.urlencode(params)
            url = f"{url}?{query_string}"

        req = urllib.request.Request(url, headers=self.headers)
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    if data.get("success", True):
                        return data.get("result", data)
        except Exception as e:
            print(f"[DeltaAPI Error] Request failed for {url}: {e}")
            return None
        return None

    def get_tickers(self) -> List[Dict[str, Any]]:
        """Fetch all current tickers for assets available on Delta Exchange India."""
        res = self._get("/v2/tickers")
        if isinstance(res, list):
            return res
        return []

    def get_ticker(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch ticker information for a specific symbol (e.g. 'BTCUSD')."""
        tickers = self.get_tickers()
        for t in tickers:
            if t.get("symbol") == symbol:
                return t
        return None

    def get_orderbook(self, symbol: str) -> Dict[str, Any]:
        """Fetch L2 orderbook depth (top 20 bids and asks)."""
        res = self._get(f"/v2/l2orderbook/{symbol}")
        if res and isinstance(res, dict):
            return res
        # Fallback structure if API call fails
        return {"buy_book": [], "sell_book": []}

    def get_klines(self, symbol: str, resolution: str = "1h", limit: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch historical candle data.
        resolutions: 1m, 5m, 15m, 1h, 4h, 1d
        """
        end_time = int(time.time())
        # Approximate start time window based on resolution
        multipliers = {"1m": 60, "5m": 300, "15m": 900, "1h": 3600, "4h": 14400, "1d": 86400}
        sec_per_bar = multipliers.get(resolution, 3600)
        start_time = end_time - (sec_per_bar * limit)

        params = {
            "symbol": symbol,
            "resolution": resolution,
            "start": start_time,
            "end": end_time
        }
        res = self._get("/v2/history/candles", params)
        if isinstance(res, list):
            return res
        return []

    def get_recent_trades(self, symbol: str) -> List[Dict[str, Any]]:
        """Fetch recent execution trade logs to compute CVD (Cumulative Volume Delta)."""
        res = self._get(f"/v2/trades/{symbol}")
        if isinstance(res, list):
            return res
        return []
