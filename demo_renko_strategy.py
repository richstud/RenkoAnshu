"""
Renko Strategy Demo - Shows how bricks are created and signals are generated
Run this to understand the Renko algorithm step-by-step
"""
from backend.renko.engine import RenkoEngine
from backend.strategy.engine import StrategyEngine

print("=" * 80)
print("RENKO TRADING STRATEGY - DEMO WITH CALCULATIONS")
print("=" * 80)
print()

# Initialize engines
brick_size = 0.05  # 0.05 for EURUSD (50 pips)
renko = RenkoEngine(brick_size)
strategy = StrategyEngine()

print(f"📊 Configuration:")
print(f"   Brick Size: {brick_size}")
print(f"   Strategy: Renko Reversal")
print()

# Simulate price data for EURUSD
prices = [
    1.1700,  # Start
    1.1705,  # +5 pips (no brick yet)
    1.1710,  # +10 pips (no brick yet)
    1.1715,  # +15 pips (no brick yet)
    1.1720,  # +20 pips (no brick yet)
    1.1725,  # +25 pips (no brick yet)
    1.1730,  # +30 pips (no brick yet)
    1.1735,  # +35 pips (no brick yet)
    1.1740,  # +40 pips (no brick yet)
    1.1745,  # +45 pips (no brick yet)
    1.1750,  # +50 pips (GREEN BRICK #1!)
    1.1751,  # +51 pips (still in same brick)
    1.1755,  # +55 pips (GREEN BRICK #2!)
    1.1760,  # +60 pips (GREEN BRICK #3!)
    1.1740,  # Down -20 pips (RED BRICK #1 - REVERSAL!)
    1.1730,  # -30 pips (RED BRICK #2!)
    1.1720,  # -40 pips (RED BRICK #3!)
    1.1760,  # Up +40 pips (GREEN BRICKS forming)
    1.1765,  # +45 pips (GREEN BRICK)
    1.1770,  # +50 pips (GREEN BRICK)
]

print("=" * 80)
print("PRICE FEED AND BRICK GENERATION")
print("=" * 80)
print()

signals_generated = []

for i, price in enumerate(prices, 1):
    print(f"Step {i}: Price = {price:.4f}")
    
    # Feed price to Renko engine
    new_bricks = renko.feed_tick(price)
    
    if new_bricks:
        print(f"   ✅ {len(new_bricks)} NEW BRICK(S) CREATED:")
        for brick in new_bricks:
            print(f"      - {brick.color.upper()} brick: {brick.open_price:.4f} → {brick.close_price:.4f}")
    else:
        print(f"   ⏳ Waiting... (price hasn't moved {brick_size} enough yet)")
    
    # Get signal from strategy
    signal = strategy.process(new_bricks)
    
    if signal:
        print(f"   🎯 SIGNAL GENERATED: {signal['type'].upper()} at {signal['price']:.4f}")
        signals_generated.append({
            'step': i,
            'price': price,
            'signal': signal['type'],
            'signal_price': signal['price']
        })
    else:
        if new_bricks:
            print(f"   (No signal - same direction as before)")
    
    print()

print("=" * 80)
print("BRICK HISTORY")
print("=" * 80)
print()

all_bricks = renko.history(999)  # Get all bricks
for i, brick in enumerate(all_bricks, 1):
    print(f"Brick #{i}: {brick.color.upper():6} | Open: {brick.open_price:.4f} | Close: {brick.close_price:.4f} | Range: {abs(brick.close_price - brick.open_price):.4f}")

print()
print("=" * 80)
print("SIGNALS GENERATED")
print("=" * 80)
print()

if signals_generated:
    for sig in signals_generated:
        print(f"Step {sig['step']}: {sig['signal'].upper()} signal at price {sig['signal_price']:.4f}")
else:
    print("No signals generated yet")

print()
print("=" * 80)
print("HOW RENKO WORKS:")
print("=" * 80)
print("""
1. BRICK CREATION:
   - Each brick represents a fixed price movement (brick_size)
   - Green brick = upward movement
   - Red brick = downward movement
   - Prices within the brick range are ignored (no micro-movements)

2. SIGNAL GENERATION:
   - BUY signal: When a NEW GREEN brick forms (after red bricks)
   - SELL signal: When a NEW RED brick forms (after green bricks)
   - Prevents duplicate signals in same direction

3. ADVANTAGES:
   - Filters out noise and consolidation
   - Clear entry/exit points
   - Works in trending markets
   - Ignores sideways price action

4. EXAMPLE:
   Prices: 1.1700 → 1.1750 → 1.1755 → 1.1760
   Brick size: 0.0050 (50 pips)
   
   Step 1: 1.1700 to 1.1750 = Green brick (move of 50 pips)
   Step 2: 1.1750 to 1.1755 = Same brick (only 5 pips, need 50)
   Step 3: 1.1755 to 1.1760 = Another green brick (another 50 pips)
   
   Signals: BUY at 1.1750, BUY at 1.1760 (but no duplicate signal)
""")

print("=" * 80)
print("CURRENT STATE:")
print("=" * 80)
print()
print(f"Last price: {prices[-1]:.4f}")
print(f"Direction: {renko.direction()}")
print(f"Total bricks: {len(all_bricks)}")
if all_bricks:
    print(f"Last brick: {all_bricks[-1].color.upper()}")
print()
