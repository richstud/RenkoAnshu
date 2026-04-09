#!/usr/bin/env python
"""
Quick test for new API endpoints
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.config import settings
from backend.supabase.client import supabase_client
from backend.services.price_manager import price_manager
from backend.services.watchlist_manager import watchlist_manager

async def test_endpoints():
    print("\n" + "="*50)
    print("Testing API Endpoints")
    print("="*50 + "\n")
    
    # Test 1: Get tickers
    print("1️⃣  Testing GET /api/tickers")
    try:
        result = supabase_client.table('available_symbols').select('*').eq('is_active', True).execute()
        print(f"✅ Found {len(result.data)} symbols")
        for sym in result.data[:3]:
            print(f"   - {sym['symbol']}: {sym['description']}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Get quote
    print("\n2️⃣  Testing GET /api/tickers/{symbol}/quote")
    try:
        quote = price_manager.get_quote("XAUUSD")
        if quote:
            print(f"✅ XAUUSD: Bid={quote['bid']}, Ask={quote['ask']}")
        else:
            print("❌ No quote data available (MT5 may not be running)")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Add to watchlist
    print("\n3️⃣  Testing POST /api/watchlist")
    try:
        result = watchlist_manager.add_to_watchlist(
            account_id=101510620,
            symbol="XAUUSD",
            stop_loss_pips=50,
            take_profit_pips=100,
            brick_size=1.0,
            algo_enabled=True
        )
        if result:
            print(f"✅ Added XAUUSD to watchlist (ID: {result['id']})")
            watchlist_id = result['id']
        else:
            print("❌ Failed to add to watchlist")
            watchlist_id = None
    except Exception as e:
        print(f"❌ Error: {e}")
        watchlist_id = None
    
    # Test 4: Get watchlist
    print("\n4️⃣  Testing GET /api/watchlist?account_id=101510620")
    try:
        watchlist = watchlist_manager.get_watchlist(101510620)
        print(f"✅ Watchlist has {len(watchlist)} items")
        for item in watchlist:
            print(f"   - {item['symbol']}: SL={item['stop_loss_pips']}p, TP={item['take_profit_pips']}p, Algo={'ON' if item['algo_enabled'] else 'OFF'}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 5: Update watchlist item
    if watchlist_id:
        print(f"\n5️⃣  Testing PUT /api/watchlist/{watchlist_id}")
        try:
            result = watchlist_manager.update_watchlist_item(
                watchlist_id,
                stop_loss_pips=60,
                take_profit_pips=120
            )
            if result:
                print(f"✅ Updated: SL={result['stop_loss_pips']}p, TP={result['take_profit_pips']}p")
            else:
                print("❌ Failed to update")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Test 6: Toggle algo
    if watchlist_id:
        print(f"\n6️⃣  Testing POST /api/algo/toggle/{watchlist_id}")
        try:
            result = watchlist_manager.toggle_algo(watchlist_id, False)
            if result:
                print(f"✅ Algo disabled: algo_enabled={result['algo_enabled']}")
            else:
                print("❌ Failed to toggle algo")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Test 7: Get algo status
    print("\n7️⃣  Testing GET /api/algo/status/101510620/XAUUSD")
    try:
        settings = watchlist_manager.get_symbol_settings(101510620, "XAUUSD")
        if settings:
            print(f"✅ Algo status: enabled={settings['algo_enabled']}")
            print(f"   SL={settings['stop_loss_pips']}p, TP={settings['take_profit_pips']}p")
        else:
            print("⚠️  Symbol not in watchlist")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 8: Get settings
    print("\n8️⃣  Testing GET /api/settings")
    try:
        result = supabase_client.table('settings').select('*').execute()
        print(f"✅ Found {len(result.data)} global settings")
        for setting in result.data[:3]:
            print(f"   - {setting['setting_key']}: {setting['setting_value']}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 9: Clean up - delete the test item
    if watchlist_id:
        print(f"\n9️⃣  Cleaning up - DELETE /api/watchlist/{watchlist_id}")
        try:
            success = watchlist_manager.remove_from_watchlist(watchlist_id)
            if success:
                print(f"✅ Removed from watchlist")
            else:
                print("❌ Failed to remove")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "="*50)
    print("Test Complete!")
    print("="*50 + "\n")

if __name__ == "__main__":
    asyncio.run(test_endpoints())
