"""
Verify Supabase Connection and Tables
Run this after you've created the tables in Supabase
"""

from supabase import create_client
import json

# Your credentials
SUPABASE_URL = "https://mflakcwgbpghyzdyevsb.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1mbGFrY3dnYnBnaHl6ZHlldnNiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU1Nzc3OTQsImV4cCI6MjA5MTE1Mzc5NH0.2Ev5gdEz-9rSgDkKTC_siX_SH5iEfFK6SPM8S8uRx9Q"

def test_connection():
    """Test Supabase connection"""
    print("🧪 Testing Supabase Connection...")
    print("=" * 60)
    
    try:
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Connected to Supabase!")
        print(f"📍 Project: mflakcwgbpghyzdyevsb")
        return client
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None

def check_tables(client):
    """Check if all required tables exist"""
    required_tables = [
        'accounts',
        'watchlist', 
        'trades',
        'logs',
        'bot_control',
        'settings',
        'price_ticks',
        'available_symbols'
    ]
    
    print("\n📋 Checking Tables...")
    print("-" * 60)
    
    all_exist = True
    for table_name in required_tables:
        try:
            # Try to query each table
            result = client.table(table_name).select("*").limit(1).execute()
            print(f"  ✅ {table_name:<20} - EXISTS")
        except Exception as e:
            print(f"  ❌ {table_name:<20} - MISSING")
            all_exist = False
    
    return all_exist

def check_data(client):
    """Check if there's any sample data"""
    print("\n📊 Checking Data...")
    print("-" * 60)
    
    try:
        accounts = client.table('accounts').select("*").execute()
        print(f"  Accounts: {len(accounts.data)} record(s)")
        
        symbols = client.table('available_symbols').select("*").execute()
        print(f"  Available Symbols: {len(symbols.data)} record(s)")
        if symbols.data:
            print(f"    Sample: {symbols.data[0]['symbol']}")
        
        trades = client.table('trades').select("*").execute()
        print(f"  Trades: {len(trades.data)} record(s)")
        
        return True
    except Exception as e:
        print(f"  ⚠️  Error reading data: {e}")
        return False

def main():
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + "RENKO BOT - SUPABASE VERIFICATION".center(58) + "║")
    print("╚" + "=" * 58 + "╝")
    
    # Test connection
    client = test_connection()
    if not client:
        print("\n❌ Cannot proceed without connection!")
        return False
    
    # Check tables
    all_exist = check_tables(client)
    
    if all_exist:
        print("\n" + "=" * 60)
        print("✅ ALL TABLES EXIST!")
        print("=" * 60)
        
        # Check data
        check_data(client)
        
        print("\n" + "=" * 60)
        print("✅ Setup Status: READY TO USE")
        print("=" * 60)
        print("\n📝 Next Steps:")
        print("  1. Update .env file with your Supabase credentials")
        print("  2. Start the backend: uvicorn backend.main:app --reload")
        print("  3. Start the frontend: npm run dev")
        print("\n✨ You're all set!")
        return True
    else:
        print("\n" + "=" * 60)
        print("❌ Some tables are missing!")
        print("=" * 60)
        print("\n📝 Please follow SUPABASE_QUICK_SETUP.md to create tables:")
        print("  File: SUPABASE_QUICK_SETUP.md")
        print("  Steps: Copy schema.sql into Supabase SQL Editor and RUN")
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
