import asyncio
import logging
from typing import Dict

import MetaTrader5 as mt5

from backend.config import settings
from backend.execution.trade import place_buy, place_sell
from backend.mt5.connection import mt5_manager
from backend.renko.engine import RenkoEngine
from backend.strategy.engine import StrategyEngine
from backend.supabase.client import supabase_client

logger = logging.getLogger("worker")

class BotWorker:
    def __init__(self):
        self.active = False
        self.renko_engine: Dict[int, RenkoEngine] = {}
        self.strategy_engine: Dict[int, StrategyEngine] = {}

    async def start(self):
        self.active = True
        mt5_manager.connect_all()

        while self.active:
            await self.cycle()
            await asyncio.sleep(settings.POLL_INTERVAL)

    async def stop(self):
        self.active = False
        mt5_manager.disconnect_all()

    async def cycle(self):
        for login, session in mt5_manager.sessions.items():
            try:
                session.ensure_connected()
                symbol = settings.SYMBOL

                tick = mt5.symbol_info_tick(symbol)
                if tick is None:
                    logger.warning(f"No tick for {symbol}")
                    continue

                price = float(tick.last)

                if login not in self.renko_engine:
                    self.renko_engine[login] = RenkoEngine(brick_size=settings.RENKO_BRICK_SIZE)
                    self.strategy_engine[login] = StrategyEngine(self.renko_engine[login])

                strategy = self.strategy_engine[login]
                signal = strategy.process_tick(price)

                if signal:
                    if signal["type"] == "buy":
                        place_buy(session, symbol, signal["price"])
                        self.log_event(login, "buy_executed")
                    elif signal["type"] == "sell":
                        place_sell(session, symbol, signal["price"])
                        self.log_event(login, "sell_executed")

            except Exception as exc:
                logger.exception(f"Error on account {login}: {exc}")
                self.log_event(login, f"error:{exc}")

    def log_event(self, account_id: int, event: str, latency: float = 0.0):
        supabase_client.table("logs").insert({"account_id": account_id, "event": event, "latency": latency}).execute()

bot_worker = BotWorker()
