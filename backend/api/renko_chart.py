"""
Real-time Renko Chart Endpoint
Provides Renko brick data for frontend charting - directly from MT5
"""
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from backend.renko.engine import RenkoEngine
from backend.strategy.engine import StrategyEngine
from backend.config import settings
from backend.mt5.connection import mt5_manager
import MetaTrader5 as mt5
from datetime import datetime
import logging
import json
import asyncio

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/renko", tags=["renko"])

# Store Renko engines per symbol
renko_engines = {}
strategy_engines = {}
last_rates = {}  # Cache last rates for each symbol

@router.get("/chart/{symbol}")
async def get_renko_chart(symbol: str, brick_size: float = None, limit: int = 100):
    """
    Get Renko brick data for charting
    ⚡ DATA SOURCE: REAL-TIME from MT5 (1-minute timeframe)
    
    Args:
        symbol: Trading symbol (e.g., EURUSD, GOLD, BTCUSD)
        brick_size: Brick size (if None, uses defaults)
        limit: Number of bricks to return (max 500)
    
    Returns:
        Real-time Renko brick data from MT5
    """
    try:
        if limit > 500:
            limit = 500
        
        # Default brick sizes if not specified
        if brick_size is None:
            brick_sizes = {
                "EURUSD": 0.005,
                "GBPUSD": 0.005,
                "USDJPY": 0.05,
                "GOLD": 5.0,
                "BTCUSD": 1.0,
            }
            brick_size = brick_sizes.get(symbol, 0.01)
        
        # Get symbol info from MT5 (real-time)
        symbol_info = mt5.symbol_info(symbol)
        if not symbol_info:
            raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found in MT5")
        
        # Fetch LIVE 1-minute candles from MT5 (real-time market data)
        logger.info(f"Fetching live 1-min data for {symbol} from MT5...")
        rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 500)
        
        if rates is None or len(rates) == 0:
            raise HTTPException(status_code=400, detail=f"No real-time price data from MT5 for {symbol}")
        
        # Cache the last rates timestamp for verification
        last_rates[symbol] = datetime.now().isoformat()
        
        # Initialize or get existing Renko engine
        engine_key = f"{symbol}_{brick_size}"
        if engine_key not in renko_engines:
            renko_engines[engine_key] = RenkoEngine(brick_size)
            strategy_engines[engine_key] = StrategyEngine(renko_engines[engine_key])
        
        renko = renko_engines[engine_key]
        strategy = strategy_engines[engine_key]
        
        # Feed all prices to Renko engine
        for rate in rates:
            renko.feed_tick(rate['close'])
        
        # Get brick history
        all_bricks = renko.history(limit)
        
        # Format bricks for charting
        chart_data = []
        for i, brick in enumerate(all_bricks):
            chart_data.append({
                "index": i,
                "open": float(brick.open_price),
                "close": float(brick.close_price),
                "high": float(brick.high),
                "low": float(brick.low),
                "color": brick.color,  # "green" or "red"
                "signal": "BUY" if brick.color == "green" else "SELL",
            })
        
        # Get current state
        current_direction = renko.direction()
        
        return {
            "symbol": symbol,
            "brick_size": brick_size,
            "bricks": chart_data[-limit:],  # Return last N bricks
            "total_bricks": len(all_bricks),
            "current_direction": current_direction,
            "current_price": float(rates[-1]['close']),
            "last_update": datetime.fromtimestamp(rates[-1]['time']).isoformat(),
            "data_source": "MT5_LIVE_1MIN",  # Confirm data is from MT5
            "timestamp": datetime.now().isoformat(),
        }
    
    except Exception as e:
        logger.error(f"Error getting Renko chart from MT5: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/ws/chart/{symbol}")
async def websocket_renko_chart(websocket: WebSocket, symbol: str):
    """
    WebSocket endpoint for real-time Renko chart updates
    ⚡ REAL-TIME STREAMING from MT5
    
    Updates client every time new 1-minute candle closes
    """
    await websocket.accept()
    
    try:
        # Get default brick size
        brick_sizes = {
            "EURUSD": 0.005,
            "GOLD": 5.0,
            "BTCUSD": 1.0,
        }
        brick_size = brick_sizes.get(symbol, 0.01)
        
        # Verify symbol exists in MT5
        symbol_info = mt5.symbol_info(symbol)
        if not symbol_info:
            await websocket.send_json({
                "error": f"Symbol {symbol} not found in MT5"
            })
            await websocket.close()
            return
        
        # Initialize Renko engine
        engine_key = f"{symbol}_{brick_size}"
        if engine_key not in renko_engines:
            renko_engines[engine_key] = RenkoEngine(brick_size)
            strategy_engines[engine_key] = StrategyEngine(renko_engines[engine_key])
        
        renko = renko_engines[engine_key]
        strategy = strategy_engines[engine_key]
        
        logger.info(f"WebSocket connected for {symbol} - streaming real-time MT5 data")
        
        # Stream real-time updates
        last_candle_time = None
        
        while True:
            # Get latest 1-min candle from MT5
            rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 10)
            
            if rates and len(rates) > 0:
                latest_time = rates[-1]['time']
                
                # Only process if new candle
                if latest_time != last_candle_time:
                    last_candle_time = latest_time
                    
                    # Feed new price
                    new_bricks = renko.feed_tick(rates[-1]['close'])
                    
                    # Get signal if bricks formed
                    signal = None
                    if new_bricks:
                        signal = strategy.process(new_bricks)
                    
                    # Send update to client
                    await websocket.send_json({
                        "symbol": symbol,
                        "current_price": float(rates[-1]['close']),
                        "new_bricks": [
                            {
                                "open": float(brick.open_price),
                                "close": float(brick.close_price),
                                "color": brick.color,
                            }
                            for brick in (new_bricks or [])
                        ],
                        "signal": signal['type'].upper() if signal else None,
                        "direction": renko.direction(),
                        "timestamp": datetime.fromtimestamp(rates[-1]['time']).isoformat(),
                        "data_source": "MT5_LIVE_STREAM",
                    })
            
            # Update every 0.5 seconds (more frequent for real-time feel)
            await asyncio.sleep(0.5)
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for {symbol}")
    except Exception as e:
        logger.error(f"WebSocket error for {symbol}: {e}")
        try:
            await websocket.send_json({"error": str(e)})
        except:
            pass


@router.post("/reset/{symbol}")
async def reset_renko_chart(symbol: str, brick_size: float = None):
    """Reset Renko engine for a symbol"""
    try:
        if brick_size is None:
            brick_sizes = {
                "EURUSD": 0.005,
                "GOLD": 5.0,
                "BTCUSD": 1.0,
            }
            brick_size = brick_sizes.get(symbol, 0.01)
        
        engine_key = f"{symbol}_{brick_size}"
        if engine_key in renko_engines:
            del renko_engines[engine_key]
            del strategy_engines[engine_key]
        
        logger.info(f"Reset Renko engine for {symbol}")
        return {"message": f"Reset Renko engine for {symbol}", "data_source": "MT5"}
    
    except Exception as e:
        logger.error(f"Error resetting Renko: {e}")
        raise HTTPException(status_code=500, detail=str(e))
