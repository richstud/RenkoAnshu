from typing import Optional

from backend.renko.engine import RenkoBrick, RenkoEngine

class StrategyEngine:
    def __init__(self, renko_engine: RenkoEngine, min_reversal_bricks: int = 2):
        self.renko = renko_engine
        self.current_side: Optional[str] = None
        self.min_reversal_bricks = min_reversal_bricks  # Require N consecutive opposite bricks
        self.consecutive_count: int = 0  # Count of bricks in current direction

    def process_tick(self, price: float) -> Optional[dict]:
        new_brick = self.renko.feed_tick(price)
        if not new_brick:
            return None

        if new_brick.color == "green":
            signal = "buy"
        elif new_brick.color == "red":
            signal = "sell"
        else:
            return None

        # Count consecutive bricks in this direction
        if signal == self.current_side:
            # Same direction as open trade — no new signal
            self.consecutive_count += 1
            return None

        # Opposite direction detected — increment reversal counter
        if self.current_side is not None:
            # We're tracking a potential reversal
            if not hasattr(self, '_reversal_signal') or self._reversal_signal != signal:
                # New reversal direction started — reset counter to 1
                self._reversal_signal = signal
                self._reversal_count = 1
            else:
                self._reversal_count += 1

            if self._reversal_count < self.min_reversal_bricks:
                # Not enough confirming bricks yet — wait
                return None

        # Signal confirmed
        action = {
            "type": signal,
            "price": new_brick.high if signal == "buy" else new_brick.low,
            "brick": new_brick,
        }

        self.current_side = signal
        self.consecutive_count = 1
        self._reversal_signal = None
        self._reversal_count = 0
        return action

    def reset(self):
        self.current_side = None
        self.consecutive_count = 0
        self._reversal_signal = None
        self._reversal_count = 0
        self.renko.bricks.clear()
        self.renko.last_price = None
