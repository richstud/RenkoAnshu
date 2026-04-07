# Quick Reference: Signal Generation API

## Basic Usage

### Get a Trading Signal
```python
from backend.signals import get_signal

# Get signal for XAUUSD at price 2350.50
signal = get_signal('XAUUSD', 2350.50)

# Returns: 'BUY', 'SELL', or None
if signal == 'BUY':
    execute_buy_order()
elif signal == 'SELL':
    execute_sell_order()
```

## Advanced Usage

### SignalGenerator Class
```python
from backend.signals import SignalGenerator

# Create with custom brick size
gen = SignalGenerator(brick_size=0.5)

# Get signal
signal = gen.get_signal('EURUSD', 1.1050)

# Get brick details
info = gen.get_last_brick_info('EURUSD')
print(info['color'])      # 'green' or 'red'
print(info['direction'])  # 'long' or 'short'
print(info['high'])       # Brick high
print(info['low'])        # Brick low

# Reset a symbol
gen.reset_symbol('EURUSD')

# Reset all symbols
gen.reset_all()

# Update brick size (for new symbols)
gen.set_brick_size(1.0)
```

## API Endpoints

### Get Trading Signal
```
GET /signal/{symbol}/{price}

Example:
GET /signal/XAUUSD/2350.50

Response:
{
  "symbol": "XAUUSD",
  "price": 2350.50,
  "signal": "BUY",
  "brick_info": {
    "color": "green",
    "open": 2350.0,
    "close": 2351.0,
    "high": 2351.0,
    "low": 2350.0,
    "direction": "long"
  }
}
```

### Reset Signal State
```
POST /reset-signal/{symbol}

Example:
POST /reset-signal/XAUUSD

Response:
{
  "message": "Signal generator reset for XAUUSD"
}
```

## Brick Information Reference

### Brick Info Structure
```python
{
    "color": str,      # "green" (bullish) or "red" (bearish)
    "open": float,     # Brick open price
    "close": float,    # Brick close price
    "high": float,     # Brick high
    "low": float,      # Brick low
    "direction": str   # "long" (bullish trend) or "short" (bearish trend)
}
```

### Signal Return Values
- `'BUY'` - Green brick formed, long position signal
- `'SELL'` - Red brick formed, short position signal
- `None` - No complete brick yet, or same direction as current

## Strategy Rules

1. **Green Brick (Uptrend)**
   - Forms when price rises by brick_size or more
   - Triggers BUY signal
   - Entry point: brick high

2. **Red Brick (Downtrend)**
   - Forms when price falls by brick_size or more
   - Triggers SELL signal
   - Entry point: brick low

3. **Position Reversal**
   - Each signal reverses the previous position
   - Only one active position at a time
   - Prevents duplicate signals in same direction

## Configuration

### Environment Variables
```bash
RENKO_BRICK_SIZE=1.0        # Default brick size in points
SYMBOL=XAUUSD              # Default symbol
POLL_INTERVAL=0.5          # Polling interval in seconds
```

### Programmatic Configuration
```python
from backend.signals import signal_generator
from backend.config import settings

# Update brick size
signal_generator.set_brick_size(0.5)

# Or use settings
signal_generator.set_brick_size(settings.RENKO_BRICK_SIZE)
```

## Common Patterns

### Multi-Symbol Trading
```python
from backend.signals import signal_generator

symbols = ['XAUUSD', 'EURUSD', 'GBPUSD']
prices = [2350.50, 1.1050, 1.3250]

for symbol, price in zip(symbols, prices):
    signal = signal_generator.get_signal(symbol, price)
    if signal:
        execute_trade(symbol, signal)
```

### Real-time Signal Monitor
```python
import asyncio
from backend.signals import signal_generator

async def monitor_signals():
    while True:
        signal = signal_generator.get_signal('XAUUSD', current_price)
        if signal:
            print(f"Signal: {signal}")
            
        await asyncio.sleep(0.1)

asyncio.run(monitor_signals())
```

### Backtesting
```python
from backend.signals import SignalGenerator

gen = SignalGenerator(brick_size=1.0)
historical_prices = [100.0, 101.5, 99.0, 102.0, 100.5]

for price in historical_prices:
    signal = gen.get_signal('BACKTEST', price)
    if signal:
        print(f"Signal: {signal} at {price}")
```

## Error Handling

```python
from backend.signals import signal_generator

try:
    signal = signal_generator.get_signal('XAUUSD', 2350.50)
    if signal is None:
        print("No signal yet (incomplete brick)")
    else:
        print(f"Signal: {signal}")
except Exception as e:
    print(f"Error: {e}")
```

## Performance Notes

- Signal generation is O(1) operation
- Minimal memory footprint per symbol
- No database queries required for signal generation
- Fully in-memory state management
- Thread-safe for concurrent symbol tracking

## Testing

Run the comprehensive test suite:
```bash
python test_signals_full.py
```

Output:
```
✓ Renko engine creates green bricks on upward movement
✓ Renko engine creates red bricks on downward movement
✓ Brick history: 3+ bricks
✓ Strategy generates BUY signal on green brick
✓ Strategy generates SELL signal on red brick
✓ Strategy alternates BUY/SELL correctly
✓ Signal module returns BUY correctly
✓ Signal module returns SELL correctly

✅ All tests passed!
```

## Troubleshooting

### No signal returned after price movement
- Check if movement equals exact brick size
- Bricks form on >= brick_size movement
- Verify signal_generator is initialized

### Signal not changing direction
- Ensure price moved enough for new brick
- Check brick_size setting
- Reset symbol if stuck: `signal_generator.reset_symbol('SYMBOL')`

### Multiple symbols interfering
- SignalGenerator tracks each symbol independently
- No cross-symbol signal contamination
- Each symbol has its own engine and strategy

## Version History

- **v1.0.0**: Initial signal generation module
  - Unified signal interface
  - Multi-symbol support
  - API endpoints
