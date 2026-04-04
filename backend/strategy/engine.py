from typing import Optional

from backend.renko.engine import RenkoBrick, RenkoEngine

class StrategyEngine:
    def __init__(self, renko_engine: RenkoEngine):
        self.renko = renko_engine
        self.current_side: Optional[str] = None

    def process_tick(self, price: float) -> Optional[dict]:
        new_brick = self.renko.feed_tick(price)
        if not new_brick:
            return None

        signal = None
        if new_brick.color == "green":
            signal = "buy"
        elif new_brick.color == "red":
            signal = "sell"

        if signal is None:
            return None

        if self.current_side == signal:
            return None

        action = {
            "type": signal,
            "price": new_brick.high if signal == "buy" else new_brick.low,
            "brick": new_brick,
        }

        self.current_side = signal

        return action

    def reset(self):
        self.current_side = None
        self.renko.bricks.clear()
        self.renko.last_price = None
