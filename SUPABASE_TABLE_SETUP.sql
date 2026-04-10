-- ============================================================================
-- Supabase Auto-Trading Tables Setup
-- Copy and paste all commands into Supabase SQL Editor to create tables
-- ============================================================================

-- Table 1: Auto-Trading Watchlist
-- Stores symbols enabled for auto-trading with their configuration
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

-- Table 2: Auto-Trading Positions
-- Tracks currently open positions from auto-trading
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

-- Table 3: Auto-Trading History
-- Records all trades executed by auto-trading service
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

-- ============================================================================
-- Create Indexes for Performance
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_auto_trading_watchlist_account 
  ON auto_trading_watchlist(account_id);

CREATE INDEX IF NOT EXISTS idx_auto_trading_watchlist_symbol 
  ON auto_trading_watchlist(symbol);

CREATE INDEX IF NOT EXISTS idx_auto_trading_positions_account 
  ON auto_trading_positions(account_id);

CREATE INDEX IF NOT EXISTS idx_auto_trading_positions_symbol 
  ON auto_trading_positions(symbol);

CREATE INDEX IF NOT EXISTS idx_auto_trading_history_account 
  ON auto_trading_history(account_id);

CREATE INDEX IF NOT EXISTS idx_auto_trading_history_symbol 
  ON auto_trading_history(symbol);

CREATE INDEX IF NOT EXISTS idx_auto_trading_history_created 
  ON auto_trading_history(created_at DESC);

-- ============================================================================
-- Enable RLS (Row-Level Security) if needed
-- ============================================================================

-- Uncomment to enable RLS (requires policies to be defined)
-- ALTER TABLE auto_trading_watchlist ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE auto_trading_positions ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE auto_trading_history ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- Grant Permissions (if using specific roles)
-- ============================================================================

-- Grant all privileges to authenticated users
-- GRANT ALL ON auto_trading_watchlist TO authenticated;
-- GRANT ALL ON auto_trading_positions TO authenticated;
-- GRANT ALL ON auto_trading_history TO authenticated;

-- ============================================================================
-- Sample Data (Optional - for testing)
-- ============================================================================

-- Insert a sample watchlist entry
-- INSERT INTO auto_trading_watchlist (account_id, symbol, enabled, brick_size)
-- VALUES (12345, 'XAUUSD', false, 0.5);

-- ============================================================================
-- Verify Tables Created
-- ============================================================================

-- Run these SELECT statements to verify tables exist:
-- SELECT * FROM auto_trading_watchlist LIMIT 1;
-- SELECT * FROM auto_trading_positions LIMIT 1;
-- SELECT * FROM auto_trading_history LIMIT 1;
