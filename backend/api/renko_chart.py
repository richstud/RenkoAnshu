"""
Real-time Renko Chart Endpoint
Provides Renko brick data for frontend charting - directly from MT5
Non-blocking implementation with bid/ask support
"""
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from backend.renko.engine import RenkoEngine
from backend.strategy.engine import StrategyEngine
from backend.config import settings
from backend.mt5.connection import mt5_manager
import MetaTrader5 as mt5
from datetime import datetime, timedelta
import logging
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/renko", tags=["renko"])

# Store Renko engines per symbol
renko_engines = {}
strategy_engines = {}
last_rates = {}  # Cache last rates for each symbol
chart_cache = {}  # Cache chart data to avoid recalculation
cache_ttl = {}  # Cache time-to-live

# Thread pool for non-blocking calculations
executor = ThreadPoolExecutor(max_workers=4)

def calculate_renko_bricks(symbol: str, rates: list, brick_size: float, limit: int = 100):
    """
    ⚡ Runs in thread pool - non-blocking
    Calculate Renko bricks without blocking event loop
    """
    try:
        engine_key = f"{symbol}_{brick_size}"
        
        if engine_key not in renko_engines:
            renko_engines[engine_key] = RenkoEngine(brick_size)
            strategy_engines[engine_key] = StrategyEngine(renko_engines[engine_key])
        
        renko = renko_engines[engine_key]
        
        # Only feed last 50 rates to avoid expensive calculations
        for rate in rates[-50:]:
            renko.feed_tick(rate['close'], int(rate['time']))
        
        # Get brick history
        all_bricks = renko.history(min(limit, 100))
        
        # Format bricks — only mark the FIRST brick of each new color as a signal (reversal)
        chart_data = []
        prev_color = None
        for i, brick in enumerate(all_bricks):
            is_reversal = (prev_color is not None and brick.color != prev_color)
            signal = ("BUY" if brick.color == "green" else "SELL") if is_reversal else None
            chart_data.append({
                "index": i,
                "open": float(brick.open_price),
                "close": float(brick.close_price),
                "high": float(brick.high),
                "low": float(brick.low),
                "color": brick.color,
                "signal": signal,
                "time": brick.timestamp,
            })
            prev_color = brick.color
        
        # Get current bid/ask from latest close price
        current_price = float(rates[-1]['close'])
        # Calculate bid/ask as close +/- small spread (typical forex spread)
        bid = current_price - 0.0001  # 1 pip spread estimate
        ask = current_price + 0.0001
        
        # For symbols with larger pip sizes, adjust spread
        if current_price > 100:
            bid = current_price - 0.01
            ask = current_price + 0.01
        elif current_price > 10:
            bid = current_price - 0.001
            ask = current_price + 0.001
        
        return {
            "bricks": chart_data[-limit:],
            "total_bricks": len(all_bricks),
            "direction": renko.direction(),
            "current_price": current_price,
            "bid": bid,
            "ask": ask,
        }
    except Exception as e:
        logger.error(f"Error calculating Renko: {e}")
        raise

@router.get("/chart/{symbol}")
async def get_renko_chart(symbol: str, brick_size: float = None, timeframe: int = 1, limit: int = 100):
    """
    Get Renko brick data for charting
    ⚡ NON-BLOCKING - Runs calculations in thread pool
    ⚡ CACHING - Returns cached data if fresh
    
    Args:
        symbol: Trading symbol (e.g., EURUSD, GOLD, BTCUSD)
        brick_size: Brick size (if None, uses defaults)
        timeframe: 1 for 1-minute, 5 for 5-minute candles (default: 1)
        limit: Number of bricks to return (max 100 - kept low for performance)
    
    Returns:
        Real-time Renko brick data from MT5 + bid/ask prices
    """
    try:
        if limit > 100:
            limit = 100  # Limit to 100 bricks max for performance
        
        # Default brick sizes if not specified
        if brick_size is None:
            brick_sizes = {
                "EURUSD": 0.005,
                "GBPUSD": 0.005,
                "USDJPY": 0.05,
                "GOLD": 5.0,
                "BTCUSD": 1.0,
                "XPTUSD": 0.0005,  # Platinum - small brick size
                "XPDUSD": 0.0005,  # Palladium - small brick size
            }
            brick_size = brick_sizes.get(symbol, 0.01)
        
        cache_key = f"{symbol}_{brick_size}_{timeframe}"
        current_time = time.time()
        
        # Check cache (valid for 1 second to avoid duplicate calculations)
        if cache_key in chart_cache and cache_key in cache_ttl:
            if current_time - cache_ttl[cache_key] < 1.0:
                logger.debug(f"📦 Cache hit for {cache_key}")
                cached_data = chart_cache[cache_key]
                cached_data["timestamp"] = datetime.now().isoformat()
                return cached_data
        
        # Get symbol info from MT5
        symbol_info = mt5.symbol_info(symbol)
        if not symbol_info:
            raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found in MT5")
        
        # Select timeframe
        if timeframe == 5:
            tf = mt5.TIMEFRAME_M5
            logger.info(f"📊 Fetching 5-min data for {symbol} from MT5...")
            candle_count = 150  # Less data for performance
        else:
            tf = mt5.TIMEFRAME_M1
            logger.info(f"📊 Fetching 1-min data for {symbol} from MT5...")
            candle_count = 100  # Reduced from 500 for performance
        
        # Fetch rates from MT5 (with timeout)
        try:
            rates = mt5.copy_rates_from_pos(symbol, tf, 0, candle_count)
        except Exception as e:
            logger.error(f"❌ MT5 error fetching rates: {e}")
            rates = None
        
        if rates is None or len(rates) == 0:
            raise HTTPException(status_code=400, detail=f"No real-time price data from MT5 for {symbol}")
        
        # ⚡ Run Renko calculation in thread pool (NON-BLOCKING)
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            executor,
            calculate_renko_bricks,
            symbol,
            rates,
            brick_size,
            limit
        )
        
        # Build response with bid/ask
        response = {
            "symbol": symbol,
            "brick_size": brick_size,
            "bricks": result["bricks"],
            "total_bricks": result["total_bricks"],
            "current_price": result["current_price"],
            "bid": result["bid"],
            "ask": result["ask"],
            "current_direction": result["direction"],
            "timestamp": datetime.now().isoformat(),
            "data_source": "MT5_LIVE",
            "timeframe": f"{timeframe}M",
        }
        
        # Cache result
        chart_cache[cache_key] = response
        cache_ttl[cache_key] = current_time
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Chart error for {symbol}: {e}")
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
            
            if rates is not None and len(rates) > 0:
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


