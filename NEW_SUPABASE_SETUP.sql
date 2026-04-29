-- ================================================================
-- RENKO TRADING BOT — COMPLETE NEW SUPABASE SETUP
-- Paste this entire script into:
-- https://supabase.com/dashboard/project/mlygvqsakitopuluxplh/sql
-- ================================================================

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ================================================================
-- 1. ACCOUNTS TABLE
-- ================================================================
CREATE TABLE IF NOT EXISTS accounts (
    id BIGSERIAL PRIMARY KEY,
    login BIGINT NOT NULL UNIQUE,
    server TEXT NOT NULL,
    status TEXT DEFAULT 'active',
    balance FLOAT DEFAULT 0,
    password TEXT DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_accounts_login ON accounts(login);

-- ================================================================
-- 2. WATCHLIST TABLE
-- ================================================================
CREATE TABLE IF NOT EXISTS watchlist (
    id BIGSERIAL PRIMARY KEY,
    account_id BIGINT NOT NULL REFERENCES accounts(login) ON DELETE CASCADE,
    symbol TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true,
    lot_size FLOAT DEFAULT 0.01,
    stop_loss_pips FLOAT DEFAULT 50,
    take_profit_pips FLOAT DEFAULT 100,
    trailing_stop_pips FLOAT DEFAULT 30,
    use_trailing_stop BOOLEAN DEFAULT false,
    brick_size FLOAT DEFAULT 1.0,
    algo_enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(account_id, symbol)
);
CREATE INDEX IF NOT EXISTS idx_watchlist_account ON watchlist(account_id);
CREATE INDEX IF NOT EXISTS idx_watchlist_symbol ON watchlist(symbol);
CREATE INDEX IF NOT EXISTS idx_watchlist_active ON watchlist(is_active);

-- ================================================================
-- 3. TRADES TABLE
-- ================================================================
CREATE TABLE IF NOT EXISTS trades (
    id BIGSERIAL PRIMARY KEY,
    account_id BIGINT NOT NULL REFERENCES accounts(login) ON DELETE CASCADE,
    symbol TEXT NOT NULL,
    type TEXT NOT NULL,
    lot FLOAT NOT NULL,
    entry_price FLOAT NOT NULL,
    entry_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    exit_price FLOAT,
    exit_time TIMESTAMP WITH TIME ZONE,
    profit FLOAT,
    profit_percent FLOAT,
    sl_price FLOAT,
    tp_price FLOAT,
    exit_reason TEXT,
    brick_size FLOAT DEFAULT 1.0,
    closed BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_trades_account ON trades(account_id);
CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol);
CREATE INDEX IF NOT EXISTS idx_trades_closed ON trades(closed);
CREATE INDEX IF NOT EXISTS idx_trades_created ON trades(created_at DESC);

-- ================================================================
-- 4. LOGS TABLE
-- ================================================================
CREATE TABLE IF NOT EXISTS logs (
    id BIGSERIAL PRIMARY KEY,
    account_id BIGINT REFERENCES accounts(login) ON DELETE SET NULL,
    event TEXT NOT NULL,
    log_level TEXT DEFAULT 'INFO',
    symbol TEXT,
    details JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_logs_account ON logs(account_id);
CREATE INDEX IF NOT EXISTS idx_logs_symbol ON logs(symbol);
CREATE INDEX IF NOT EXISTS idx_logs_created ON logs(created_at DESC);

-- ================================================================
-- 5. BOT CONTROL TABLE
-- ================================================================
CREATE TABLE IF NOT EXISTS bot_control (
    id BIGSERIAL PRIMARY KEY,
    account_id BIGINT REFERENCES accounts(login) ON DELETE CASCADE,
    is_running BOOLEAN DEFAULT false,
    brick_size FLOAT DEFAULT 1.0,
    poll_interval FLOAT DEFAULT 0.5,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(account_id)
);
CREATE INDEX IF NOT EXISTS idx_bot_control_account ON bot_control(account_id);

-- ================================================================
-- 6. SETTINGS TABLE
-- ================================================================
CREATE TABLE IF NOT EXISTS settings (
    id BIGSERIAL PRIMARY KEY,
    setting_key TEXT NOT NULL UNIQUE,
    setting_value TEXT,
    description TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO settings (setting_key, setting_value, description) VALUES
    ('default_brick_size', '1.0', 'Default Renko brick size in pips'),
    ('default_sl_pips', '50', 'Default stop loss in pips'),
    ('default_tp_pips', '100', 'Default take profit in pips'),
    ('default_lot_size', '0.01', 'Default lot size'),
    ('max_positions_per_account', '10', 'Maximum concurrent positions per account'),
    ('enable_trailing_stops', 'true', 'Enable trailing stop functionality'),
    ('log_retention_days', '30', 'Days to keep logs')
ON CONFLICT (setting_key) DO NOTHING;

-- ================================================================
-- 7. PRICE TICKERS TABLE
-- ================================================================
CREATE TABLE IF NOT EXISTS price_ticks (
    id BIGSERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,
    bid FLOAT NOT NULL,
    ask FLOAT NOT NULL,
    last_update TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_price_ticks_symbol ON price_ticks(symbol);

-- ================================================================
-- 8. AVAILABLE SYMBOLS TABLE
-- ================================================================
CREATE TABLE IF NOT EXISTS available_symbols (
    id BIGSERIAL PRIMARY KEY,
    symbol TEXT NOT NULL UNIQUE,
    description TEXT,
    pip_value FLOAT DEFAULT 0.01,
    point_value FLOAT DEFAULT 1.0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO available_symbols (symbol, description, pip_value) VALUES
    ('GOLD', 'Gold vs USD (XM)', 0.01),
    ('EURUSD', 'EUR vs USD', 0.0001),
    ('GBPUSD', 'GBP vs USD', 0.0001),
    ('USDJPY', 'USD vs JPY', 0.01),
    ('AUDUSD', 'AUD vs USD', 0.0001),
    ('NZDUSD', 'NZD vs USD', 0.0001),
    ('USDCAD', 'USD vs CAD', 0.0001),
    ('USDCHF', 'USD vs CHF', 0.0001),
    ('BTCUSD', 'Bitcoin vs USD', 1.0),
    ('ETHUSD', 'Ethereum vs USD', 0.1),
    ('XAUUSD', 'Gold vs USD', 0.01),
    ('XAGUSD', 'Silver vs USD', 0.001),
    ('US30', 'Dow Jones 30', 1.0),
    ('NAS100', 'NASDAQ 100', 1.0),
    ('SP500', 'S&P 500', 0.1)
ON CONFLICT (symbol) DO NOTHING;

CREATE INDEX IF NOT EXISTS idx_available_symbols_active ON available_symbols(is_active);

-- ================================================================
-- 9. AUTO-TRADING WATCHLIST TABLE
-- ================================================================
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
CREATE INDEX IF NOT EXISTS idx_auto_trading_watchlist_account ON auto_trading_watchlist(account_id);
CREATE INDEX IF NOT EXISTS idx_auto_trading_watchlist_symbol ON auto_trading_watchlist(symbol);

-- ================================================================
-- 10. AUTO-TRADING POSITIONS TABLE
-- ================================================================
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
CREATE INDEX IF NOT EXISTS idx_auto_trading_positions_account ON auto_trading_positions(account_id);
CREATE INDEX IF NOT EXISTS idx_auto_trading_positions_symbol ON auto_trading_positions(symbol);

-- ================================================================
-- 11. AUTO-TRADING HISTORY TABLE
-- ================================================================
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
CREATE INDEX IF NOT EXISTS idx_auto_trading_history_account ON auto_trading_history(account_id);
CREATE INDEX IF NOT EXISTS idx_auto_trading_history_symbol ON auto_trading_history(symbol);
CREATE INDEX IF NOT EXISTS idx_auto_trading_history_created ON auto_trading_history(created_at DESC);

-- ================================================================
-- 12. DISABLE ROW LEVEL SECURITY
-- (Backend uses service_role key which bypasses RLS anyway)
-- ================================================================
ALTER TABLE accounts DISABLE ROW LEVEL SECURITY;
ALTER TABLE watchlist DISABLE ROW LEVEL SECURITY;
ALTER TABLE trades DISABLE ROW LEVEL SECURITY;
ALTER TABLE logs DISABLE ROW LEVEL SECURITY;
ALTER TABLE bot_control DISABLE ROW LEVEL SECURITY;
ALTER TABLE settings DISABLE ROW LEVEL SECURITY;
ALTER TABLE price_ticks DISABLE ROW LEVEL SECURITY;
ALTER TABLE available_symbols DISABLE ROW LEVEL SECURITY;
ALTER TABLE auto_trading_watchlist DISABLE ROW LEVEL SECURITY;
ALTER TABLE auto_trading_positions DISABLE ROW LEVEL SECURITY;
ALTER TABLE auto_trading_history DISABLE ROW LEVEL SECURITY;

-- ================================================================
-- 13. VIEWS
-- ================================================================

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

-- ================================================================
-- DONE! All 11 tables + views created.
-- ================================================================
