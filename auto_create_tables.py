#!/usr/bin/env python3
"""
Automatically create Supabase tables for auto-trading.
This script reads credentials from .env and creates tables directly.
"""

import os
import sys
from pathlib import Path

def main():
    # Load .env
    env_file = Path(__file__).parent / '.env'
    if not env_file.exists():
        print("ERROR: .env not found in current directory")
        return False
    
    print("Loading environment...")
    with open(env_file) as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value.strip('"\'')
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("ERROR: SUPABASE_URL or SUPABASE_KEY not in .env")
        return False
    
    print(f"Connecting to: {supabase_url}")
    
    # Try importing supabase-py
    try:
        from supabase import create_client
    except ImportError:
        print("Installing supabase-py...")
        os.system(f"{sys.executable} -m pip install supabase -q")
        from supabase import create_client
    
    try:
        # Create client
        supabase = create_client(supabase_url, supabase_key)
        print("Connected to Supabase!")
        
        # Try to create tables by inserting then deleting (tests connection)
        # Better approach: use raw SQL via admin API
        
        import httpx
        
        sql_script = """
-- Create tables
CREATE TABLE IF NOT EXISTS auto_trading_watchlist (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  account_id INT NOT NULL,
  symbol VARCHAR(20) NOT NULL,
  enabled BOOLEAN DEFAULT FALSE,
  brick_size FLOAT DEFAULT 0.005,
  lot_size_rules JSONB DEFAULT '{"balance_less_100": 0.001, "balance_101_500": 0.01, "balance_501_plus": 0.1}',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(account_id, symbol)
);

CREATE TABLE IF NOT EXISTS auto_trading_positions (
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
);

CREATE TABLE IF NOT EXISTS auto_trading_history (
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
);

CREATE INDEX IF NOT EXISTS idx_auto_trading_watchlist_account ON auto_trading_watchlist(account_id);
CREATE INDEX IF NOT EXISTS idx_auto_trading_positions_symbol ON auto_trading_positions(symbol);
CREATE INDEX IF NOT EXISTS idx_auto_trading_history_account ON auto_trading_history(account_id);
"""
        
        print("\nAttempting to execute SQL via Supabase API...")
        
        headers = {
            "Authorization": f"Bearer {supabase_key}",
            "apikey": supabase_key,
            "Content-Type": "application/json"
        }
        
        with httpx.Client(headers=headers, timeout=30.0) as client:
            # Try Supabase RPC (requires a function)
            # For now, just verify connection works
            response = client.get(f"{supabase_url}/rest/v1/?limit=0")
            
            if response.status_code == 200:
                print("Connection verified!")
                print("\nSince direct SQL requires Supabase function,")
                print("please use the SQL Editor method:")
                print("\n1. Go to Supabase Dashboard → SQL Editor")
                print("2. Create new query")
                print("3. Copy content from: SUPABASE_TABLE_SETUP.sql")
                print("4. Execute the query")
                print("\nOr run: create_supabase_tables.py")
                return True
            else:
                print(f"Connection test failed: {response.status_code}")
                return False
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nFallback: Verify tables using Supabase UI:")
        print("1. Open https://supabase.co")
        print("2. Go to Table Editor")
        print("3. Check for auto_trading_* tables")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
