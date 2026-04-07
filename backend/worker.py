import asyncio
import logging

import MetaTrader5 as mt5

from backend.config import settings
from backend.execution.trade import place_buy, place_sell
from backend.mt5.connection import mt5_manager
from backend.signals import signal_generator
from backend.supabase.client import supabase_client

logger = logging.getLogger("worker")


class BotWorker:
    def __init__(self):
        self.last_signal = {}  # 🔥 Prevent duplicate trades

    # 🔥 Fetch watchlist from Supabase
    def get_watchlist(self):
        try:
            response = supabase_client.table("watchlist").select("*").execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Error fetching watchlist: {e}")
            return []

    # 🔥 Check bot status from DB (UI controlled)
    def is_bot_running(self):
        try:
            response = supabase_client.table("bot_control").select("*").limit(1).execute()
            if response.data:
                return response.data[0].get("is_running", False)
            return False
        except Exception as e:
            logger.error(f"Error fetching bot control: {e}")
            return False

    async def start(self):
        signal_generator.set_brick_size(settings.RENKO_BRICK_SIZE)
        mt5_manager.connect_all()

        while True:
            # 🔥 UI control via Supabase
            if not self.is_bot_running():
                await asyncio.sleep(1)
                continue

            await self.cycle()
            await asyncio.sleep(settings.POLL_INTERVAL)

    async def stop(self):
        mt5_manager.disconnect_all()

    async def cycle(self):
        watchlist = self.get_watchlist()

        if not watchlist:
            logger.warning("Watchlist empty")
            return

        for login, session in mt5_manager.sessions.items():
            for symbol_data in watchlist:
                try:
                    # 🔥 Skip inactive symbols
                    if not symbol_data.get("is_active", True):
                        continue

                    symbol = symbol_data["symbol"]
                    lot_size = float(symbol_data.get("lot_size", 0.01))

                    session.ensure_connected()

                    tick = mt5.symbol_info_tick(symbol)
                    if tick is None:
                        logger.warning(f"No tick for {symbol}")
                        continue

                    # 🔥 Use ASK price for trading
                    price = float(tick.ask)

                    signal = signal_generator.get_signal(symbol, price)

                    # 🔥 Prevent duplicate trades
                    if signal == self.last_signal.get(symbol):
                        continue

                    if signal == "BUY":
                        place_buy(session, symbol, price, lot_size)
                        self.log_event(login, f"BUY_{symbol}")

                    elif signal == "SELL":
                        place_sell(session, symbol, price, lot_size)
                        self.log_event(login, f"SELL_{symbol}")

                    # 🔥 Store last signal
                    self.last_signal[symbol] = signal

                except Exception as exc:
                    logger.exception(f"Error on account {login}, symbol {symbol}: {exc}")
                    self.log_event(login, f"error:{symbol}:{exc}")

    def log_event(self, account_id: int, event: str):
        try:
            supabase_client.table("logs").insert({
                "account_id": account_id,
                "event": event
            }).execute()
        except Exception as e:
            logger.error(f"Supabase logging failed: {e}")


bot_worker = BotWorker()