@router.websocket("/stream/{symbol}")
async def stream_renko_chart(websocket: WebSocket, symbol: str, brick_size: float = None):
    """
    WebSocket endpoint for real-time Renko chart streaming
    ⚡ REAL-TIME STREAMING from MT5 
    """
    await websocket.accept()
    
    try:
        # Get default brick size
        if brick_size is None:
            brick_sizes = {
                "EURUSD": 0.005,
                "GBPUSD": 0.005,
                "USDJPY": 0.05,
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
        
        logger.info(f"🔌 WebSocket stream connected for {symbol} - brick_size: {brick_size}")
        
        # Stream real-time updates
        last_candle_time = None
        skip_count = 0
        
        while True:
            # Get latest 1-min candles and live tick from MT5
            rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 100)
            tick = mt5.symbol_info_tick(symbol)

            bid = float(tick.bid) if tick else None
            ask = float(tick.ask) if tick else None
            tick_price = float(tick.last) if tick and tick.last > 0 else bid

            if rates is not None and len(rates) > 0:
                latest_time = rates[-1]['time']
                candle_close = float(rates[-1]['close'])
                current_price = tick_price or candle_close

                if latest_time != last_candle_time:
                    last_candle_time = latest_time

                    for rate in rates[-10:]:
                        renko.feed_tick(rate['close'])

                    all_bricks = renko.history(100)

                    chart_data = []
                    prev_color = None
                    for i, brick in enumerate(all_bricks):
                        is_reversal = (prev_color is not None and brick.color != prev_color)
                        chart_data.append({
                            "index": i,
                            "open": float(brick.open_price),
                            "close": float(brick.close_price),
                            "high": float(brick.high),
                            "low": float(brick.low),
                            "color": brick.color,
                            "signal": ("BUY" if brick.color == "green" else "SELL") if is_reversal else None,
                        })
                        prev_color = brick.color

                    signal = None
                    if len(all_bricks) > 0:
                        signal = strategy.process(all_bricks)

                    msg = {
                        "symbol": symbol,
                        "brick_size": brick_size,
                        "bricks": chart_data,
                        "total_bricks": len(all_bricks),
                        "current_price": current_price,
                        "current_direction": renko.direction(),
                        "signal": signal['type'].upper() if signal else None,
                        "timestamp": datetime.fromtimestamp(rates[-1]['time']).isoformat(),
                        "data_source": "MT5_LIVE_STREAM",
                    }
                    if bid: msg["bid"] = bid
                    if ask: msg["ask"] = ask
                    await websocket.send_json(msg)
                    skip_count = 0
                else:
                    skip_count += 1
                    # Send tick update every 5 loops (every 500ms)
                    if skip_count >= 5:
                        skip_count = 0
                        msg = {
                            "symbol": symbol,
                            "current_price": current_price,
                            "data_source": "MT5_TICK_UPDATE",
                        }
                        if bid: msg["bid"] = bid
                        if ask: msg["ask"] = ask
                        await websocket.send_json(msg)

            # 100ms loop — 10 updates per second
            await asyncio.sleep(0.1)
    
    except WebSocketDisconnect:
        logger.info(f"🔌 WebSocket stream disconnected for {symbol}")
    except Exception as e:
        logger.error(f"🔌 WebSocket stream error for {symbol}: {e}")
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
