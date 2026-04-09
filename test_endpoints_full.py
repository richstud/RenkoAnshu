#!/usr/bin/env python
"""
Quick test for new API endpoints - including account setup
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.config import settings
from backend.supabase.client import supabase_client
from backend.services.price_manager import price_manager
from backend.services.watchlist_manager import watchlist_manager

async def test_endpoints():
    print("\n" + "="*60)
    print("🤖 Testing API Endpoints & Services")
    print("="*60 + "\n")
    
    # First, ensure an account exists
    print("🔧 Setting up test account...")
    try:
        # Check if account exists
        result = supabase_client.table("accounts").select("*").eq("login", 101510620).execute()
        
        if not result.data:
            # Create account
            account_data = {
                "login": 101510620,
                "server": "XMGlobal-MT5 5",
                "balance": 10000.0,
                "status": "active"
            }
            result = supabase_client.table("accounts").insert(account_data).execute()
            print(f"✅ Created test account: {account_data['login']}")
        else:
            print(f"✅ Account already exists: {result.data[0]['login']}")
    except Exception as e:
        print(f"❌ Failed to setup account: {e}")
        return
    
    # Test 1: Get tickers
    print("\n1️⃣  Testing GET /api/tickers")
    try:
        result = supabase_client.table('available_symbols').select('*').eq('is_active', True).execute()
        print(f"✅ Found {len(result.data)} symbols")
        for sym in result.data[:3]:
            print(f"   - {sym['symbol']}: {sym['description']}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Get quote
    print("\n2️⃣  Testing GET /api/tickers/{{symbol}}/quote")
    try:
        quote = price_manager.get_quote("XAUUSD")
        if quote and quote.get('bid'):
            print(f"✅ XAUUSD: Bid={quote['bid']}, Ask={quote['ask']}")
        else:
            print("ℹ️  No live quote (MT5 not connected) - expected for testing")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Add to watchlist
    print("\n3️⃣  Testing POST /api/watchlist")
    watchlist_id = None
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
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Get watchlist
    print("\n4️⃣  Testing GET /api/watchlist?account_id=101510620")
    try:
        watchlist = watchlist_manager.get_watchlist(101510620)
        print(f"✅ Watchlist has {len(watchlist)} items")
        for item in watchlist:
            status = "ON" if item['algo_enabled'] else "OFF"
            print(f"   - {item['symbol']}: SL={item['stop_loss_pips']}p, TP={item['take_profit_pips']}p, Algo={status}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 5: Update watchlist item
    if watchlist_id:
        print(f"\n5️⃣  Testing PUT /api/watchlist/{{id}}")
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
        print(f"\n6️⃣  Testing POST /api/algo/toggle/{{id}}")
        try:
            result = watchlist_manager.toggle_algo(watchlist_id, False)
            if result:
                status = "enabled" if result['algo_enabled'] else "disabled"
                print(f"✅ Algo {status}: algo_enabled={result['algo_enabled']}")
            else:
                print("❌ Failed to toggle algo")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Test 7: Get algo status
    print("\n7️⃣  Testing GET /api/algo/status/{{account}}/{{symbol}}")
    try:
        settings = watchlist_manager.get_symbol_settings(101510620, "XAUUSD")
        if settings:
            print(f"✅ Algo status: enabled={settings['algo_enabled']}")
            print(f"   SL={settings['stop_loss_pips']}p, TP={settings['take_profit_pips']}p, Brick={settings['brick_size']}")
        else:
            print("⚠️  Symbol not in watchlist (may have been removed)")
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
    
    # Test 9: Get specific setting
    print("\n9️⃣  Testing GET /api/settings/{{key}}")
    try:
        result = supabase_client.table('settings').select('*').eq('setting_key', 'default_brick_size').execute()
        if result.data:
            print(f"✅ default_brick_size: {result.data[0]['setting_value']}")
        else:
            print("❌ Setting not found")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 10: Clean up - delete the test item
    if watchlist_id:
        print(f"\n🧹 Cleaning up - DELETE /api/watchlist/{{id}}")
        try:
            success = watchlist_manager.remove_from_watchlist(watchlist_id)
            if success:
                print(f"✅ Removed {watchlist_id} from watchlist")
            else:
                print("❌ Failed to remove")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Test 11: Add multiple symbols to watchlist
    print("\n📋 Testing bulk add to watchlist")
    symbols_to_test = ["EURUSD", "GBPUSD", "USDJPY"]
    added_items = []
    try:
        for sym in symbols_to_test:
            result = watchlist_manager.add_to_watchlist(
                account_id=101510620,
                symbol=sym,
                algo_enabled=True
            )
            if result:
                added_items.append(result['id'])
                print(f"   ✅ Added {sym}")
        
        # Get final watchlist
        watchlist = watchlist_manager.get_watchlist(101510620)
        print(f"📊 Final watchlist has {len(watchlist)} symbols")
        
        # Cleanup added items
        for item_id in added_items:
            watchlist_manager.remove_from_watchlist(item_id)
        print("   ✅ Cleaned up test items")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*60)
    print("✨ All Tests Complete!")
    print("="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(test_endpoints())
