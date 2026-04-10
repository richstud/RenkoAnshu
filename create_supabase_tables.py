#!/usr/bin/env python3
"""
Create auto-trading tables in Supabase using direct SQL execution.
Usage: python create_supabase_tables.py
"""

import os
import sys
from pathlib import Path

def load_env():
    """Load environment variables from .env"""
    env_file = Path(__file__).parent / '.env'
    if not env_file.exists():
        print("ERROR: .env file not found")
        return None, None
    
    with open(env_file) as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value.strip('"\'')
    
    return os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY')

def main():
    supabase_url, supabase_key = load_env()
    
    if not supabase_url or not supabase_key:
        print("ERROR: SUPABASE_URL or SUPABASE_KEY not set")
        sys.exit(1)
    
    print(f"Using Supabase: {supabase_url}")
    
    # Try importing httpx for direct HTTP API calls
    try:
        import httpx
    except ImportError:
        print("Installing httpx...")
        os.system(f"{sys.executable} -m pip install -q httpx")
        import httpx
    
    # SQL Commands
    sql_commands = [
        # Table 1: Watchlist
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
        
        # Table 2: Positions
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
        
        # Table 3: History
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
        
        # Indexes
        """CREATE INDEX IF NOT EXISTS idx_auto_trading_watchlist_account ON auto_trading_watchlist(account_id)""",
        """CREATE INDEX IF NOT EXISTS idx_auto_trading_positions_symbol ON auto_trading_positions(symbol)""",
        """CREATE INDEX IF NOT EXISTS idx_auto_trading_history_account ON auto_trading_history(account_id)"""
    ]
    
    # Use httpx to make direct requests to Supabase REST API
    headers = {
        "Authorization": f"Bearer {supabase_key}",
        "apikey": supabase_key,
    }
    
    with httpx.Client(headers=headers, timeout=30.0) as client:
        print("\nExecuting SQL commands...")
        
        for i, sql in enumerate(sql_commands, 1):
            try:
                # Try RPC call first (requires function to exist)
                # Fall back to direct table operations
                
                # For table creation, we'll use a direct approach
                response = client.get(
                    f"{supabase_url}/rest/v1/?limit=0",
                )
                
                if response.status_code == 200:
                    print(f"  [{i}] Connection OK")
                else:
                    print(f"  [{i}] Status: {response.status_code}")
                    
            except Exception as e:
                print(f"  [{i}] Error: {e}")
    
    print("\n" + "="*70)
    print("NOTE: Direct SQL execution requires a Supabase function.")
    print("Please run the following SQL in Supabase SQL Editor instead:")
    print("="*70 + "\n")
    
    for sql in sql_commands:
        print(sql + ";")
        print()

if __name__ == '__main__':
    main()
