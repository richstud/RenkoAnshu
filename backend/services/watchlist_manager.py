"""
Watchlist Manager - Manage trading watchlist and parameters
"""

import logging
from typing import List, Optional, Dict
from backend.supabase.client import supabase_client

logger = logging.getLogger("watchlist_manager")


class WatchlistManager:
    """Manages watchlist for all accounts"""
    
    @staticmethod
    def add_to_watchlist(
        account_id: int,
        symbol: str,
        lot_size: float = 0.01,
        stop_loss_pips: float = 50,
        take_profit_pips: float = 100,
        trailing_stop_pips: float = 30,
        use_trailing_stop: bool = False,
        brick_size: float = 1.0,
        algo_enabled: bool = True,
    ) -> Optional[Dict]:
        """Add symbol to watchlist for account"""
        try:
            data = {
                "account_id": account_id,
                "symbol": symbol,
                "is_active": True,
                "lot_size": lot_size,
                "stop_loss_pips": stop_loss_pips,
                "take_profit_pips": take_profit_pips,
                "trailing_stop_pips": trailing_stop_pips,
                "use_trailing_stop": use_trailing_stop,
                "brick_size": brick_size,
                "algo_enabled": algo_enabled,
            }
            
            # Upsert so re-adding an existing (account_id, symbol) simply refreshes its settings
            # instead of throwing a unique-constraint violation.
            result = supabase_client.table("watchlist").upsert(data, on_conflict="account_id,symbol").execute()
            
            if result.data:
                logger.info(f"Added {symbol} to watchlist for account {account_id}")
                return result.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Error adding to watchlist: {e}")
            return None
    
    @staticmethod
    def get_watchlist(account_id: int) -> List[Dict]:
        """Get watchlist for account"""
        try:
            result = supabase_client.table("watchlist").select("*").eq("account_id", account_id).eq("is_active", True).execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Error getting watchlist: {e}")
            return []
    
    @staticmethod
    def get_watchlist_item(item_id: int) -> Optional[Dict]:
        """Get specific watchlist item"""
        try:
            result = supabase_client.table("watchlist").select("*").eq("id", item_id).execute()
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Error getting watchlist item: {e}")
            return None
    
    @staticmethod
    def update_watchlist_item(item_id: int, **kwargs) -> Optional[Dict]:
        """Update watchlist item (SL, TP, Trail, Brick Size, etc)"""
        try:
            # Remove None values
            update_data = {k: v for k, v in kwargs.items() if v is not None}
            
            result = supabase_client.table("watchlist").update(update_data).eq("id", item_id).execute()
            
            if result.data:
                logger.info(f"Updated watchlist item {item_id}: {update_data}")
                return result.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Error updating watchlist: {e}")
            return None
    
    @staticmethod
    def toggle_algo(item_id: int, enabled: bool) -> Optional[Dict]:
        """Toggle algorithm on/off for specific symbol"""
        try:
            result = supabase_client.table("watchlist").update({"algo_enabled": enabled}).eq("id", item_id).execute()
            
            if result.data:
                status = "enabled" if enabled else "disabled"
                logger.info(f"Algorithm {status} for watchlist item {item_id}")
                return result.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Error toggling algo: {e}")
            return None
    
    @staticmethod
    def remove_from_watchlist(item_id: int) -> bool:
        """Remove item from watchlist"""
        try:
            result = supabase_client.table("watchlist").delete().eq("id", item_id).execute()
            logger.info(f"Removed watchlist item {item_id}")
            return True
        except Exception as e:
            logger.error(f"Error removing from watchlist: {e}")
            return False
    
    @staticmethod
    def get_symbol_settings(account_id: int, symbol: str) -> Optional[Dict]:
        """Get trading settings for specific symbol/account combo"""
        try:
            result = supabase_client.table("watchlist").select("*").eq("account_id", account_id).eq("symbol", symbol).execute()
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Error getting symbol settings: {e}")
            return None
    
    @staticmethod
    def is_algo_enabled(account_id: int, symbol: str) -> bool:
        """Check if algo is enabled for symbol/account"""
        settings = WatchlistManager.get_symbol_settings(account_id, symbol)
        return settings.get("algo_enabled", True) if settings else True


# Global watchlist manager instance
watchlist_manager = WatchlistManager()
