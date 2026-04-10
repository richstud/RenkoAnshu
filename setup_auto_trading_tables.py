"""
Create Supabase tables for auto-trading system using REST API.
Run this script to initialize the database schema.
"""

import os
import sys
import json
from pathlib import Path

# Load environment
from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: SUPABASE_URL and SUPABASE_KEY not found in .env")
    sys.exit(1)

print(f"Connecting to Supabase: {SUPABASE_URL}")

# Try using supabase-py if available
try:
    from supabase import create_client
    
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # SQL to create tables
    sql_commands = [
        """CREATE TABLE IF NOT EXISTS auto_trading_watchlist (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  account_id INT NOT NULL,
  symbol VARCHAR(20) NOT NULL,
  enabled BOOLEAN DEFAULT FALSE,
  brick_size FLOAT DEFAULT 0.005,
  lot_size_rules JSONB DEFAULT '{"balance_less_100": 0.001, "balance_101_500": 0.01, "balance_501_plus": 0.1}',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(account_id, symbol)
)""",
        """CREATE TABLE IF NOT EXISTS auto_trading_positions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  account_id INT NOT NULL,
  symbol VARCHAR(20) NOT NULL,
  ticket INT NOT NULL,
  position VARCHAR(10),
  entry_price FLOAT,
  lot_size FLOAT,
  opened_at TIMESTAMP,
  status VARCHAR(20) DEFAULT 'OPEN',
  UNIQUE(account_id, symbol)
)""",
        """CREATE TABLE IF NOT EXISTS auto_trading_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  account_id INT NOT NULL,
  symbol VARCHAR(20) NOT NULL,
  direction VARCHAR(10),
  entry_price FLOAT,
  entry_time TIMESTAMP,
  exit_price FLOAT,
  exit_time TIMESTAMP,
  lot_size FLOAT,
  pnl FLOAT,
  reason VARCHAR(100),
  created_at TIMESTAMP DEFAULT NOW()
)""",
        """CREATE INDEX IF NOT EXISTS idx_auto_trading_watchlist_account ON auto_trading_watchlist(account_id)""",
        """CREATE INDEX IF NOT EXISTS idx_auto_trading_positions_symbol ON auto_trading_positions(symbol)""",
        """CREATE INDEX IF NOT EXISTS idx_auto_trading_history_account ON auto_trading_history(account_id)"""
    ]
    
    # Execute each command using RPC or raw query
    headers = {
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    import httpx
    client = httpx.Client(headers=headers)
    
    print("\nCreating tables...")
    for i, sql in enumerate(sql_commands, 1):
        try:
            # Use Supabase's admin API for raw SQL execution
            response = client.post(
                f"{SUPABASE_URL}/rest/v1/rpc/exec_sql",
                json={"query": sql}
            )
            if response.status_code in [200, 201]:
                print(f"  [OK] Command {i}")
            else:
                print(f"  [INFO] Command {i}: {response.text}")
        except Exception as e:
            print(f"  [INFO] Command {i}: {str(e)}")
    
    client.close()
    
    # Verify tables were created
    print("\nVerifying tables...")
    try:
        # Test auto_trading_watchlist
        supabase.table('auto_trading_watchlist').select('*').limit(1).execute()
        print("  [OK] auto_trading_watchlist exists")
    except Exception as e:
        print(f"  [WARN] auto_trading_watchlist: {e}")
    
    try:
        # Test auto_trading_positions
        supabase.table('auto_trading_positions').select('*').limit(1).execute()
        print("  [OK] auto_trading_positions exists")
    except Exception as e:
        print(f"  [WARN] auto_trading_positions: {e}")
    
    try:
        # Test auto_trading_history
        supabase.table('auto_trading_history').select('*').limit(1).execute()
        print("  [OK] auto_trading_history exists")
    except Exception as e:
        print(f"  [WARN] auto_trading_history: {e}")
    
    print("\nDone!")

except ImportError:
    print("ERROR: supabase-py not installed. Install with: pip install supabase")
    print("\nAlternatively, copy and run these SQL commands in Supabase SQL Editor:")
    print("=" * 70)
    
    sql_commands = [
        """CREATE TABLE IF NOT EXISTS auto_trading_watchlist (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  account_id INT NOT NULL,
  symbol VARCHAR(20) NOT NULL,
  enabled BOOLEAN DEFAULT FALSE,
  brick_size FLOAT DEFAULT 0.005,
  lot_size_rules JSONB DEFAULT '{"balance_less_100": 0.001, "balance_101_500": 0.01, "balance_501_plus": 0.1}',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(account_id, symbol)
);""",
        """CREATE TABLE IF NOT EXISTS auto_trading_positions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  account_id INT NOT NULL,
  symbol VARCHAR(20) NOT NULL,
  ticket INT NOT NULL,
  position VARCHAR(10),
  entry_price FLOAT,
  lot_size FLOAT,
  opened_at TIMESTAMP,
  status VARCHAR(20) DEFAULT 'OPEN',
  UNIQUE(account_id, symbol)
);""",
        """CREATE TABLE IF NOT EXISTS auto_trading_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  account_id INT NOT NULL,
  symbol VARCHAR(20) NOT NULL,
  direction VARCHAR(10),
  entry_price FLOAT,
  entry_time TIMESTAMP,
  exit_price FLOAT,
  exit_time TIMESTAMP,
  lot_size FLOAT,
  pnl FLOAT,
  reason VARCHAR(100),
  created_at TIMESTAMP DEFAULT NOW()
);""",
        """CREATE INDEX IF NOT EXISTS idx_auto_trading_watchlist_account ON auto_trading_watchlist(account_id);""",
        """CREATE INDEX IF NOT EXISTS idx_auto_trading_positions_symbol ON auto_trading_positions(symbol);""",
        """CREATE INDEX IF NOT EXISTS idx_auto_trading_history_account ON auto_trading_history(account_id);"""
    ]
    
    for sql in sql_commands:
        print(sql)
    print("=" * 70)
    sys.exit(1)
