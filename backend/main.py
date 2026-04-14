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
from backend.api.renko_chart import router as renko_router
from backend.api.auto_trading import router as auto_trading_router
from backend.api.account_manager import router as account_manager_router
from backend.services.auto_trader import start_auto_trading, stop_auto_trading
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

# Include API routers
app.include_router(api_router)
app.include_router(renko_router)
app.include_router(auto_trading_router)
app.include_router(account_manager_router)

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
        # Load only ACTIVE accounts from Supabase DB into mt5_manager.sessions
        try:
            response = supabase_client.table("accounts").select("*").eq("status", "active").execute()
            if response.data:
                for account in response.data:
                    if account["login"] not in mt5_manager.sessions:
                        password = account.get("password", settings.MT5_PASSWORD)
                        server = account.get("server", settings.MT5_SERVER)
                        mt5_manager.add_account(account["login"], password, server)
                        logger.info(f"Loaded account {account['login']} from database")
                logger.info(f"Loaded {len(response.data)} active accounts from database")
        except Exception as e:
            logger.warning(f"Could not load accounts from Supabase: {e}")

        # Try to add the default env-var account too
        if settings.MT5_LOGIN and settings.MT5_PASSWORD and settings.MT5_SERVER:
            if settings.MT5_LOGIN not in mt5_manager.sessions:
                mt5_manager.add_account(settings.MT5_LOGIN, settings.MT5_PASSWORD, settings.MT5_SERVER)
                logger.info(f"Added default account {settings.MT5_LOGIN} from environment")

        # Connect MT5 accounts in a background thread so the HTTP server starts immediately
        if mt5_manager.sessions:
            logger.info(f"Starting MT5 connection for {len(mt5_manager.sessions)} account(s) in background...")
            loop = asyncio.get_event_loop()
            asyncio.create_task(
                loop.run_in_executor(None, lambda: mt5_manager.connect_all(max_retries=3))
            )
        
        # Start auto-trading service (after a short delay to let MT5 connect first)
        logger.info("Starting auto-trading service...")
        await start_auto_trading()
        
    except Exception as e:
        logger.error(f"Startup error: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    try:
        logger.info("Shutting down services...")
        await stop_auto_trading()
        logger.info("Auto-trading service stopped")
        
        # Disconnect all MT5 accounts and shutdown MT5 library
        logger.info("Disconnecting MT5 accounts...")
        mt5_manager.disconnect_all()
        logger.info("MT5 disconnected")
    except Exception as e:
        logger.error(f"Shutdown error: {e}")

@app.post("/api/start-bot")
async def start_bot():
    if bot_worker.active:
        return {"message": "Bot already running"}

    asyncio.create_task(run_worker())
    return {"message": "Bot started"}

@app.post("/api/stop-bot")
async def stop_bot():
    if not bot_worker.active:
        return {"message": "Bot is not running"}
    await bot_worker.stop()
    return {"message": "Bot stopped"}

@app.get("/api/signal/{symbol}/{price}")
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

@app.post("/api/reset-signal/{symbol}")
def reset_signal(symbol: str):
    """Reset signal generator for a symbol."""
    signal_generator.reset_symbol(symbol)
    return {"message": f"Signal generator reset for {symbol}"}

@app.post("/api/accounts")
def add_account(account: AccountPayload):
    mt5_manager.add_account(account.login, account.password, account.server)
    data = {
        "login": account.login,
        "server": account.server,
        "status": "added",
    }
    supabase_client.table("accounts").insert(data).execute()
    return {"message": "Account added"}

@app.get("/api/accounts")
def get_accounts():
    res = supabase_client.table("accounts").select("*").execute()
    return res.data

@app.get("/api/trades")
def get_trades():
    res = supabase_client.table("trades").select("*").execute()
    return res.data

@app.get("/api/logs")
def get_logs():
    res = supabase_client.table("logs").select("*").order("created_at", desc=True).limit(100).execute()
    return res.data

@app.post("/api/update-settings")
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
    try:
        await ws_manager.connect(websocket)
        logger.info(f"WebSocket connection accepted")
        
        # Send initial connection confirmation
        await ws_manager.send_personal(websocket, {"type": "connected", "message": "WebSocket connected successfully"})
        
        while True:
            try:
                # Keep connection alive and receive any messages from client
                data = await websocket.receive_text()
                if data == "ping":
                    await ws_manager.send_personal(websocket, {"type": "pong"})
            except Exception as recv_error:
                logger.debug(f"WebSocket receive error: {recv_error}")
                break
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}", exc_info=True)
        raise
    finally:
        ws_manager.disconnect(websocket)
        logger.info(f"WebSocket connection closed")


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


