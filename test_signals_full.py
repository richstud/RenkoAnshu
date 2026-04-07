#!/usr/bin/env python
"""
Test suite for the Renko signal generation logic.
Validates the core algorithm without external dependencies.
"""
import sys
import os

# Create a minimal .env for testing
env_content = """
SUPABASE_URL=https://test.supabase.co
SUPABASE_KEY=test-key
MT5_PATH=/test
RENKO_BRICK_SIZE=1.0
SYMBOL=XAUUSD
POLL_INTERVAL=0.5
"""

with open('.env', 'w') as f:
    f.write(env_content)

sys.path.insert(0, '.')

# Now import after .env is created
from backend.renko.engine import RenkoEngine
from backend.strategy.engine import StrategyEngine

def test_renko_engine():
    """Test the Renko engine brick formation."""
    engine = RenkoEngine(brick_size=1.0)
    
    # Feed ticks
    brick1 = engine.feed_tick(100.0)
    assert brick1 is None, "First tick should not create brick"
    
    # Move up 1.5 units - should create 1 green brick
    brick2 = engine.feed_tick(101.5)
    assert brick2 is not None, "Should create brick"
    assert brick2.color == 'green', "Should be green brick"
    print("✓ Renko engine creates green bricks on upward movement")
    
    # Move down 2.5 units - should create 2 red bricks
    brick3 = engine.feed_tick(99.0)
    assert brick3 is not None, "Should create brick"
    assert brick3.color == 'red', "Should be red brick"
    print("✓ Renko engine creates red bricks on downward movement")
    
    # Check history
    history = engine.history(10)
    assert len(history) >= 3, "Should have at least 3 bricks"
    print(f"✓ Brick history: {len(history)} bricks")


def test_strategy_engine():
    """Test the strategy engine signal generation."""
    renko = RenkoEngine(brick_size=1.0)
    strategy = StrategyEngine(renko)
    
    # Initial state
    signal1 = strategy.process_tick(100.0)
    assert signal1 is None, "First tick should not generate signal"
    
    # Move up - should generate BUY
    signal2 = strategy.process_tick(101.5)
    assert signal2 is not None, "Should generate signal"
    assert signal2['type'] == 'buy', "Should be buy signal"
    print("✓ Strategy generates BUY signal on green brick")
    
    # Move down - should generate SELL
    signal3 = strategy.process_tick(99.0)
    assert signal3 is not None, "Should generate signal"
    assert signal3['type'] == 'sell', "Should be sell signal"
    print("✓ Strategy generates SELL signal on red brick")
    
    # Move up again - should generate BUY
    signal4 = strategy.process_tick(101.0)
    assert signal4 is not None, "Should generate signal"
    assert signal4['type'] == 'buy', "Should be buy signal"
    print("✓ Strategy alternates BUY/SELL correctly")


def test_signal_module():
    """Test the high-level signal generation interface."""
    from backend.signals import SignalGenerator
    
    gen = SignalGenerator(brick_size=1.0)
    
    # Get signals
    sig1 = gen.get_signal('XAUUSD', 100.0)
    assert sig1 is None, "First price should not generate signal"
    
    sig2 = gen.get_signal('XAUUSD', 101.5)
    assert sig2 == 'BUY', f"Expected BUY, got {sig2}"
    print("✓ Signal module returns BUY correctly")
    
    sig3 = gen.get_signal('XAUUSD', 99.0)
    assert sig3 == 'SELL', f"Expected SELL, got {sig3}"
    print("✓ Signal module returns SELL correctly")


if __name__ == '__main__':
    print("Running comprehensive signal tests...\n")
    try:
        test_renko_engine()
        print()
        test_strategy_engine()
        print()
        test_signal_module()
        print("\n✅ All tests passed!")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Clean up test .env
        if os.path.exists('.env'):
            os.remove('.env')
