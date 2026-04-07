import asyncio
import logging
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

from backend.config import settings
from backend.mt5.connection import mt5_manager
from backend.signals import signal_generator
from backend.supabase.client import supabase_client
from backend.worker import bot_worker

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Renko Reversal Gold Bot")

class AccountPayload(BaseModel):
    login: int
    password: str
    server: str

class SettingsPayload(BaseModel):
    brick_size: Optional[float]
    bot_status: Optional[str]

async def run_worker():
    await bot_worker.start()

@app.on_event("startup")
async def startup_event():
    # Setup supabase schema if needed
    pass

@app.post("/start-bot")
async def start_bot():
    if bot_worker.active:
        return {"message": "Bot already running"}

    asyncio.create_task(run_worker())
    return {"message": "Bot started"}

@app.post("/stop-bot")
async def stop_bot():
    if not bot_worker.active:
        return {"message": "Bot is not running"}
    await bot_worker.stop()
    return {"message": "Bot stopped"}

@app.get("/signal/{symbol}/{price}")
def get_signal_endpoint(symbol: str, price: float):
    """Get trading signal for a symbol at a given price."""
    try:
        signal = signal_generator.get_signal(symbol, price)
        brick_info = signal_generator.get_last_brick_info(symbol)
        return {
            "symbol": symbol,
            "price": price,
            "signal": signal,
            "brick_info": brick_info,
        }
    except Exception as exc:
        return {
            "symbol": symbol,
            "price": price,
            "error": str(exc),
        }

@app.post("/reset-signal/{symbol}")
def reset_signal(symbol: str):
    """Reset signal generator for a symbol."""
    signal_generator.reset_symbol(symbol)
    return {"message": f"Signal generator reset for {symbol}"}

@app.post("/accounts")
def add_account(account: AccountPayload):
    mt5_manager.add_account(account.login, account.password, account.server)
    data = {
        "login": account.login,
        "server": account.server,
        "status": "added",
    }
    supabase_client.table("accounts").insert(data).execute()
    return {"message": "Account added"}

@app.get("/accounts")
def get_accounts():
    res = supabase_client.table("accounts").select("*").execute()
    return res.data

@app.get("/trades")
def get_trades():
    res = supabase_client.table("trades").select("*").execute()
    return res.data

@app.get("/logs")
def get_logs():
    res = supabase_client.table("logs").select("*").order("created_at", {"ascending": False}).limit(100).execute()
    return res.data

@app.post("/update-settings")
def update_settings(payload: SettingsPayload):
    if payload.brick_size is not None:
        settings.RENKO_BRICK_SIZE = payload.brick_size
        supabase_client.table("settings").upsert({"id": 1, "brick_size": payload.brick_size}).execute()

    if payload.bot_status and payload.bot_status.lower() in {"started", "stopped"}:
        supabase_client.table("settings").upsert({"id": 1, "bot_status": payload.bot_status}).execute()

    return {"message": "Settings updated"}

@app.get("/health")
def health():
    return {"status": "ok", "active": bot_worker.active}
