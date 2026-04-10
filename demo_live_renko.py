"""
Live Renko Strategy Demo - Uses real MT5 prices
Shows how the bot would trade using Renko signals
"""
import MetaTrader5 as mt5
from backend.config import settings
from backend.renko.engine import RenkoEngine
from backend.strategy.engine import StrategyEngine
import time

print("=" * 80)
print("LIVE RENKO STRATEGY - REAL MT5 PRICES")
print("=" * 80)
print()

# Initialize MT5 - it may already be running
if not mt5.initialize(path=settings.MT5_PATH):
    print("⚠️  MT5 already initialized")
else:
    print("✅ MT5 initialized")

# Try to login - if already logged in, this may fail but we can continue
result = mt5.login(settings.MT5_LOGIN, settings.MT5_PASSWORD, settings.MT5_SERVER)

if result:
    print("✅ Logged in to MT5")
elif mt5.terminal_info():
    print("✅ MT5 already running (using existing session)")
else:
    print("❌ MT5 not available - make sure MT5 is running and logged in")
    print("   Please start MetaTrader 5 and login first")
    mt5.shutdown()
    exit(1)

# Select a symbol to demo - GOLD or EURUSD
symbol = "GOLD"  # Change to "EURUSD" if GOLD not available
symbol_info = mt5.symbol_info(symbol)

if not symbol_info:
    print(f"❌ Symbol {symbol} not found!")
    mt5.shutdown()
    exit(1)

print(f"📊 Symbol: {symbol}")
print(f"   Digits: {symbol_info.digits}")
print(f"   Point: {symbol_info.point}")
print()

# Get the last 100 candles for GOLD
rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H1, 0, 100)

if rates is None or len(rates) == 0:
    print(f"❌ Could not get price data for {symbol}")
    mt5.shutdown()
    exit(1)

print(f"Got {len(rates)} hourly candles")
print()

# Initialize Renko engine with brick size suitable for the symbol
if symbol == "GOLD":
    brick_size = 5.0  # $5 per brick for GOLD
elif symbol == "EURUSD":
    brick_size = 0.005  # 50 pips per brick for EURUSD
else:
    brick_size = 0.01

renko = RenkoEngine(brick_size)
strategy = StrategyEngine(renko)

print(f"Renko Configuration:")
print(f"   Brick Size: {brick_size}")
print()

print("=" * 80)
print("FEEDING PRICES INTO RENKO ENGINE")
print("=" * 80)
print()

brick_count = 0
signal_count = 0
last_signal = None

# Process each candle's close price
for i, rate in enumerate(rates[-50:], 1):  # Use last 50 candles
    price = rate['close']
    
    # Feed price to Renko
    new_bricks = renko.feed_tick(price)
    
    if new_bricks:
        brick_count += len(new_bricks)
        print(f"Candle {i}: Price {price:.2f} → {len(new_bricks)} brick(s) created")
        
        for brick in new_bricks:
            brick_color = "🟢 GREEN (BUY)" if brick.color == "green" else "🔴 RED (SELL)"
            print(f"   {brick_color} brick: {brick.open_price:.2f} → {brick.close_price:.2f}")
        
        # Get signal
        signal = strategy.process(new_bricks)
        
        if signal:
            signal_count += 1
            print(f"   ⚡ TRADE SIGNAL: {signal['type'].upper()} at {signal['price']:.2f}")
            last_signal = signal
        print()

print("=" * 80)
print("SUMMARY")
print("=" * 80)
print()
print(f"Price Range: {rates[-50][0]['close']:.2f} to {rates[-1]['close']:.2f}")
print(f"Bricks Created: {brick_count}")
print(f"Signals Generated: {signal_count}")

if last_signal:
    print()
    print(f"Last Signal: {last_signal['type'].upper()} at {last_signal['price']:.2f}")
    
    # Show what a trade would look like
    current_price = rates[-1]['close']
    
    print()
    print("=" * 80)
    print("SAMPLE TRADE (Using Last Signal)")
    print("=" * 80)
    print()
    
    if last_signal['type'] == 'buy':
        print(f"🟢 BUY Trade")
        print(f"   Entry Price: {last_signal['price']:.2f}")
        print(f"   Current Price: {current_price:.2f}")
        profit_loss = current_price - last_signal['price']
        print(f"   Unrealized P/L: {profit_loss:.2f} per lot")
        
        # With 0.1 lot size
        lot_size = 0.1
        pl_total = profit_loss * (100 if symbol == "GOLD" else 10000)  # GOLD: $100 per pip, EURUSD: $10 per pip
        print(f"   Unrealized P/L (0.1 lot): ${pl_total * lot_size:.2f}")
    else:
        print(f"🔴 SELL Trade")
        print(f"   Entry Price: {last_signal['price']:.2f}")
        print(f"   Current Price: {current_price:.2f}")
        profit_loss = last_signal['price'] - current_price
        print(f"   Unrealized P/L: {profit_loss:.2f} per lot")
        
        # With 0.1 lot size
        lot_size = 0.1
        pl_total = profit_loss * (100 if symbol == "GOLD" else 10000)
        print(f"   Unrealized P/L (0.1 lot): ${pl_total * lot_size:.2f}")

print()

# Show all bricks
all_bricks = renko.history(999)
print("=" * 80)
print(f"ALL BRICKS ({len(all_bricks)} total)")
print("=" * 80)
print()

for i, brick in enumerate(all_bricks[-10:], 1):  # Show last 10 bricks
    color_emoji = "🟢" if brick.color == "green" else "🔴"
    print(f"{color_emoji} Brick: {brick.open_price:.2f} → {brick.close_price:.2f}")

print()

mt5.shutdown()
