import unittest
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, os.path.dirname(BASE_DIR))

from delta_signal_bot.delta_api import DeltaExchangeAPI
from delta_signal_bot.agents.head_agent import HeadAgent
from delta_signal_bot.agents.orderflow_agent import OrderFlowAgent
from delta_signal_bot.agents.smc_agent import SMCAgent
from delta_signal_bot.agents.quant_agent import QuantAgent
from delta_signal_bot.agents.risk_agent import RiskAgent
from delta_signal_bot.agents.macro_agent import MacroAgent
from delta_signal_bot.agents.learning_agent import LearningAgent
from delta_signal_bot.bot import DeltaTelegramBot

class TestHermesTradingSystem(unittest.TestCase):

    def setUp(self):
        self.api = DeltaExchangeAPI()
        self.head = HeadAgent()
        self.bot = DeltaTelegramBot("TEST_TOKEN")

    def test_delta_api_tickers(self):
        tickers = self.api.get_tickers()
        self.assertIsInstance(tickers, list)
        self.assertGreater(len(tickers), 0)
        self.assertIn("symbol", tickers[0])

    def test_delta_api_ticker_btcusd(self):
        ticker = self.api.get_ticker("BTCUSD")
        self.assertIsInstance(ticker, dict)
        self.assertEqual(ticker.get("symbol"), "BTCUSD")

    def test_orderflow_agent(self):
        agent = OrderFlowAgent()
        t = self.api.get_ticker("BTCUSD") or {}
        ob = self.api.get_orderbook("BTCUSD")
        trades = self.api.get_recent_trades("BTCUSD")
        result = agent.analyze(t, ob, trades)
        self.assertIn("score", result)
        self.assertIn("bias", result)

    def test_smc_agent(self):
        agent = SMCAgent()
        kl_1h = self.api.get_klines("BTCUSD", "1h", 60)
        kl_4h = self.api.get_klines("BTCUSD", "4h", 60)
        result = agent.analyze(kl_1h, kl_4h)
        self.assertIn("score", result)
        self.assertIn("bias", result)

    def test_quant_agent(self):
        agent = QuantAgent()
        kl_1h = self.api.get_klines("BTCUSD", "1h", 60)
        t = self.api.get_ticker("BTCUSD") or {}
        result = agent.analyze(kl_1h, t)
        self.assertIn("score", result)
        self.assertIn("bias", result)

    def test_macro_agent(self):
        agent = MacroAgent()
        btc_ticker = self.api.get_ticker("BTCUSD") or {"price_change_percent_24h": "0"}
        t = self.api.get_ticker("ETHUSD") or {}
        result = agent.analyze(btc_ticker, t)
        self.assertIn("score", result)
        self.assertIn("regime", result)

    def test_risk_agent(self):
        agent = RiskAgent()
        params = agent.calculate_trade_parameters("BUY", 65000.0, 500.0, {})
        self.assertEqual(params["entry_price"], 65000.0)
        self.assertIn("stop_loss", params)
        self.assertIn("tp1", params)

    def test_learning_agent(self):
        test_db = os.path.join(BASE_DIR, "test_learning_db.json")
        if os.path.exists(test_db):
            os.remove(test_db)
        agent = LearningAgent(db_path=test_db)
        stats = agent.evaluate_performance([])
        self.assertIn("total_signals", stats)
        if os.path.exists(test_db):
            os.remove(test_db)

    def test_head_agent_processing(self):
        t = self.api.get_ticker("BTCUSD")
        ob = self.api.get_orderbook("BTCUSD")
        kl_1h = self.api.get_klines("BTCUSD", "1h", 60)
        kl_4h = self.api.get_klines("BTCUSD", "4h", 60)
        trades = self.api.get_recent_trades("BTCUSD")
        res = self.head.process_asset("BTCUSD", t, ob, kl_1h, kl_4h, trades, t)
        self.assertIn("direction", res)
        self.assertIn("confidence_pct", res)
        self.assertIn("agent_breakdowns", res)

    def test_telegram_bot_commands(self):
        messages = []
        self.bot.send_message = lambda chat_id, text, parse_mode="HTML": messages.append(text)
        
        self.bot.handle_command(12345, "/start")
        self.assertGreater(len(messages), 0)
        self.assertIn("Delta Exchange Institutional Signal Bot", messages[-1])

        self.bot.handle_command(12345, "/begin")
        self.assertIn("STARTED", messages[-1])
        self.assertTrue(self.bot.is_scanning)

        self.bot.handle_command(12345, "/stopapp")
        self.assertIn("STOPPED", messages[-1])
        self.assertFalse(self.bot.is_scanning)

if __name__ == "__main__":
    unittest.main()
