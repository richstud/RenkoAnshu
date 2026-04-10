-- ===================================================================
-- ADD ONLY THE AUTO-TRADING TABLES (Missing from your schema)
-- These 3 tables are new and don't exist yet in your database
-- ===================================================================

-- Table 1: Auto-Trading Watchlist
-- Stores which symbols are enabled for auto-trading
CREATE TABLE IF NOT EXISTS auto_trading_watchlist (
    id BIGSERIAL PRIMARY KEY,
    account_id BIGINT NOT NULL REFERENCES accounts(login) ON DELETE CASCADE,
    symbol TEXT NOT NULL,
    enabled BOOLEAN DEFAULT FALSE,
    brick_size FLOAT DEFAULT 0.005,
    lot_size_rules JSONB DEFAULT '{"balance_less_100": 0.001, "balance_101_500": 0.01, "balance_501_plus": 0.1}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(account_id, symbol)
);

-- Table 2: Auto-Trading Positions
-- Tracks currently open positions from auto-trading
CREATE TABLE IF NOT EXISTS auto_trading_positions (
    id BIGSERIAL PRIMARY KEY,
    account_id BIGINT NOT NULL REFERENCES accounts(login) ON DELETE CASCADE,
    symbol TEXT NOT NULL,
    ticket INT NOT NULL,
    position VARCHAR(10),
    entry_price FLOAT,
    lot_size FLOAT,
    opened_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'OPEN',
    UNIQUE(account_id, symbol)
);

-- Table 3: Auto-Trading History
-- Records all trades executed by auto-trading
CREATE TABLE IF NOT EXISTS auto_trading_history (
    id BIGSERIAL PRIMARY KEY,
    account_id BIGINT NOT NULL REFERENCES accounts(login) ON DELETE CASCADE,
    symbol TEXT NOT NULL,
    direction VARCHAR(10),
    entry_price FLOAT,
    entry_time TIMESTAMP WITH TIME ZONE,
    exit_price FLOAT,
    exit_time TIMESTAMP WITH TIME ZONE,
    lot_size FLOAT,
    pnl FLOAT,
    reason VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ===================================================================
-- CREATE INDEXES FOR PERFORMANCE
-- ===================================================================

CREATE INDEX IF NOT EXISTS idx_auto_trading_watchlist_account ON auto_trading_watchlist(account_id);
CREATE INDEX IF NOT EXISTS idx_auto_trading_watchlist_symbol ON auto_trading_watchlist(symbol);
CREATE INDEX IF NOT EXISTS idx_auto_trading_positions_account ON auto_trading_positions(account_id);
CREATE INDEX IF NOT EXISTS idx_auto_trading_positions_symbol ON auto_trading_positions(symbol);
CREATE INDEX IF NOT EXISTS idx_auto_trading_history_account ON auto_trading_history(account_id);
CREATE INDEX IF NOT EXISTS idx_auto_trading_history_symbol ON auto_trading_history(symbol);
CREATE INDEX IF NOT EXISTS idx_auto_trading_history_created ON auto_trading_history(created_at DESC);

-- ===================================================================
-- DONE! Now you have all the tables needed for auto-trading
-- ===================================================================
