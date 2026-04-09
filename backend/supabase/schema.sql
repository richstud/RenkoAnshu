-- ===================================
-- RENKO TRADING BOT SCHEMA
-- ===================================

-- Enable UUID and JSON extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ===================================
-- ACCOUNTS TABLE
-- ===================================
CREATE TABLE IF NOT EXISTS accounts (
    id BIGSERIAL PRIMARY KEY,
    login BIGINT NOT NULL UNIQUE,
    server TEXT NOT NULL,
    status TEXT DEFAULT 'active',
    balance FLOAT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_accounts_login ON accounts(login);


-- ===================================
-- WATCHLIST TABLE
-- ===================================
CREATE TABLE IF NOT EXISTS watchlist (
    id BIGSERIAL PRIMARY KEY,
    account_id BIGINT NOT NULL REFERENCES accounts(login) ON DELETE CASCADE,
    symbol TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true,
    
    -- Trading Parameters (per symbol)
    lot_size FLOAT DEFAULT 0.01,
    stop_loss_pips FLOAT DEFAULT 50,           -- SL in pips/points
    take_profit_pips FLOAT DEFAULT 100,        -- TP in pips/points
    trailing_stop_pips FLOAT DEFAULT 30,       -- Trailing SL in pips/points
    use_trailing_stop BOOLEAN DEFAULT false,   -- Enable trailing stop?
    
    -- Custom Brick Size (per symbol)
    brick_size FLOAT DEFAULT 1.0,
    
    -- Algo Control (per symbol)
    algo_enabled BOOLEAN DEFAULT true,         -- Is this symbol's algo enabled?
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(account_id, symbol)
);

CREATE INDEX idx_watchlist_account ON watchlist(account_id);
CREATE INDEX idx_watchlist_symbol ON watchlist(symbol);
CREATE INDEX idx_watchlist_active ON watchlist(is_active);


-- ===================================
-- TRADES TABLE
-- ===================================
CREATE TABLE IF NOT EXISTS trades (
    id BIGSERIAL PRIMARY KEY,
    account_id BIGINT NOT NULL REFERENCES accounts(login) ON DELETE CASCADE,
    symbol TEXT NOT NULL,
    type TEXT NOT NULL,                    -- 'buy' or 'sell'
    lot FLOAT NOT NULL,
    entry_price FLOAT NOT NULL,
    entry_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Exit info
    exit_price FLOAT,
    exit_time TIMESTAMP WITH TIME ZONE,
    
    -- PnL
    profit FLOAT,                          -- P&L in points or currency
    profit_percent FLOAT,
    
    -- SL/TP hit info
    sl_price FLOAT,                        -- Stop loss price that was set
    tp_price FLOAT,                        -- Take profit price that was set
    exit_reason TEXT,                      -- 'sl_hit', 'tp_hit', 'manual_close'
    
    -- Brick info
    brick_size FLOAT DEFAULT 1.0,
    
    closed BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_trades_account ON trades(account_id);
CREATE INDEX idx_trades_symbol ON trades(symbol);
CREATE INDEX idx_trades_closed ON trades(closed);
CREATE INDEX idx_trades_created ON trades(created_at DESC);


-- ===================================
-- LOGS TABLE
-- ===================================
CREATE TABLE IF NOT EXISTS logs (
    id BIGSERIAL PRIMARY KEY,
    account_id BIGINT REFERENCES accounts(login) ON DELETE SET NULL,
    event TEXT NOT NULL,
    log_level TEXT DEFAULT 'INFO',         -- 'INFO', 'WARN', 'ERROR', 'DEBUG'
    symbol TEXT,                           -- Optional, for symbol-specific logs
    details JSONB,                         -- JSON data for extra info
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_logs_account ON logs(account_id);
CREATE INDEX idx_logs_symbol ON logs(symbol);
CREATE INDEX idx_logs_created ON logs(created_at DESC);


-- ===================================
-- BOT CONTROL TABLE
-- ===================================
CREATE TABLE IF NOT EXISTS bot_control (
    id BIGSERIAL PRIMARY KEY,
    account_id BIGINT REFERENCES accounts(login) ON DELETE CASCADE,
    is_running BOOLEAN DEFAULT false,
    brick_size FLOAT DEFAULT 1.0,
    poll_interval FLOAT DEFAULT 0.5,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(account_id)
);

CREATE INDEX idx_bot_control_account ON bot_control(account_id);


-- ===================================
-- SETTINGS TABLE (Global)
-- ===================================
CREATE TABLE IF NOT EXISTS settings (
    id BIGSERIAL PRIMARY KEY,
    setting_key TEXT NOT NULL UNIQUE,
    setting_value TEXT,
    description TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Default settings
INSERT INTO settings (setting_key, setting_value, description) VALUES
    ('default_brick_size', '1.0', 'Default Renko brick size in pips'),
    ('default_sl_pips', '50', 'Default stop loss in pips'),
    ('default_tp_pips', '100', 'Default take profit in pips'),
    ('default_lot_size', '0.01', 'Default lot size'),
    ('max_positions_per_account', '10', 'Maximum concurrent positions per account'),
    ('enable_trailing_stops', 'true', 'Enable trailing stop functionality'),
    ('log_retention_days', '30', 'Days to keep logs')
ON CONFLICT (setting_key) DO NOTHING;


-- ===================================
-- PRICE TICKERS TABLE
-- ===================================
CREATE TABLE IF NOT EXISTS price_ticks (
    id BIGSERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,
    bid FLOAT NOT NULL,
    ask FLOAT NOT NULL,
    last_update TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_price_ticks_symbol ON price_ticks(symbol);


-- ===================================
-- AVAILABLE SYMBOLS TABLE
-- ===================================
CREATE TABLE IF NOT EXISTS available_symbols (
    id BIGSERIAL PRIMARY KEY,
    symbol TEXT NOT NULL UNIQUE,
    description TEXT,
    pip_value FLOAT DEFAULT 0.01,          -- Pip size (0.01 for most, 0.0001 for spot)
    point_value FLOAT DEFAULT 1.0,         -- Value per point
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Pre-populate some common symbols
INSERT INTO available_symbols (symbol, description, pip_value) VALUES
    ('XAUUSD', 'Gold vs USD', 0.01),
    ('EURUSD', 'EUR vs USD', 0.0001),
    ('GBPUSD', 'GBP vs USD', 0.0001),
    ('USDJPY', 'USD vs JPY', 0.01),
    ('AUDUSD', 'AUD vs USD', 0.0001),
    ('NZDUSD', 'NZD vs USD', 0.0001),
    ('USDCAD', 'USD vs CAD', 0.0001)
ON CONFLICT (symbol) DO NOTHING;

CREATE INDEX idx_available_symbols_active ON available_symbols(is_active);


-- ===================================
-- RLS (Row Level Security) - Optional
-- ===================================
-- You can enable RLS if using Supabase auth, for now keeping it simple

-- Enable RLS on all tables (uncomment if using Supabase auth)
-- ALTER TABLE accounts ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE watchlist ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE trades ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE logs ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE bot_control ENABLE ROW LEVEL SECURITY;


-- ===================================
-- VIEWS (Optional, for easier queries)
-- ===================================

-- View for active positions
CREATE OR REPLACE VIEW active_positions AS
SELECT 
    t.id,
    a.login,
    a.server,
    t.symbol,
    t.type,
    t.lot,
    t.entry_price,
    t.entry_time,
    t.sl_price,
    t.tp_price,
    CASE WHEN t.type = 'buy' THEN (pt.bid - t.entry_price) ELSE (t.entry_price - pt.ask) END as points_from_entry,
    pt.bid,
    pt.ask
FROM trades t
JOIN accounts a ON t.account_id = a.login
LEFT JOIN price_ticks pt ON t.symbol = pt.symbol
WHERE t.closed = false
ORDER BY t.entry_time DESC;


-- View for trade statistics
CREATE OR REPLACE VIEW trade_stats AS
SELECT 
    account_id,
    symbol,
    COUNT(*) as total_trades,
    SUM(CASE WHEN type = 'buy' THEN 1 ELSE 0 END) as buy_trades,
    SUM(CASE WHEN type = 'sell' THEN 1 ELSE 0 END) as sell_trades,
    SUM(CASE WHEN closed = true AND profit > 0 THEN 1 ELSE 0 END) as winning_trades,
    SUM(CASE WHEN closed = true AND profit <= 0 THEN 1 ELSE 0 END) as losing_trades,
    ROUND(SUM(profit)::numeric, 2) as total_profit,
    ROUND(AVG(profit)::numeric, 2) as avg_profit
FROM trades
GROUP BY account_id, symbol;
