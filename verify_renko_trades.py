#!/usr/bin/env python3
"""
Verify if BTCUSD trades follow the Renko strategy
Checks trade directions against Renko brick color changes
"""
import os
import sys
from datetime import datetime, timedelta
from supabase import create_client
import MetaTrader5 as mt5

# Supabase credentials
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: SUPABASE_URL or SUPABASE_KEY not set in environment")
    sys.exit(1)

# Initialize clients
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("🔍 Fetching BTCUSD trades from Supabase...")

# Fetch all BTCUSD trades from auto_trading_history
try:
    response = supabase.table('auto_trading_history').select('*').eq('symbol', 'BTCUSD').order('entry_time', desc=False).execute()
    trades = response.data
    
    if not trades:
        print("❌ No BTCUSD trades found in auto_trading_history")
        sys.exit(1)
    
    print(f"\n✅ Found {len(trades)} BTCUSD trades\n")
    print("=" * 100)
    print(f"{'#':<3} {'Direction':<10} {'Entry Price':<15} {'Entry Time':<25} {'Lot Size':<10} {'Reason':<30}")
    print("=" * 100)
    
    for i, trade in enumerate(trades, 1):
        direction = trade.get('direction', 'N/A')
        entry_price = trade.get('entry_price', 0)
        entry_time = trade.get('entry_time', 'N/A')
        lot_size = trade.get('lot_size', 0)
        reason = trade.get('reason', 'N/A')
        
        print(f"{i:<3} {direction:<10} {entry_price:<15.2f} {entry_time:<25} {lot_size:<10} {reason:<30}")
    
    print("=" * 100)
    
    # Analyze sequence
    print("\n📊 Trade Sequence Analysis:")
    print("-" * 100)
    
    for i, trade in enumerate(trades):
        if i == 0:
            print(f"[Trade 1] Initial trade: {trade['direction']} @ {trade['entry_price']} ({trade['entry_time']})")
            prev_direction = trade['direction']
        else:
            curr_direction = trade['direction']
            if curr_direction != prev_direction:
                print(f"[Trade {i+1}] ✅ Direction changed: {prev_direction} → {curr_direction} @ {trade['entry_price']} ({trade['entry_time']})")
                print(f"         Reason: {trade['reason']}")
            else:
                print(f"[Trade {i+1}] ⚠️  Same direction as before: {curr_direction} @ {trade['entry_price']} ({trade['entry_time']})")
                print(f"         Reason: {trade['reason']}")
            prev_direction = curr_direction
    
    # Summary
    print("\n" + "=" * 100)
    print("📈 Summary:")
    print(f"Total Trades: {len(trades)}")
    buy_count = len([t for t in trades if t['direction'] == 'BUY'])
    sell_count = len([t for t in trades if t['direction'] == 'SELL'])
    print(f"BUY Trades:  {buy_count}")
    print(f"SELL Trades: {sell_count}")
    
    # Check if alternating (Renko expects direction changes)
    alternating = True
    for i in range(1, len(trades)):
        if trades[i]['direction'] == trades[i-1]['direction']:
            alternating = False
            break
    
    if alternating and len(trades) > 1:
        print("✅ Trades are ALTERNATING (following Renko strategy)")
    elif len(trades) <= 1:
        print("⏳ Insufficient trades to verify alternating pattern")
    else:
        print("❌ Trades are NOT alternating (possible issue with strategy)")
    
    print("=" * 100)
    
except Exception as e:
    print(f"❌ Error fetching trades: {e}")
    sys.exit(1)
