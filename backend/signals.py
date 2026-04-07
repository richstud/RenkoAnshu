"""
Signal generation module for Renko-based trading strategy.
Provides a unified interface to get trading signals.
"""
from typing import Dict, Optional

from backend.renko.engine import RenkoEngine
from backend.strategy.engine import StrategyEngine


class SignalGenerator:
    """Manages signal generation for multiple trading symbols/accounts."""
    
    def __init__(self, brick_size: float = 1.0):
        self.brick_size = brick_size
        self.engines: Dict[str, RenkoEngine] = {}
        self.strategies: Dict[str, StrategyEngine] = {}
    
    def get_signal(self, symbol: str, price: float) -> Optional[str]:
        """
        Generate a trading signal for a symbol at a given price.
        
        Args:
            symbol: Trading symbol (e.g., 'XAUUSD')
            price: Current market price
            
        Returns:
            'BUY', 'SELL', or None (no signal)
        """
        # Initialize engines for this symbol if needed
        if symbol not in self.engines:
            self.engines[symbol] = RenkoEngine(brick_size=self.brick_size)
            self.strategies[symbol] = StrategyEngine(self.engines[symbol])
        
        strategy = self.strategies[symbol]
        action = strategy.process_tick(price)
        
        if action is None:
            return None
        
        return action["type"].upper()
    
    def get_last_brick_info(self, symbol: str) -> Optional[dict]:
        """
        Get information about the last brick for a symbol.
        
        Returns:
            Dict with brick_color, price, direction or None if no bricks exist
        """
        if symbol not in self.engines:
            return None
        
        engine = self.engines[symbol]
        last_brick = engine.last_brick()
        
        if last_brick is None:
            return None
        
        return {
            "color": last_brick.color,
            "open": last_brick.open_price,
            "close": last_brick.close_price,
            "high": last_brick.high,
            "low": last_brick.low,
            "direction": engine.direction(),
        }
    
    def reset_symbol(self, symbol: str):
        """Reset the engine for a specific symbol."""
        if symbol in self.engines:
            self.strategies[symbol].reset()
    
    def reset_all(self):
        """Reset all engines."""
        for strategy in self.strategies.values():
            strategy.reset()
    
    def set_brick_size(self, brick_size: float):
        """Update brick size for new symbols (existing symbols keep their size)."""
        self.brick_size = brick_size


# Global signal generator instance
signal_generator = SignalGenerator()


def get_signal(symbol: str, price: float) -> Optional[str]:
    """
    Get a trading signal for a symbol at a given price.
    
    Args:
        symbol: Trading symbol (e.g., 'XAUUSD')
        price: Current market price
        
    Returns:
        'BUY', 'SELL', or None (no signal)
    """
    return signal_generator.get_signal(symbol, price)
