#!/usr/bin/env python
"""Debug script to check API and database"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from backend.supabase.client import supabase_client
    print("✅ Supabase client imported")
    
    # Check accounts
    print("\nChecking accounts...")
    result = supabase_client.table('accounts').select('*').execute()
    print(f"✅ Found {len(result.data)} accounts:")
    for acc in result.data:
        print(f"   - Login: {acc['login']}, Server: {acc['server']}, Status: {acc['status']}")
    
    if not result.data:
        print("\n⚠️  No accounts in database!")
        print("Need to create an account with login 101510620")
        
        # Create account
        try:
            create_result = supabase_client.table('accounts').insert({
                'login': 101510620,
                'server': 'XMGlobal-MT5 5',
                'status': 'active',
                'balance': 10000.0
            }).execute()
            print(f"✅ Created account: {create_result.data[0]['login']}")
        except Exception as e:
            print(f"❌ Failed to create account: {e}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
