"""
Price Manager - Fetch and manage real-time prices from MT5
"""

import logging
from typing import Optional, Dict
import MetaTrader5 as mt5
from backend.supabase.client import supabase_client

logger = logging.getLogger("price_manager")


class PriceManager:
    """Manages real-time price data from MT5"""
    
    @staticmethod
    def get_quote(symbol: str) -> Optional[Dict]:
        """
        Get current bid/ask for a symbol from MT5
        
        Returns:
            {
                "symbol": "XAUUSD",
                "bid": 2050.45,
                "ask": 2050.55,
                "last_update": "2024-04-08T10:30:45Z",
                "bid_size": 100,
                "ask_size": 100
            }
        """
        try:
            # Ensure symbol is visible in MT5 Market Watch
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                logger.warning(f"Symbol {symbol} not found in MT5")
                return None
            
            # If symbol not visible, select it
            if not symbol_info.visible:
                if not mt5.symbol_select(symbol, True):
                    logger.warning(f"Could not select symbol {symbol}")
                    return None
            
            # Get tick data
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                logger.warning(f"No tick data for {symbol} - MT5 might not be initialized")
                return None
            
            return {
                "symbol": symbol,
                "bid": float(tick.bid),
                "ask": float(tick.ask),
                "last_update": tick.time_msc,
                "volume": float(tick.volume) if hasattr(tick, 'volume') else 0,
            }
        except Exception as e:
            logger.error(f"Error getting quote for {symbol}: {e}")
            return None
    
    @staticmethod
    def update_price_in_db(symbol: str, bid: float, ask: float) -> bool:
        """Update price_ticks table in Supabase"""
        try:
            # Check if symbol exists
            existing = supabase_client.table('price_ticks').select('*').eq('symbol', symbol).execute()
            
            if existing.data:
                # Update existing
                supabase_client.table('price_ticks').update({
                    'bid': bid,
                    'ask': ask,
                    'last_update': 'now()'
                }).eq('symbol', symbol).execute()
            else:
                # Insert new
                supabase_client.table('price_ticks').insert({
                    'symbol': symbol,
                    'bid': bid,
                    'ask': ask
                }).execute()
            
            return True
        except Exception as e:
            logger.error(f"Error updating price in DB: {e}")
            return False
    
    @staticmethod
    def get_all_symbols() -> list:
        """Get all available symbols from MT5"""
        try:
            # Get active symbols from Supabase
            symbols = supabase_client.table('available_symbols').select('symbol').eq('is_active', True).execute()
            return [s['symbol'] for s in symbols.data]
        except Exception as e:
            logger.error(f"Error getting symbols: {e}")
            return []
    
    @staticmethod
    def get_symbol_info(symbol: str) -> Optional[Dict]:
        """Get symbol specifications from Supabase"""
        try:
            result = supabase_client.table('available_symbols').select('*').eq('symbol', symbol).execute()
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Error getting symbol info: {e}")
            return None


# Global price manager instance
price_manager = PriceManager()
