#!/usr/bin/env python
"""Test Supabase and backend configuration"""

import sys
from backend.config import settings
from backend.supabase.client import supabase_client

def test_backend():
    print('🧪 Testing Backend Configuration')
    print('=' * 60)
    
    # Test 1: Config loaded
    print('\n✅ Configuration loaded:')
    print(f'   SUPABASE_URL: {settings.SUPABASE_URL[:40]}...')
    print(f'   MT5_PATH: {settings.MT5_PATH}')
    print(f'   RENKO_BRICK_SIZE: {settings.RENKO_BRICK_SIZE}')
    print(f'   ENVIRONMENT: {settings.environment}')
    
    # Test 2: Supabase connection
    print('\n✅ Testing Supabase connection...')
    try:
        accounts = supabase_client.table('accounts').select('*').limit(1).execute()
        print(f'   ✅ Supabase connected!')
        print(f'   Found {len(accounts.data)} accounts')
    except Exception as e:
        print(f'   ❌ Supabase error: {e}')
        return False
    
    # Test 3: Available symbols
    print('\n✅ Available symbols in database:')
    try:
        symbols = supabase_client.table('available_symbols').select('symbol').execute()
        symbol_list = [s['symbol'] for s in symbols.data]
        print(f'   Total: {len(symbol_list)} symbols')
        print(f'   Examples: {", ".join(symbol_list[:5])}...')
    except Exception as e:
        print(f'   ❌ Error: {e}')
        return False
    
    print('\n' + '=' * 60)
    print('✅ Backend configuration is READY!')
    print('=' * 60)
    return True

if __name__ == '__main__':
    success = test_backend()
    sys.exit(0 if success else 1)
