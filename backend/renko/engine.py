from dataclasses import dataclass
from typing import List, Optional

@dataclass
class RenkoBrick:
    open_price: float
    close_price: float
    high: float
    low: float
    color: str  # "green" or "red"
    timestamp: int = 0  # Unix timestamp of when brick was formed


class RenkoEngine:
    def __init__(self, brick_size: float = 1.0):
        self.brick_size = brick_size
        self.bricks: List[RenkoBrick] = []
        self.last_price: Optional[float] = None

    def feed_tick(self, price: float, timestamp: int = 0) -> Optional[RenkoBrick]:
        if self.last_price is None:
            # Use actual first-candle price as anchor (no snapping).
            self.last_price = price
            return None

        last_color = self.bricks[-1].color if self.bricks else None
        moved = price - self.last_price

        # Traditional Renko rules (matches XM / MT5 chart):
        #   Continuation (same direction): 1 * brick_size
        #   Reversal (opposite direction) : 2 * brick_size
        # Example (brick_size=2): red trend last_close=100
        #   -> green reversal needs price >= 104 (2x=4 above 100)
        #   -> first green brick: open=100, close=102
        if last_color is None:
            # First brick ever: 1x in either direction
            if moved >= self.brick_size:
                direction = 'green'
                brick_units = int(moved // self.brick_size)
            elif moved <= -self.brick_size:
                direction = 'red'
                brick_units = int(-moved // self.brick_size)
            else:
                return None
        elif last_color == 'green':
            if moved >= self.brick_size:                     # continuation green (1x)
                direction = 'green'
                brick_units = int(moved // self.brick_size)
            elif moved <= -2 * self.brick_size:              # reversal red (2x)
                direction = 'red'
                brick_units = 1 + int(max(0, -moved - 2 * self.brick_size) // self.brick_size)
            else:
                return None
        else:  # last_color == 'red'
            if moved <= -self.brick_size:                    # continuation red (1x)
                direction = 'red'
                brick_units = int(-moved // self.brick_size)
            elif moved >= 2 * self.brick_size:               # reversal green (2x)
                direction = 'green'
                brick_units = 1 + int(max(0, moved - 2 * self.brick_size) // self.brick_size)
            else:
                return None

        new_brick = None
        for _ in range(brick_units):
            if direction == 'green':
                brick_open = self.last_price
                brick_close = round(brick_open + self.brick_size, 10)
                new_brick = RenkoBrick(
                    open_price=brick_open,
                    close_price=brick_close,
                    high=brick_close,
                    low=brick_open,
                    color="green",
                    timestamp=timestamp,
                )
            else:
                brick_open = self.last_price
                brick_close = round(brick_open - self.brick_size, 10)
                new_brick = RenkoBrick(
                    open_price=brick_open,
                    close_price=brick_close,
                    high=brick_open,
                    low=brick_close,
                    color="red",
                    timestamp=timestamp,
                )
            self.bricks.append(new_brick)
            self.last_price = brick_close

        return new_brick

    def last_brick(self) -> Optional[RenkoBrick]:
        if self.bricks:
            return self.bricks[-1]
        return None

    def direction(self) -> Optional[str]:
        last = self.last_brick()
        if not last:
            return None
        return "long" if last.color == "green" else "short"

    def history(self, n: int = 50) -> List[RenkoBrick]:
        return self.bricks[-n:]
