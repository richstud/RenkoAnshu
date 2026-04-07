#!/usr/bin/env python
"""
Test suite for the signal generation module.
Validates the Renko strategy logic and signal generation.
"""
import sys
sys.path.insert(0, '.')

from backend.signals import SignalGenerator

def test_signal_generation():
    """Test basic signal generation."""
    gen = SignalGenerator(brick_size=1.0)
    
    # Test BUY signal (green brick)
    signal1 = gen.get_signal('XAUUSD', 100.0)
    assert signal1 is None, "First price should not generate signal"
    
    # Move up by 1.5 bricks - should get BUY
    signal2 = gen.get_signal('XAUUSD', 101.5)
    assert signal2 == 'BUY', f"Expected BUY, got {signal2}"
    print("✓ BUY signal generated correctly")
    
    # Move down by 2 bricks - should get SELL
    signal3 = gen.get_signal('XAUUSD', 99.5)
    assert signal3 == 'SELL', f"Expected SELL, got {signal3}"
    print("✓ SELL signal generated correctly")
    
    # Move back up by 2.5 bricks - should get BUY
    signal4 = gen.get_signal('XAUUSD', 102.0)
    assert signal4 == 'BUY', f"Expected BUY, got {signal4}"
    print("✓ Reversal BUY signal generated correctly")
    
    # Small move in same direction - should not generate signal
    signal5 = gen.get_signal('XAUUSD', 102.3)
    assert signal5 is None, "Small move should not generate signal"
    print("✓ No duplicate signal in same direction")


def test_brick_info():
    """Test brick information retrieval."""
    gen = SignalGenerator(brick_size=1.0)
    
    # No bricks yet
    info1 = gen.get_last_brick_info('XAUUSD')
    assert info1 is None, "Should be no brick info yet"
    
    # Create a brick
    gen.get_signal('XAUUSD', 100.0)
    gen.get_signal('XAUUSD', 102.0)
    
    info2 = gen.get_last_brick_info('XAUUSD')
    assert info2 is not None, "Should have brick info"
    assert info2['color'] == 'green', "Should be green brick"
    assert info2['direction'] == 'long', "Direction should be long"
    print("✓ Brick information retrieved correctly")


def test_multi_symbol():
    """Test multiple symbols can be tracked independently."""
    gen = SignalGenerator(brick_size=1.0)
    
    # Trade XAUUSD
    signal1 = gen.get_signal('XAUUSD', 100.0)
    signal2 = gen.get_signal('XAUUSD', 101.5)
    
    # Trade EURUSD
    signal3 = gen.get_signal('EURUSD', 1.1000)
    signal4 = gen.get_signal('EURUSD', 1.1015)
    
    assert signal2 == 'BUY', "XAUUSD should have BUY"
    assert signal4 == 'BUY', "EURUSD should have BUY"
    print("✓ Multiple symbols tracked independently")


def test_reset():
    """Test signal generator reset."""
    gen = SignalGenerator(brick_size=1.0)
    
    # Generate a signal
    gen.get_signal('XAUUSD', 100.0)
    gen.get_signal('XAUUSD', 101.5)
    
    # Reset
    gen.reset_symbol('XAUUSD')
    
    # Next price should not generate signal (history cleared)
    signal = gen.get_signal('XAUUSD', 102.0)
    assert signal is None, "After reset, next price should not generate signal"
    print("✓ Reset works correctly")


if __name__ == '__main__':
    print("Running signal generation tests...\n")
    try:
        test_signal_generation()
        test_brick_info()
        test_multi_symbol()
        test_reset()
        print("\n✅ All tests passed!")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
