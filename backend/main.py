import asyncio
import logging
from typing import Optional

from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.config import settings
from backend.mt5.connection import mt5_manager
from backend.signals import signal_generator
from backend.supabase.client import supabase_client
from backend.worker import bot_worker
from backend.api.endpoints import router as api_router
from backend.websocket_manager import ws_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Renko Reversal Gold Bot")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router)

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
    """Initialize MT5 connection and load accounts on startup"""
    try:
        # Try to initialize default account from settings
        if settings.MT5_LOGIN and settings.MT5_PASSWORD and settings.MT5_SERVER:
            mt5_manager.add_account(
                settings.MT5_LOGIN,
                settings.MT5_PASSWORD,
                settings.MT5_SERVER
            )
            logger.info(f"Added default account {settings.MT5_LOGIN} from environment")
        
        # Load accounts from Supabase and connect
        try:
            response = supabase_client.table("accounts").select("*").execute()
            if response.data:
                for account in response.data:
                    if account["login"] not in mt5_manager.sessions:
                        # Skip, just load from DB for reference
                        pass
                logger.info(f"Loaded {len(response.data)} accounts from database")
        except Exception as e:
            logger.warning(f"Could not load accounts from Supabase: {e}")
        
        # Try to connect at least one account
        if mt5_manager.sessions:
            logger.info(f"Attempting to connect {len(mt5_manager.sessions)} account(s)")
            mt5_manager.connect_all()
        
    except Exception as e:
        logger.error(f"Startup error: {e}")

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
    res = supabase_client.table("logs").select("*").order("created_at", desc=True).limit(100).execute()
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
    """Health check endpoint with connection status"""
    mt5_connected = False
    connected_accounts = []
    
    for login, session in mt5_manager.sessions.items():
        if session.connected:
            mt5_connected = True
            connected_accounts.append(login)
    
    return {
        "status": "ok",
        "active": bot_worker.active,
        "mt5_connected": mt5_connected,
        "total_accounts": len(mt5_manager.sessions),
        "connected_accounts": connected_accounts,
        "api_version": "1.0"
    }

@app.get("/diagnose")
def diagnose():
    """Diagnose MT5 and system issues"""
    import MetaTrader5 as mt5
    
    diagnostics = {
        "mt5_initialized": False,
        "mt5_path": settings.MT5_PATH,
        "accounts_registered": len(mt5_manager.sessions),
        "accounts_connected": [],
        "default_account_configured": bool(settings.MT5_LOGIN),
        "supabase_connected": False,
        "issues": []
    }
    
    # Check if MT5 is initialized
    try:
        platform_info = mt5.terminal_info()
        if platform_info:
            diagnostics["mt5_initialized"] = True
    except Exception as e:
        diagnostics["issues"].append(f"MT5 not initialized: {str(e)}")
    
    # Check connected accounts
    for login, session in mt5_manager.sessions.items():
        if session.connected:
            diagnostics["accounts_connected"].append({
                "login": login,
                "server": session.server,
                "balance": session.get_balance()
            })
        else:
            diagnostics["issues"].append(f"Account {login} is not connected")
    
    # Check Supabase
    try:
        supabase_client.table("accounts").select("*").limit(1).execute()
        diagnostics["supabase_connected"] = True
    except Exception as e:
        diagnostics["issues"].append(f"Supabase connection failed: {str(e)}")
    
    if not diagnostics["mt5_initialized"]:
        diagnostics["issues"].append(
            "MT5 Terminal is not running. Launch MetaTrader 5 and ensure you are logged in."
        )
    
    if not diagnostics["accounts_connected"]:
        diagnostics["issues"].append(
            f"No MT5 accounts connected. Check your credentials in .env and ensure MT5 terminal is running."
        )
    
    return diagnostics


# ===================================
# WebSocket - Real-time Data Streaming
# ===================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time data streaming"""
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and receive any messages from client
            data = await websocket.receive_text()
            if data == "ping":
                await ws_manager.send_personal(websocket, {"type": "pong"})
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        ws_manager.disconnect(websocket)


# ===================================
# Manual Trade Execution Endpoints
# ===================================

class TradeRequest(BaseModel):
    account_id: int
    symbol: str
    trade_type: str  # "buy" or "sell"
    lot_size: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None


@app.post("/execute-trade")
async def execute_manual_trade(trade: TradeRequest):
    """Execute a manual trade from the frontend"""
    try:
        # Get the account session
        account_session = mt5_manager.get_session(trade.account_id)
        if not account_session or not account_session.connected:
            raise Exception(f"Account {trade.account_id} not connected")
        
        import MetaTrader5 as mt5
        
        # Create trade request
        symbol_info = mt5.symbol_info(trade.symbol)
        if symbol_info is None:
            raise Exception(f"Symbol {trade.symbol} not found")
        
        # Determine order type
        order_type = mt5.ORDER_TYPE_BUY if trade.trade_type.lower() == "buy" else mt5.ORDER_TYPE_SELL
        
        # Get current price
        tick = mt5.symbol_info_tick(trade.symbol)
        if tick is None:
            raise Exception(f"Cannot get price for {trade.symbol}")
        
        price = tick.ask if order_type == mt5.ORDER_TYPE_BUY else tick.bid
        
        # Build request
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": trade.symbol,
            "volume": trade.lot_size,
            "type": order_type,
            "price": price,
            "sl": trade.stop_loss,
            "tp": trade.take_profit,
            "comment": "Manual trade from frontend",
            "type_filling": mt5.ORDER_FILLING_IOC,
            "type_time": mt5.ORDER_TIME_GTC,
        }
        
        # Send order
        result = mt5.order_send(request)
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            raise Exception(f"Trade failed: {result.comment}")
        
        # Log trade
        trade_data = {
            "account_id": trade.account_id,
            "symbol": trade.symbol,
            "type": trade.trade_type,
            "lot": trade.lot_size,
            "entry_price": price,
            "stop_loss": trade.stop_loss,
            "take_profit": trade.take_profit,
            "ticket": result.order,
            "timestamp": "now()"
        }
        
        supabase_client.table("trades").insert(trade_data).execute()
        
        # Broadcast trade execution to all connected clients
        await ws_manager.broadcast({
            "type": "trade_executed",
            "trade": trade_data
        })
        
        return {
            "success": True,
            "message": f"Trade executed: {trade.trade_type.upper()} {trade.lot_size} {trade.symbol}",
            "ticket": result.order
        }
        
    except Exception as e:
        logger.error(f"Trade execution error: {e}")
        # Broadcast error to all connected clients
        await ws_manager.broadcast({
            "type": "trade_error",
            "error": str(e)
        })
        raise HTTPException(status_code=400, detail=str(e))
