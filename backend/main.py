import asyncio
import logging
import time
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
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

# Add CORS middleware — restrict to known frontend origins only
_ALLOWED_ORIGINS = [
    "https://renkomt5.netlify.app",  # Netlify frontend
    "https://api.turnends.win",       # Cloudflare Tunnel (same-origin API calls)
    "http://localhost:5173",          # Local dev (Vite default port)
    "http://localhost:3000",          # Local dev (alternate port)
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
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
        # Load ACTIVE and PENDING accounts from Supabase DB into mt5_manager.sessions
        try:
            response = supabase_client.table("accounts").select("*").in_("status", ["active", "pending"]).execute()
            if response.data:
                for account in response.data:
                    if account["login"] not in mt5_manager.sessions:
                        password = account.get("password", settings.MT5_PASSWORD)
                        server = account.get("server", settings.MT5_SERVER)
                        mt5_manager.add_account(account["login"], password, server)
                        logger.info(f"Loaded account {account['login']} (status={account.get('status')}) from database")
                logger.info(f"Loaded {len(response.data)} accounts from database")
        except Exception as e:
            logger.warning(f"Could not load accounts from Supabase: {e}")

        # Try to add the default env-var account too
        if settings.MT5_LOGIN and settings.MT5_PASSWORD and settings.MT5_SERVER:
            if settings.MT5_LOGIN not in mt5_manager.sessions:
                mt5_manager.add_account(settings.MT5_LOGIN, settings.MT5_PASSWORD, settings.MT5_SERVER)
                logger.info(f"Added default account {settings.MT5_LOGIN} from environment")

        # Connect MT5 in background, then update DB status and reload auto-trader watchlist.
        if mt5_manager.sessions:
            logger.info(f"Starting MT5 connection for {len(mt5_manager.sessions)} account(s) in background...")
            loop = asyncio.get_event_loop()

            async def connect_then_sync():
                await loop.run_in_executor(None, lambda: mt5_manager.connect_all(max_retries=3))
                for login, session in mt5_manager.sessions.items():
                    try:
                        if getattr(session, 'connected', False):
                            supabase_client.table('accounts').update({'status': 'active'}).eq('login', login).execute()
                            logger.info(f"Account {login} marked active in DB")
                        else:
                            logger.info(f"Account {login} did not connect — marking pending in DB")
                            try:
                                supabase_client.table('accounts').update({'status': 'pending'}).eq('login', login).execute()
                            except Exception as _upd_err:
                                logger.warning(f"Could not mark {login} pending: {_upd_err}")
                    except Exception as db_err:
                        logger.warning(f"Could not update account {login} status: {db_err}")
                try:
                    from backend.services.auto_trader import get_auto_trader_instance
                    instance = get_auto_trader_instance()
                    if instance and instance.is_running:
                        await instance.load_watchlist()
                        logger.info("Auto-trader watchlist reloaded after MT5 connect")
                except Exception as reload_err:
                    logger.warning(f"Could not reload watchlist after MT5 connect: {reload_err}")

            asyncio.ensure_future(connect_then_sync())

        # Start auto-trading service in background (auto_trader.start() waits 8s for MT5 to connect)
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

    from backend.services.auto_trader import auto_trader as _auto_trader
    auto_trader_running = _auto_trader.is_running if _auto_trader else False
    auto_trader_symbols = list(_auto_trader.enabled_symbols.keys()) if _auto_trader else []

    return {
        "status": "ok",
        "active": auto_trader_running,
        "auto_trader_symbols": auto_trader_symbols,
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

@app.websocket("/ws/live")
async def websocket_live_data(websocket: WebSocket):
    """Real-time quotes + positions streaming — tick by tick, 10x per second"""
    await websocket.accept()
    import MetaTrader5 as mt5_module
    symbols = []
    account_id = None
    try:
        # First message must contain subscription info
        try:
            msg = await asyncio.wait_for(websocket.receive_json(), timeout=10.0)
            symbols = msg.get("symbols", [])
            account_id = msg.get("account_id", None)
        except (asyncio.TimeoutError, Exception):
            pass

        # Ensure all subscribed symbols are in MT5 Market Watch so ticks arrive.
        # Build a map: requested name → resolved MT5 name (handles XM '#' suffix, etc.)
        symbol_map: dict = {}  # {requested: resolved}
        if symbols:
            def _select_symbols():
                for sym in symbols:
                    # Try exact name first
                    if mt5_module.symbol_select(sym, True) and mt5_module.symbol_info_tick(sym):
                        symbol_map[sym] = sym
                        continue
                    # Try '#' suffix (XM broker convention for CFD/crypto)
                    hashed = sym + "#"
                    if mt5_module.symbol_select(hashed, True) and mt5_module.symbol_info_tick(hashed):
                        symbol_map[sym] = hashed
                        logger.info(f"ws/live: resolved {sym} → {hashed}")
                        continue
                    # Try other common suffixes — includes .i# for XM precious metals (e.g. GOLD.i#)
                    for suffix in [".i#", ".", "+", "m"]:
                        candidate = sym + suffix
                        if mt5_module.symbol_select(candidate, True) and mt5_module.symbol_info_tick(candidate):
                            symbol_map[sym] = candidate
                            logger.info(f"ws/live: resolved {sym} → {candidate}")
                            break
                    else:
                        symbol_map[sym] = sym  # keep original as fallback
            import asyncio as _aio
            loop = _aio.get_event_loop()
            await loop.run_in_executor(None, _select_symbols)

        _mt5_ok = True
        _mt5_retry_at = 0.0

        while True:
            update: dict = {}
            now = time.time()

            # Switch to the requested account — but only retry MT5 every 5s when it's down
            if account_id:
                session = mt5_manager.get_session(int(account_id))
                if session and (_mt5_ok or now >= _mt5_retry_at):
                    try:
                        session.switch_to()
                        _mt5_ok = True
                    except Exception as sw_err:
                        if _mt5_ok:  # only log on first failure, not every tick
                            logger.warning(f"ws/live switch to {account_id} failed: {sw_err}")
                        _mt5_ok = False
                        _mt5_retry_at = now + 5.0  # retry in 5 seconds

            # Account balance/equity for the selected account
            if account_id and _mt5_ok:
                try:
                    acct_info = mt5_module.account_info()
                    if acct_info is not None:
                        update["account"] = {
                            "login": acct_info.login,
                            "balance": round(float(acct_info.balance), 2),
                            "equity": round(float(acct_info.equity), 2),
                            "margin": round(float(acct_info.margin), 2),
                            "free_margin": round(float(acct_info.margin_free), 2),
                        }
                except Exception:
                    pass

            # Live quotes for subscribed symbols
            if symbols:
                quotes = {}
                for sym in symbols:
                    resolved = symbol_map.get(sym, sym)
                    tick = mt5_module.symbol_info_tick(resolved)
                    if tick:
                        # Key quote by original name so frontend can match it
                        quotes[sym] = {
                            "bid": float(tick.bid),
                            "ask": float(tick.ask),
                            "time": int(tick.time),
                        }
                update["quotes"] = quotes

            # Live positions (current MT5 account) — positions is a numpy array, must use `is not None`
            positions = mt5_module.positions_get()
            pos_iter = positions if positions is not None else []
            update["positions"] = [
                {
                    "ticket": p.ticket,
                    "symbol": p.symbol,
                    "type": "buy" if p.type == 0 else "sell",
                    "volume": p.volume,
                    "open_price": p.price_open,
                    "current_price": p.price_current,
                    "sl": p.sl,
                    "tp": p.tp,
                    "profit": round(p.profit, 2),
                    "swap": round(p.swap, 2),
                    "open_time": p.time,
                }
                for p in pos_iter
            ]

            await websocket.send_json(update)
            await asyncio.sleep(0.1)  # 100ms = 10 updates per second

    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"Live WebSocket error: {e}")




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

        # Switch MT5 to the correct account before any symbol/price calls
        try:
            account_session.switch_to()
        except Exception as sw_err:
            raise Exception(f"Cannot switch to account {trade.account_id}: {sw_err}")

        # Broker suffix aliases — XM uses GOLD#, ETHUSD#, BTCUSD# etc.
        _SUFFIXES = ["", "#", ".", "m", "+"]
        resolved_symbol = None
        symbol_info = None
        for sfx in _SUFFIXES:
            candidate = trade.symbol + sfx
            if mt5.symbol_select(candidate, True):
                info = mt5.symbol_info(candidate)
                if info is not None:
                    resolved_symbol = candidate
                    symbol_info = info
                    break

        if symbol_info is None:
            err = mt5.last_error()
            raise Exception(
                f"Symbol {trade.symbol} not found in MT5 (tried suffixes {_SUFFIXES}). "
                f"MT5 error: {err}. Check symbol name matches the broker's Market Watch."
            )

        logger.info(f"Trade: resolved {trade.symbol!r} -> {resolved_symbol!r}")
        # Use the broker-resolved symbol name for the actual request
        trade_symbol = resolved_symbol
        
        # Validate lot size
        if trade.lot_size < symbol_info.volume_min:
            raise Exception(f"Lot size {trade.lot_size} is below minimum {symbol_info.volume_min}")
        if trade.lot_size > symbol_info.volume_max:
            raise Exception(f"Lot size {trade.lot_size} exceeds maximum {symbol_info.volume_max}")
        
        # Determine order type
        order_type = mt5.ORDER_TYPE_BUY if trade.trade_type.lower() == "buy" else mt5.ORDER_TYPE_SELL
        
        # Get current price
        tick = mt5.symbol_info_tick(trade_symbol)
        if tick is None:
            raise Exception(f"Cannot get price for {trade_symbol}")
        
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
            "symbol": trade_symbol,
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
