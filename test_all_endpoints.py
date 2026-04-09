#!/usr/bin/env python
"""
Test all backend endpoints including new account and trade endpoints
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from backend.config import settings
from backend.supabase.client import supabase_client

def test_endpoints():
    print("\n" + "="*60)
    print("🧪 Testing All Backend Endpoints")
    print("="*60 + "\n")
    
    # Test 1: Get accounts
    print("1️⃣  Testing GET /api/accounts")
    try:
        result = supabase_client.table('accounts').select('*').execute()
        print(f"✅ Found {len(result.data)} accounts")
        for acc in result.data[:3]:
            print(f"   - Login: {acc['login']}, Server: {acc['server']}, Status: {acc['status']}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Get trades
    print("\n2️⃣  Testing GET /api/trades")
    try:
        result = supabase_client.table('trades').select('*').order('created_at', desc=True).execute()
        print(f"✅ Found {len(result.data)} trades")
        for trade in result.data[:3]:
            print(f"   - {trade['symbol']} {trade['type'].upper()} @ {trade['entry_price']} (ID: {trade['id']})")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Get settings
    print("\n3️⃣  Testing GET /api/settings")
    try:
        result = supabase_client.table('settings').select('*').execute()
        print(f"✅ Found {len(result.data)} settings")
        for setting in result.data[:3]:
            print(f"   - {setting['setting_key']}: {setting['setting_value']}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Get bot control status
    print("\n4️⃣  Testing GET /api/bot-control")
    try:
        result = supabase_client.table('bot_control').select('*').execute()
        print(f"✅ Found {len(result.data)} bot control records")
        for rec in result.data:
            status = "RUNNING" if rec['is_running'] else "STOPPED"
            print(f"   - Account {rec['account_id']}: {status}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 5: Create a trade
    print("\n5️⃣  Testing POST /api/trades (Create Trade)")
    try:
        # Get an account first
        acc_result = supabase_client.table('accounts').select('login').limit(1).execute()
        if acc_result.data:
            account_id = acc_result.data[0]['login']
            
            trade_data = {
                'account_id': account_id,
                'symbol': 'XAUUSD',
                'type': 'buy',
                'lot': 0.01,
                'entry_price': 2050.50,
                'sl_price': 2040.00,
                'tp_price': 2070.00,
                'brick_size': 1.0,
                'closed': False
            }
            
            result = supabase_client.table('trades').insert(trade_data).execute()
            if result.data:
                trade_id = result.data[0]['id']
                print(f"✅ Created trade ID: {trade_id}")
                print(f"   Symbol: {trade_data['symbol']}, Type: {trade_data['type'].upper()}")
                print(f"   Entry: {trade_data['entry_price']}, SL: {trade_data['sl_price']}, TP: {trade_data['tp_price']}")
                
                # Test 6: Get the created trade
                print(f"\n6️⃣  Testing GET /api/trades/{{id}} - Get Trade {trade_id}")
                trade_result = supabase_client.table('trades').select('*').eq('id', trade_id).execute()
                if trade_result.data:
                    t = trade_result.data[0]
                    print(f"✅ Retrieved trade: {t['symbol']} {t['type'].upper()} @ {t['entry_price']}")
                    
                    # Test 7: Update trade (close it)
                    print(f"\n7️⃣  Testing PUT /api/trades/{{id}} - Close Trade")
                    update_result = supabase_client.table('trades').update({
                        'closed': True,
                        'exit_price': 2060.00,
                        'profit': 100.00,
                        'exit_reason': 'tp_hit'
                    }).eq('id', trade_id).execute()
                    if update_result.data:
                        print(f"✅ Closed trade - Profit: {update_result.data[0]['profit']}")
                        # Clean up - delete the test trade
                        supabase_client.table('trades').delete().eq('id', trade_id).execute()
                        print(f"✅ Cleaned up test trade")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 8: Get tickers
    print("\n8️⃣  Testing GET /api/tickers")
    try:
        result = supabase_client.table('available_symbols').select('*').eq('is_active', True).execute()
        print(f"✅ Found {len(result.data)} available symbols")
        for sym in result.data[:3]:
            print(f"   - {sym['symbol']}: {sym['description']}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*60)
    print("✨ Tests Complete!")
    print("="*60 + "\n")

if __name__ == "__main__":
    test_endpoints()
