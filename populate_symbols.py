#!/usr/bin/env python3
"""
Populate Supabase available_symbols table with common forex symbols
Run this once to seed your symbol database
"""

from supabase import create_client
import json

# Your credentials
SUPABASE_URL = "https://mflakcwgbpghyzdyevsb.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1mbGFrY3dnYnBnaHl6ZHlldnNiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU1Nzc3OTQsImV4cCI6MjA5MTE1Mzc5NH0.2Ev5gdEz-9rSgDkKTC_siX_SH5iEfFK6SPM8S8uRx9Q"

# Extended list of common forex and commodities symbols
SYMBOLS = [
    # Precious Metals
    {"symbol": "XAUUSD", "description": "Gold vs USD", "pip_value": 0.01, "is_active": True},
    {"symbol": "XAGUSD", "description": "Silver vs USD", "pip_value": 0.0001, "is_active": True},
    {"symbol": "XPTUSD", "description": "Platinum vs USD", "pip_value": 0.01, "is_active": True},
    {"symbol": "XPDUSD", "description": "Palladium vs USD", "pip_value": 0.01, "is_active": True},
    
    # Major Pairs
    {"symbol": "EURUSD", "description": "EUR vs USD", "pip_value": 0.0001, "is_active": True},
    {"symbol": "GBPUSD", "description": "GBP vs USD", "pip_value": 0.0001, "is_active": True},
    {"symbol": "USDJPY", "description": "USD vs JPY", "pip_value": 0.01, "is_active": True},
    {"symbol": "USDCHF", "description": "USD vs CHF", "pip_value": 0.0001, "is_active": True},
    {"symbol": "AUDUSD", "description": "AUD vs USD", "pip_value": 0.0001, "is_active": True},
    {"symbol": "USRCAD", "description": "USD vs CAD", "pip_value": 0.0001, "is_active": True},
    {"symbol": "NZDUSD", "description": "NZD vs USD", "pip_value": 0.0001, "is_active": True},
    
    # Cross Pairs
    {"symbol": "EURGBP", "description": "EUR vs GBP", "pip_value": 0.0001, "is_active": True},
    {"symbol": "EURJPY", "description": "EUR vs JPY", "pip_value": 0.01, "is_active": True},
    {"symbol": "EURCHF", "description": "EUR vs CHF", "pip_value": 0.0001, "is_active": True},
    {"symbol": "GBPJPY", "description": "GBP vs JPY", "pip_value": 0.01, "is_active": True},
    {"symbol": "GBPCHF", "description": "GBP vs CHF", "pip_value": 0.0001, "is_active": True},
    {"symbol": "AUDJPY", "description": "AUD vs JPY", "pip_value": 0.01, "is_active": True},
    {"symbol": "CADJPY", "description": "CAD vs JPY", "pip_value": 0.01, "is_active": True},
    
    # Commodity Indices
    {"symbol": "US30", "description": "Dow Jones 30", "pip_value": 0.1, "is_active": True},
    {"symbol": "US100", "description": "Nasdaq 100", "pip_value": 0.1, "is_active": True},
    {"symbol": "US500", "description": "S&P 500", "pip_value": 0.1, "is_active": True},
    
    # Cryptocurrencies
    {"symbol": "BTCUSD", "description": "Bitcoin vs USD", "pip_value": 0.01, "is_active": True},
    {"symbol": "ETHUSD", "description": "Ethereum vs USD", "pip_value": 0.0001, "is_active": True},
]

def populate_symbols():
    """Populate symbols table with standard symbols"""
    print("🧪 Connecting to Supabase...")
    try:
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Connected!")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False
    
    print(f"\n📝 Populating {len(SYMBOLS)} symbols...")
    print("-" * 60)
    
    inserted = 0
    skipped = 0
    
    for symbol in SYMBOLS:
        try:
            # Check if symbol already exists
            existing = client.table('available_symbols').select('*').eq('symbol', symbol['symbol']).execute()
            
            if existing.data:
                print(f"  ⏭️  {symbol['symbol']:<12} - ALREADY EXISTS")
                skipped += 1
            else:
                # Insert new symbol
                result = client.table('available_symbols').insert(symbol).execute()
                print(f"  ✅ {symbol['symbol']:<12} - INSERTED ({symbol['description']})")
                inserted += 1
        except Exception as e:
            print(f"  ⚠️  {symbol['symbol']:<12} - ERROR: {str(e)[:50]}")
    
    print("\n" + "=" * 60)
    print(f"✅ RESULTS: {inserted} inserted, {skipped} skipped")
    print("=" * 60)
    
    # Verify
    try:
        all_symbols = client.table('available_symbols').select('*').eq('is_active', True).execute()
        print(f"\n📊 Total active symbols in database: {len(all_symbols.data)}")
        print("\nSymbols available for trading:")
        for sym in all_symbols.data:
            print(f"  • {sym['symbol']:<12} - {sym['description']}")
        return True
    except Exception as e:
        print(f"Error verifying symbols: {e}")
        return False

if __name__ == "__main__":
    import sys
    success = populate_symbols()
    sys.exit(0 if success else 1)