@app.post("/api/execute-trade")
async def execute_manual_trade(trade: TradeRequest):
    """Execute a manual trade from the frontend"""
    try:
        # Get the account session
        account_session = mt5_manager.get_session(trade.account_id)
        if not account_session:
            raise Exception(f"Account {trade.account_id} not registered")
        
        # If connection was lost, try to reconnect
        if not account_session.connected:
            logger.warning(f"Account {trade.account_id} disconnected, attempting reconnection...")
            account_session.connect()
            if not account_session.connected:
                raise Exception(f"Account {trade.account_id} not connected")
        
        import MetaTrader5 as mt5
        
        # Create trade request
        symbol_info = mt5.symbol_info(trade.symbol)
        if symbol_info is None:
            raise Exception(f"Symbol {trade.symbol} not found")
        
        # Validate lot size
        if trade.lot_size < symbol_info.volume_min:
            raise Exception(f"Lot size {trade.lot_size} is below minimum {symbol_info.volume_min}")
        if trade.lot_size > symbol_info.volume_max:
            raise Exception(f"Lot size {trade.lot_size} exceeds maximum {symbol_info.volume_max}")
        
        # Determine order type
        order_type = mt5.ORDER_TYPE_BUY if trade.trade_type.lower() == "buy" else mt5.ORDER_TYPE_SELL
        
        # Get current price
        tick = mt5.symbol_info_tick(trade.symbol)
        if tick is None:
            raise Exception(f"Cannot get price for {trade.symbol}")
        
        price = tick.ask if order_type == mt5.ORDER_TYPE_BUY else tick.bid
        
        # Calculate actual stop loss and take profit prices from pips
        if trade.stop_loss and trade.stop_loss > 0:
            # Convert pips to price levels
            pip_size = symbol_info.point * (10 if symbol_info.digits == 5 else 1)
            stop_loss_pips = trade.stop_loss
            if order_type == mt5.ORDER_TYPE_BUY:
                sl_price = price - (stop_loss_pips * pip_size)
            else:
                sl_price = price + (stop_loss_pips * pip_size)
        else:
            sl_price = None
            
        if trade.take_profit and trade.take_profit > 0:
            # Convert pips to price levels
            pip_size = symbol_info.point * (10 if symbol_info.digits == 5 else 1)
            tp_pips = trade.take_profit
            if order_type == mt5.ORDER_TYPE_BUY:
                tp_price = price + (tp_pips * pip_size)
            else:
                tp_price = price - (tp_pips * pip_size)
        else:
            tp_price = None
        
        # Build request - only include fields that have values
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": trade.symbol,
            "volume": trade.lot_size,
            "type": order_type,
            "price": price,
            "comment": "Manual trade from frontend",
            "type_filling": mt5.ORDER_FILLING_IOC,
            "type_time": mt5.ORDER_TIME_GTC,
        }
        
        # Add stop loss and take profit only if provided
        if sl_price:
            request["sl"] = round(sl_price, symbol_info.digits)
        if tp_price:
            request["tp"] = round(tp_price, symbol_info.digits)
        
        # Send order
        result = mt5.order_send(request)
        
        if result is None:
            error_info = mt5.last_error()
            raise Exception(f"Order send failed: {error_info}")
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            raise Exception(f"Trade failed: {result.comment}")
        
        # Broadcast trade execution result
        await ws_manager.broadcast({
            "type": "trade_executed",
            "status": "success",
            "trade_id": result.order,
            "symbol": trade.symbol,
            "trade_type": trade.trade_type,
            "lot_size": trade.lot_size,
            "price": price,
            "message": f"Trade executed: {trade.trade_type.upper()} {trade.lot_size} {trade.symbol} @ {price}"
        })
        
        # Log trade - only insert basic fields that exist
        try:
            trade_data = {
                "account_id": trade.account_id,
                "symbol": trade.symbol,
                "type": trade.trade_type,
                "lot": trade.lot_size,
                "entry_price": price,
            }
            
            supabase_client.table("trades").insert(trade_data).execute()
        except Exception as db_error:
            logger.warning(f"Could not log trade to database: {db_error}")
        
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
