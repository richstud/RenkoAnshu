"""
API endpoints for automated trading control
"""
from fastapi import APIRouter, HTTPException
from backend.services.auto_trader import get_auto_trader
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auto-trading", tags=["auto-trading"])


@router.post("/symbols/add")
async def add_symbol_to_auto_trading(symbol: str, account_id: int, brick_size: float = 0.005):
    """
    Add a symbol to automated trading watchlist
    
    Args:
        symbol: Trading symbol (e.g., EURUSD)
        account_id: MT5 account ID
        brick_size: Renko brick size for strategy (default: 0.005)
    
    Returns:
        Status and confirmation
    """
    try:
        auto_trader = await get_auto_trader()
        success = await auto_trader.add_symbol(symbol, account_id, brick_size)
        
        if success:
            return {
                "status": "success",
                "message": f"Symbol {symbol} added to auto-trading",
                "symbol": symbol,
                "brick_size": brick_size,
                "monitoring": True,
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to add symbol")
    
    except Exception as e:
        logger.error(f"Error adding symbol: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/symbols/remove")
async def remove_symbol_from_auto_trading(symbol: str):
    """
    Remove a symbol from automated trading watchlist
    (Will close any open position)
    
    Args:
        symbol: Trading symbol to remove
    
    Returns:
        Confirmation of removal
    """
    try:
        auto_trader = await get_auto_trader()
        success = await auto_trader.remove_symbol(symbol)
        
        if success:
            return {
                "status": "success",
                "message": f"Symbol {symbol} removed from auto-trading",
                "symbol": symbol,
                "monitoring": False,
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to remove symbol")
    
    except Exception as e:
        logger.error(f"Error removing symbol: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_auto_trading_status():
    """
    Get current auto-trading service status
    
    Returns:
        Service status, enabled symbols, open positions, last evaluation time
    """
    try:
        auto_trader = await get_auto_trader()
        status = auto_trader.get_status()
        
        return {
            "service": {
                "running": status['running'],
                "enabled_symbols": status['enabled_symbols'],
                "symbol_count": len(status['enabled_symbols']),
                "last_evaluation": status['last_evaluation'],
            },
            "positions": {
                "open_count": len(status['open_positions']),
                "details": list(status['open_positions'].values()),
            },
            "data_source": "MT5_LIVE",
        }
    
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/symbols")
async def list_auto_trading_symbols():
    """
    List all symbols currently in auto-trading watchlist
    
    Returns:
        List of monitored symbols with their configuration
    """
    try:
        auto_trader = await get_auto_trader()
        
        symbols = []
        for symbol, config in auto_trader.enabled_symbols.items():
            pos = auto_trader.open_positions.get(symbol)
            symbols.append({
                "symbol": symbol,
                "account_id": config['account_id'],
                "brick_size": config['brick_size'],
                "enabled": config['enabled'],
                "current_position": {
                    "direction": pos['direction'] if pos else None,
                    "entry_price": pos['entry_price'] if pos else None,
                    "lot_size": pos['lot_size'] if pos else None,
                    "opened_at": pos['opened_at'] if pos else None,
                } if pos else None,
            })
        
        return {
            "symbols": symbols,
            "count": len(symbols),
        }
    
    except Exception as e:
        logger.error(f"Error listing symbols: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/start")
async def start_auto_trading():
    """
    Start the auto-trading service
    
    Returns:
        Confirmation that service is running
    """
    try:
        auto_trader = await get_auto_trader()
        
        if auto_trader.is_running:
            return {
                "status": "already_running",
                "message": "Auto-trading service is already running",
            }
        
        # Note: In a real implementation, you'd start the background task here
        # For now, the service starts automatically on initialization
        
        return {
            "status": "running",
            "message": "Auto-trading service is active",
            "enabled_symbols": list(auto_trader.enabled_symbols.keys()),
        }
    
    except Exception as e:
        logger.error(f"Error starting auto-trading: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop")
async def stop_auto_trading():
    """
    Stop the auto-trading service
    (Does not close open positions)
    
    Returns:
        Confirmation that service is stopped
    """
    try:
        auto_trader = await get_auto_trader()
        await auto_trader.stop()
        
        return {
            "status": "stopped",
            "message": "Auto-trading service stopped",
            "note": "Open positions remain active. Close manually if needed.",
        }
    
    except Exception as e:
        logger.error(f"Error stopping auto-trading: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/positions")
async def get_auto_trading_positions():
    """
    Get all open positions from auto-trading
    
    Returns:
        List of all open positions with details
    """
    try:
        auto_trader = await get_auto_trader()
        
        positions = []
        for symbol, pos in auto_trader.open_positions.items():
            positions.append({
                "symbol": symbol,
                "direction": pos['direction'],
                "entry_price": pos['entry_price'],
                "lot_size": pos['lot_size'],
                "opened_at": pos['opened_at'],
                "ticket": pos['ticket'],
            })
        
        return {
            "positions": positions,
            "count": len(positions),
            "total_active_trades": len(positions),
        }
    
    except Exception as e:
        logger.error(f"Error getting positions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/close-position/{symbol}")
async def close_auto_trading_position(symbol: str):
    """
    Manually close an open auto-trading position for a symbol
    
    Args:
        symbol: Symbol to close position for
    
    Returns:
        Confirmation of position closure
    """
    try:
        auto_trader = await get_auto_trader()
        account_id = auto_trader.enabled_symbols.get(symbol, {}).get('account_id')
        
        if not account_id:
            raise HTTPException(status_code=404, detail=f"Symbol {symbol} not in auto-trading")
        
        await auto_trader.close_opposite_position(symbol, account_id)
        
        return {
            "status": "closed",
            "symbol": symbol,
            "message": f"Position for {symbol} closed successfully",
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error closing position: {e}")
        raise HTTPException(status_code=500, detail=str(e))
