"""
API endpoints for watchlist management with auto-trading integration
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from backend.config import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/watchlist", tags=["watchlist"])

# Initialize Supabase client — use service_role key to bypass RLS
from supabase import create_client
_sb_key = settings.SUPABASE_SERVICE_KEY or settings.SUPABASE_KEY
supabase = create_client(settings.SUPABASE_URL, _sb_key)


class WatchlistItem(BaseModel):
    symbol: str
    brick_size: float = 1.0
    lot_size: float = 0.01
    algo_enabled: bool = False
    stop_loss_pips: float = 50
    take_profit_pips: float = 100
    trailing_stop_pips: float = 30
    use_trailing_stop: bool = False


@router.get("/")
async def get_watchlist(account_id: int = Query(...)):
    """
    Get watchlist for an account
    
    Args:
        account_id: MT5 account ID
    
    Returns:
        List of watchlist items
    """
    try:
        response = supabase.table('watchlist').select('*').eq('account_id', account_id).execute()
        
        return {
            "status": "success",
            "account_id": account_id,
            "symbols": response.data if response.data else [],
            "count": len(response.data) if response.data else 0
        }
    except Exception as e:
        logger.error(f"Error fetching watchlist: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/")
async def add_to_watchlist(item: WatchlistItem, account_id: int = Query(...)):
    """
    Add symbol to watchlist and enable auto-trading
    
    Auto-trading will start within 30 seconds once algo_enabled=true
    
    Args:
        account_id: MT5 account ID
        item: WatchlistItem with symbol and settings
    
    Returns:
        Success status and added item
    """
    try:
        # Check if already exists
        existing = supabase.table('watchlist').select('*').eq('account_id', account_id).eq('symbol', item.symbol).execute()
        
        if existing.data and len(existing.data) > 0:
            # Update existing
            response = supabase.table('watchlist').update({
                'brick_size': item.brick_size,
                'lot_size': item.lot_size,
                'algo_enabled': item.algo_enabled,
                'stop_loss_pips': item.stop_loss_pips,
                'take_profit_pips': item.take_profit_pips,
                'updated_at': 'NOW()'
            }).eq('account_id', account_id).eq('symbol', item.symbol).execute()
            
            logger.info(f"Updated {item.symbol} in watchlist for account {account_id}")
        else:
            # Insert new
            response = supabase.table('watchlist').insert({
                'account_id': account_id,
                'symbol': item.symbol,
                'brick_size': item.brick_size,
                'lot_size': item.lot_size,
                'algo_enabled': item.algo_enabled,
                'stop_loss_pips': item.stop_loss_pips,
                'take_profit_pips': item.take_profit_pips,
                'is_active': True
            }).execute()
            
            logger.info(f"Added {item.symbol} to watchlist for account {account_id}")
        
        return {
            "status": "success",
            "message": f"Symbol {item.symbol} added/updated in watchlist",
            "symbol": item.symbol,
            "brick_size": item.brick_size,
            "algo_enabled": item.algo_enabled,
            "note": "Auto-trading will start within 30 seconds if algo_enabled=true"
        }
    
    except Exception as e:
        logger.error(f"Error adding to watchlist: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{symbol}")
async def update_watchlist_item(symbol: str, item: WatchlistItem, account_id: int = Query(...)):
    """
    Update all settings for a watchlist symbol (called from UI Edit form).
    Changes take effect immediately in the auto-trader.
    """
    try:
        response = supabase.table('watchlist').update({
            'brick_size': item.brick_size,
            'lot_size': item.lot_size,
            'algo_enabled': item.algo_enabled,
            'stop_loss_pips': item.stop_loss_pips,
            'take_profit_pips': item.take_profit_pips,
            'trailing_stop_pips': item.trailing_stop_pips,
            'use_trailing_stop': item.use_trailing_stop,
            'updated_at': 'NOW()'
        }).eq('account_id', account_id).eq('symbol', symbol).execute()

        logger.info(f"Updated watchlist for {symbol} (account {account_id}): brick_size={item.brick_size}, lot={item.lot_size}")

        # Immediately reload auto-trader so new brick_size takes effect without waiting 30s
        try:
            from backend.services.auto_trader import auto_trader as _at
            if _at:
                import asyncio
                asyncio.create_task(_at.load_watchlist())
                logger.info(f"🔄 Auto-trader reload triggered for {symbol} brick_size={item.brick_size}")
        except Exception as e:
            logger.warning(f"Auto-trader reload skipped: {e}")

        return {
            "status": "success",
            "symbol": symbol,
            "brick_size": item.brick_size,
            "lot_size": item.lot_size,
            "algo_enabled": item.algo_enabled,
            "message": f"Watchlist updated. Auto-trader reloaded with brick_size={item.brick_size}"
        }
    except Exception as e:
        logger.error(f"Error updating watchlist item {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{symbol}/algo")
async def toggle_algo(symbol: str, algo_enabled: bool = Query(...), account_id: int = Query(...)):
    """
    Enable/disable auto-trading for a symbol
    
    Args:
        symbol: Trading symbol
        algo_enabled: Enable or disable auto-trading
        account_id: MT5 account ID
    
    Returns:
        Updated status
    """
    try:
        response = supabase.table('watchlist').update({
            'algo_enabled': algo_enabled,
            'updated_at': 'NOW()'
        }).eq('account_id', account_id).eq('symbol', symbol).execute()
        
        action = "enabled" if algo_enabled else "disabled"
        logger.info(f"Auto-trading {action} for {symbol}")
        
        return {
            "status": "success",
            "symbol": symbol,
            "algo_enabled": algo_enabled,
            "message": f"Auto-trading {action} for {symbol}"
        }
    
    except Exception as e:
        logger.error(f"Error updating algo status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{symbol}/brick-size")
async def update_brick_size(symbol: str, brick_size: float = Query(...), account_id: int = Query(...)):
    """
    Update brick size for a symbol
    
    Changes take effect within 30 seconds
    
    Args:
        symbol: Trading symbol
        brick_size: New brick size
        account_id: MT5 account ID
    
    Returns:
        Updated status
    """
    try:
        response = supabase.table('watchlist').update({
            'brick_size': brick_size,
            'updated_at': 'NOW()'
        }).eq('account_id', account_id).eq('symbol', symbol).execute()
        
        logger.info(f"Updated brick size for {symbol} to {brick_size}")
        
        return {
            "status": "success",
            "symbol": symbol,
            "brick_size": brick_size,
            "message": f"Brick size updated to {brick_size}"
        }
    
    except Exception as e:
        logger.error(f"Error updating brick size: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{symbol}")
async def remove_from_watchlist(symbol: str, account_id: int = Query(...)):
    """
    Remove symbol from watchlist and stop auto-trading
    
    Args:
        symbol: Trading symbol
        account_id: MT5 account ID
    
    Returns:
        Success status
    """
    try:
        logger.info(f"DEBUG: Deleting {symbol} for account {account_id}")
        
        response = supabase.table('watchlist').delete().eq('account_id', account_id).eq('symbol', symbol).execute()
        
        logger.info(f"DEBUG: Delete response: {response}")
        logger.info(f"Removed {symbol} from watchlist for account {account_id}")
        
        return {
            "status": "success",
            "symbol": symbol,
            "message": f"Symbol {symbol} removed from watchlist"
        }
    
    except Exception as e:
        logger.error(f"Error removing from watchlist: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}")
async def get_watchlist_item(symbol: str, account_id: int = Query(...)):
    """
    Get specific watchlist item
    
    Args:
        symbol: Trading symbol
        account_id: MT5 account ID
    
    Returns:
        Watchlist item details
    """
    try:
        response = supabase.table('watchlist').select('*').eq('account_id', account_id).eq('symbol', symbol).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found in watchlist")
        
        return {
            "status": "success",
            "item": response.data[0]
        }
    
    except Exception as e:
        logger.error(f"Error fetching watchlist item: {e}")
        raise HTTPException(status_code=500, detail=str(e))
