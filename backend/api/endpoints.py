"""
API Endpoints for Renko Trading Bot
New endpoints for tickers, watchlist, and market data
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from backend.services.price_manager import price_manager
from backend.services.watchlist_manager import watchlist_manager
from backend.supabase.client import supabase_client

logger = logging.getLogger("endpoints")

router = APIRouter(prefix="/api", tags=["Trading"])


# ===================================
# PYDANTIC MODELS
# ===================================

class Quote(BaseModel):
    symbol: str
    bid: float
    ask: float
    last_update: int


class WatchlistItem(BaseModel):
    account_id: int
    symbol: str
    lot_size: float = 0.01
    stop_loss_pips: float = 50
    take_profit_pips: float = 100
    trailing_stop_pips: float = 30
    use_trailing_stop: bool = False
    brick_size: float = 1.0
    algo_enabled: bool = True


class WatchlistUpdate(BaseModel):
    lot_size: Optional[float] = None
    stop_loss_pips: Optional[float] = None
    take_profit_pips: Optional[float] = None
    trailing_stop_pips: Optional[float] = None
    use_trailing_stop: Optional[bool] = None
    brick_size: Optional[float] = None
    algo_enabled: Optional[bool] = None


class AlgoToggle(BaseModel):
    account_id: int
    enabled: bool


# ===================================
# TICKER ENDPOINTS
# ===================================

@router.get("/tickers")
async def get_tickers():
    """Get all available tickers that exist in MT5"""
    try:
        import MetaTrader5 as mt5
        
        symbols = supabase_client.table('available_symbols').select('*').eq('is_active', True).execute()
        
        # Filter to only symbols available in MT5
        available = []
        for symbol_data in symbols.data:
            symbol = symbol_data['symbol']
            try:
                # Check if symbol exists in MT5
                symbol_info = mt5.symbol_info(symbol)
                if symbol_info is not None:
                    available.append(symbol_data)
                    logger.info(f"✅ Symbol {symbol} available in MT5")
                else:
                    logger.warning(f"⚠️ Symbol {symbol} not found in MT5 - skipping from frontend list")
            except Exception as e:
                logger.warning(f"Error checking symbol {symbol}: {e}")
        
        return {
            "count": len(available),
            "total": len(symbols.data),
            "unavailable": len(symbols.data) - len(available),
            "data": available
        }
    except Exception as e:
        logger.error(f"Error getting tickers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tickers/{symbol}/quote")
async def get_ticker_quote(symbol: str):
    """Get current bid/ask for a symbol"""
    try:
        quote = price_manager.get_quote(symbol)
        if not quote:
            raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found or no quote data")
        return quote
    except Exception as e:
        logger.error(f"Error getting quote for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/market/quote/{symbol}")
async def get_market_quote(symbol: str):
    """Get live market quote for symbol"""
    return await get_ticker_quote(symbol)


@router.get("/market/symbols")
async def get_market_symbols():
    """Get all available symbols"""
    try:
        symbols = price_manager.get_all_symbols()
        return {
            "count": len(symbols),
            "symbols": symbols
        }
    except Exception as e:
        logger.error(f"Error getting symbols: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===================================
# WATCHLIST ENDPOINTS
# ===================================

@router.post("/watchlist")
async def add_to_watchlist(item: WatchlistItem):
    """Add symbol to watchlist"""
    try:
        result = watchlist_manager.add_to_watchlist(
            account_id=item.account_id,
            symbol=item.symbol,
            lot_size=item.lot_size,
            stop_loss_pips=item.stop_loss_pips,
            take_profit_pips=item.take_profit_pips,
            trailing_stop_pips=item.trailing_stop_pips,
            use_trailing_stop=item.use_trailing_stop,
            brick_size=item.brick_size,
            algo_enabled=item.algo_enabled
        )
        
        if not result:
            raise HTTPException(status_code=400, detail="Failed to add to watchlist")
        
        return {
            "message": f"Added {item.symbol} to watchlist",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error adding to watchlist: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/watchlist")
async def get_watchlist(account_id: int):
    """Get watchlist for account"""
    try:
        watchlist = watchlist_manager.get_watchlist(account_id)
        return {
            "account_id": account_id,
            "count": len(watchlist),
            "data": watchlist
        }
    except Exception as e:
        logger.error(f"Error getting watchlist: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/watchlist/{item_id}")
async def get_watchlist_item(item_id: int):
    """Get specific watchlist item"""
    try:
        item = watchlist_manager.get_watchlist_item(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Watchlist item not found")
        return item
    except Exception as e:
        logger.error(f"Error getting watchlist item: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/watchlist/{item_id}")
async def update_watchlist_item(item_id: int, updates: WatchlistUpdate):
    """Update watchlist item (SL, TP, Trail, Brick Size)"""
    try:
        # Convert to dict and remove None values
        update_dict = {k: v for k, v in updates.dict().items() if v is not None}
        
        result = watchlist_manager.update_watchlist_item(item_id, **update_dict)
        
        if not result:
            raise HTTPException(status_code=404, detail="Watchlist item not found")
        
        return {
            "message": "Watchlist item updated",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error updating watchlist: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/watchlist/{item_id}")
async def remove_from_watchlist(item_id: int):
    """Remove item from watchlist"""
    try:
        success = watchlist_manager.remove_from_watchlist(item_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Watchlist item not found")
        
        return {
            "message": "Removed from watchlist"
        }
    except Exception as e:
        logger.error(f"Error removing from watchlist: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===================================
# ALGORITHM CONTROL ENDPOINTS
# ===================================

@router.post("/algo/toggle/{item_id}")
async def toggle_algo(item_id: int, toggle: AlgoToggle):
    """Toggle algorithm on/off for symbol"""
    try:
        result = watchlist_manager.toggle_algo(item_id, toggle.enabled)
        
        if not result:
            raise HTTPException(status_code=404, detail="Watchlist item not found")
        
        status = "enabled" if toggle.enabled else "disabled"
        return {
            "message": f"Algorithm {status}",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error toggling algo: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/algo/status/{account_id}/{symbol}")
async def get_algo_status(account_id: int, symbol: str):
    """Get algo status for symbol"""
    try:
        settings = watchlist_manager.get_symbol_settings(account_id, symbol)
        
        if not settings:
            return {
                "symbol": symbol,
                "account_id": account_id,
                "algo_enabled": False,
                "message": "Symbol not in watchlist"
            }
        
        return {
            "symbol": symbol,
            "account_id": account_id,
            "algo_enabled": settings.get("algo_enabled", False),
            "stop_loss_pips": settings.get("stop_loss_pips"),
            "take_profit_pips": settings.get("take_profit_pips"),
            "trailing_stop_pips": settings.get("trailing_stop_pips"),
            "brick_size": settings.get("brick_size")
        }
    except Exception as e:
        logger.error(f"Error getting algo status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===================================
# SETTINGS ENDPOINTS
# ===================================

@router.get("/settings")
async def get_all_settings():
    """Get all global settings"""
    try:
        result = supabase_client.table('settings').select('*').execute()
        return {
            "count": len(result.data),
            "data": result.data
        }
    except Exception as e:
        logger.error(f"Error getting settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/settings/{setting_key}")
async def get_setting(setting_key: str):
    """Get specific setting"""
    try:
        result = supabase_client.table('settings').select('*').eq('setting_key', setting_key).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail=f"Setting {setting_key} not found")
        return result.data[0]
    except Exception as e:
        logger.error(f"Error getting setting: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/settings/{setting_key}")
async def update_setting(setting_key: str, setting_value: str):
    """Update a setting"""
    try:
        result = supabase_client.table('settings').update({
            'setting_value': setting_value
        }).eq('setting_key', setting_key).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail=f"Setting {setting_key} not found")
        
        return {
            "message": f"Updated {setting_key}",
            "data": result.data[0]
        }
    except Exception as e:
        logger.error(f"Error updating setting: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===================================
# ACCOUNTS ENDPOINTS
# ===================================

@router.get("/accounts")
async def get_accounts():
    """Get all trading accounts"""
    try:
        result = supabase_client.table('accounts').select('*').execute()
        return {
            "count": len(result.data),
            "data": result.data
        }
    except Exception as e:
        logger.error(f"Error getting accounts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/accounts/{login}")
async def get_account(login: int):
    """Get specific account details"""
    try:
        result = supabase_client.table('accounts').select('*').eq('login', login).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail=f"Account {login} not found")
        return result.data[0]
    except Exception as e:
        logger.error(f"Error getting account: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===================================
# TRADES ENDPOINTS
# ===================================

@router.get("/trades")
async def get_trades(account_id: int = None, closed: bool = None):
    """Get trades (optionally filtered by account and status)"""
    try:
        query = supabase_client.table('trades').select('*')
        
        if account_id:
            query = query.eq('account_id', account_id)
        
        if closed is not None:
            query = query.eq('closed', closed)
        
        result = query.order('created_at', desc=True).execute()
        return {
            "count": len(result.data),
            "data": result.data
        }
    except Exception as e:
        logger.error(f"Error getting trades: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trades/{trade_id}")
async def get_trade(trade_id: int):
    """Get specific trade details"""
    try:
        result = supabase_client.table('trades').select('*').eq('id', trade_id).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail=f"Trade {trade_id} not found")
        return result.data[0]
    except Exception as e:
        logger.error(f"Error getting trade: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trades/by-date/{account_id}")
async def get_trades_by_date(account_id: int, date_str: str = Query(...), closed: bool = None):
    """
    Get trades for a specific date and account
    
    Args:
        account_id: MT5 account ID
        date_str: Date in format YYYY-MM-DD (e.g., '2026-04-13')
        closed: Optional filter for trade status (true for closed, false for open)
    
    Returns:
        List of trades for the specified date
    """
    try:
        from datetime import datetime, timedelta
        
        # Parse the date
        target_date = datetime.strptime(date_str, '%Y-%m-%d')
        start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        end_of_day = (target_date + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        
        # Query trades
        query = supabase_client.table('trades').select('*').eq('account_id', account_id)
        query = query.gte('created_at', start_of_day).lt('created_at', end_of_day)
        
        if closed is not None:
            query = query.eq('closed', closed)
        
        result = query.order('created_at', desc=True).execute()
        
        return {
            "account_id": account_id,
            "date": date_str,
            "count": len(result.data),
            "data": result.data
        }
    except ValueError as e:
        logger.error(f"Invalid date format: {e}")
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        logger.error(f"Error getting trades by date: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class TradeCreate(BaseModel):
    account_id: int
    symbol: str
    type: str  # 'buy' or 'sell'
    lot: float
    entry_price: float
    sl_price: float = None
    tp_price: float = None
    brick_size: float = 1.0


@router.post("/trades")
async def create_trade(trade: TradeCreate):
    """Create a new trade"""
    try:
        data = {
            "account_id": trade.account_id,
            "symbol": trade.symbol,
            "type": trade.type,
            "lot": trade.lot,
            "entry_price": trade.entry_price,
            "sl_price": trade.sl_price,
            "tp_price": trade.tp_price,
            "brick_size": trade.brick_size,
            "closed": False
        }
        
        result = supabase_client.table('trades').insert(data).execute()
        
        if result.data:
            logger.info(f"Created trade: {trade.symbol} {trade.type} @ {trade.entry_price}")
            return {
                "message": "Trade created successfully",
                "data": result.data[0]
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to create trade")
    except Exception as e:
        logger.error(f"Error creating trade: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trades/export/{account_id}")
async def export_trades(account_id: int, date_str: str = Query(...)):
    """
    Export trades for a specific date to CSV format
    
    Args:
        account_id: MT5 account ID
        date_str: Date in format YYYY-MM-DD (e.g., '2026-04-13')
    
    Returns:
        CSV data as downloadable file
    """
    try:
        from datetime import datetime, timedelta
        from io import StringIO
        from fastapi.responses import StreamingResponse
        import csv
        
        # Parse the date
        target_date = datetime.strptime(date_str, '%Y-%m-%d')
        start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        end_of_day = (target_date + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        
        # Query trades
        query = supabase_client.table('trades').select('*').eq('account_id', account_id)
        query = query.gte('created_at', start_of_day).lt('created_at', end_of_day)
        result = query.order('created_at', desc=True).execute()
        
        # Create CSV
        output = StringIO()
        if result.data:
            fieldnames = ['ID', 'Symbol', 'Type', 'Lot', 'Entry Price', 'SL Price', 'TP Price', 'Status', 'Created At', 'Brick Size']
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            
            for trade in result.data:
                writer.writerow({
                    'ID': trade.get('id', ''),
                    'Symbol': trade.get('symbol', ''),
                    'Type': trade.get('type', '').upper(),
                    'Lot': trade.get('lot', ''),
                    'Entry Price': trade.get('entry_price', ''),
                    'SL Price': trade.get('sl_price', ''),
                    'TP Price': trade.get('tp_price', ''),
                    'Status': 'Closed' if trade.get('closed') else 'Open',
                    'Created At': trade.get('created_at', ''),
                    'Brick Size': trade.get('brick_size', '')
                })
        else:
            fieldnames = ['ID', 'Symbol', 'Type', 'Lot', 'Entry Price', 'SL Price', 'TP Price', 'Status', 'Created At', 'Brick Size']
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
        
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment;filename=trades_{date_str}_{account_id}.csv"}
        )
    except ValueError as e:
        logger.error(f"Invalid date format: {e}")
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        logger.error(f"Error exporting trades: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===================================
# BOT CONTROL ENDPOINTS
# ===================================

@router.post("/start-bot")
async def start_bot(account_id: int = 101510620):
    """Start the trading bot"""
    try:
        # Check if bot control record exists
        result = supabase_client.table('bot_control').select('*').eq('account_id', account_id).execute()
        
        if result.data:
            # Update existing record
            update_result = supabase_client.table('bot_control').update({
                'is_running': True
            }).eq('account_id', account_id).execute()
            return {
                "message": "Bot started",
                "is_running": True,
                "account_id": account_id
            }
        else:
            # Create new record
            insert_result = supabase_client.table('bot_control').insert({
                'account_id': account_id,
                'is_running': True
            }).execute()
            return {
                "message": "Bot started",
                "is_running": True,
                "account_id": account_id
            }
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop-bot")
async def stop_bot(account_id: int = 101510620):
    """Stop the trading bot"""
    try:
        update_result = supabase_client.table('bot_control').update({
            'is_running': False
        }).eq('account_id', account_id).execute()
        
        return {
            "message": "Bot stopped",
            "is_running": False,
            "account_id": account_id
        }
    except Exception as e:
        logger.error(f"Error stopping bot: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update-settings")
async def update_global_settings(data: dict):
    """Update global bot settings"""
    try:
        updates = []
        for key, value in data.items():
            result = supabase_client.table('settings').update({
                'setting_value': str(value)
            }).eq('setting_key', f'default_{key}' if not key.startswith('default_') else key).execute()
            updates.append(result.data[0] if result.data else None)
        
        return {
            "message": "Settings updated",
            "data": updates
        }
    except Exception as e:
        logger.error(f"Error updating settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===================================
# TRADE AUTO-CLEANUP ENDPOINTS
# ===================================

@router.post("/trades/auto-cleanup")
async def auto_cleanup_trades(account_id: int = Query(...)):
    """
    Auto-cleanup old trades:
    - Delete trades older than 2 days
    - Keep only today and yesterday
    """
    try:
        from datetime import datetime, timedelta
        
        today = datetime.now().date()
        two_days_ago = (today - timedelta(days=2)).isoformat()
        
        logger.info(f"Starting cleanup for account {account_id}, removing trades before {two_days_ago}")
        
        # Get trades older than 2 days
        old_trades_query = supabase_client.table('trades').select('id').eq('account_id', account_id).lt('created_at', two_days_ago)
        old_trades = old_trades_query.execute()
        
        deleted_count = 0
        if old_trades.data:
            for trade in old_trades.data:
                supabase_client.table('trades').delete().eq('id', trade['id']).execute()
                deleted_count += 1
                logger.info(f"Deleted old trade {trade['id']}")
        
        logger.info(f"Cleanup complete for account {account_id}, deleted {deleted_count} old trades")
        
        return {
            "status": "success",
            "message": f"Cleanup complete",
            "deleted_count": deleted_count,
            "account_id": account_id
        }
    except Exception as e:
        logger.error(f"Error in auto-cleanup: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trades/move-closed")
async def move_closed_trades(account_id: int = Query(...)):
    """Mark and report closed trades for archival to trade history"""
    try:
        # Get all closed trades from today and yesterday only
        from datetime import datetime, timedelta
        
        today = datetime.now().date()
        yesterday = (today - timedelta(days=1)).date()
        
        start_of_yesterday = yesterday.replace().isoformat() + "T00:00:00"
        end_of_today = (today + timedelta(days=1)).replace().isoformat() + "T00:00:00"
        
        # Query for closed trades from last 2 days
        closed_trades_query = supabase_client.table('trades').select('*').eq('account_id', account_id).eq('closed', True)
        closed_trades_query = closed_trades_query.gte('created_at', start_of_yesterday).lt('created_at', end_of_today)
        
        result = closed_trades_query.execute()
        
        logger.info(f"Found {len(result.data)} closed trades for account {account_id} in last 2 days")
        
        return {
            "status": "success",
            "message": f"Found {len(result.data)} closed trades ready for history",
            "count": len(result.data),
            "data": result.data if result.data else []
        }
    except Exception as e:
        logger.error(f"Error moving closed trades: {e}")
        raise HTTPException(status_code=500, detail=str(e))

