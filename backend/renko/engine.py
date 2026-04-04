from dataclasses import dataclass
from typing import List, Optional

@dataclass
class RenkoBrick:
    open_price: float
    close_price: float
    high: float
    low: float
    color: str  # "green" or "red"


class RenkoEngine:
    def __init__(self, brick_size: float = 1.0):
        self.brick_size = brick_size
        self.bricks: List[RenkoBrick] = []
        self.last_price: Optional[float] = None

    def feed_tick(self, price: float) -> Optional[RenkoBrick]:
        if self.last_price is None:
            self.last_price = price
            return None

        moved = price - self.last_price
        brick_units = int(abs(moved) // self.brick_size)

        if brick_units == 0:
            return None

        new_brick = None
        for _ in range(brick_units):
            if moved > 0:
                brick_open = self.last_price
                brick_close = brick_open + self.brick_size
                new_brick = RenkoBrick(
                    open_price=brick_open,
                    close_price=brick_close,
                    high=brick_close,
                    low=brick_open,
                    color="green",
                )
                self.bricks.append(new_brick)
            else:
                brick_open = self.last_price
                brick_close = brick_open - self.brick_size
                new_brick = RenkoBrick(
                    open_price=brick_open,
                    close_price=brick_close,
                    high=brick_open,
                    low=brick_close,
                    color="red",
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
