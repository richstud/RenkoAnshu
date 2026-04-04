import logging
from typing import Optional

import MetaTrader5 as mt5

from backend.config import settings
from backend.execution.lot import get_lot_for_account
from backend.mt5.connection import AccountSession
from backend.supabase.client import supabase_client

logger = logging.getLogger("execution")


def close_all_positions(session: AccountSession, symbol: str):
    session.ensure_connected()
    positions = mt5.positions_get(symbol=symbol)
    if positions is None:
        return

    for pos in positions:
        tp = mt5.order_send({
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": pos.symbol,
            "volume": pos.volume,
            "type": mt5.ORDER_TYPE_SELL if pos.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY,
            "position": pos.ticket,
            "price": mt5.symbol_info_tick(pos.symbol).bid if pos.type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(pos.symbol).ask,
            "deviation": 10,
            "magic": 123456,
            "comment": "renko-reversal-close",
        })
        logger.info(f"Close pos response: {tp}")


def place_order(session: AccountSession, symbol: str, side: str, price: float):
    session.ensure_connected()

    lot = get_lot_for_account(session)
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        raise RuntimeError(f"Symbol {symbol} not found")

    if not symbol_info.visible:
        if not mt5.symbol_select(symbol, True):
            raise RuntimeError(f"Failed to select symbol: {symbol}")

    current_price = mt5.symbol_info_tick(symbol)
    order_type = mt5.ORDER_TYPE_BUY if side == "buy" else mt5.ORDER_TYPE_SELL
    price_send = current_price.ask if side == "buy" else current_price.bid

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": order_type,
        "price": price_send,
        "deviation": 20,
        "magic": 123456,
        "comment": f"renko-{side}",
    }

    result = mt5.order_send(request)
    logger.info(f"Order send {side} result: {result}")

    if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
        raise RuntimeError(f"Order {side} failed: {result}")

    trade_record = {
        "account_id": session.login,
        "symbol": symbol,
        "type": side,
        "lot": lot,
        "entry_price": price_send,
        "exit_price": None,
        "profit": None,
    }
    supabase_client.table("trades").insert(trade_record).execute()

    return result


def place_buy(session: AccountSession, symbol: str, price: float):
    close_all_positions(session, symbol)
    return place_order(session, symbol, "buy", price)


def place_sell(session: AccountSession, symbol: str, price: float):
    close_all_positions(session, symbol)
    return place_order(session, symbol, "sell", price)
