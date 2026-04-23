-- ============================================================
-- RENKO BOT - Enable Row Level Security on all TABLES only
-- (active_positions, auto_trading_history, auto_trading_positions,
--  auto_trading_watchlist, trade_stats are VIEWS - skip them)
-- Run this in Supabase SQL Editor:
-- supabase.com/dashboard/project/mflakcwgbpghyzdyevsb/sql
-- ============================================================

-- Enable RLS on actual tables only (not views)
ALTER TABLE accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE available_symbols ENABLE ROW LEVEL SECURITY;
ALTER TABLE bot_control ENABLE ROW LEVEL SECURITY;
ALTER TABLE logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE price_ticks ENABLE ROW LEVEL SECURITY;
ALTER TABLE settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE trades ENABLE ROW LEVEL SECURITY;
ALTER TABLE watchlist ENABLE ROW LEVEL SECURITY;

-- ============================================================
-- CREATE POLICIES: Only authenticated users can access data
-- ============================================================

-- accounts
CREATE POLICY "Authenticated users only" ON accounts FOR ALL TO authenticated USING (true) WITH CHECK (true);

-- available_symbols
CREATE POLICY "Authenticated users only" ON available_symbols FOR ALL TO authenticated USING (true) WITH CHECK (true);

-- bot_control
CREATE POLICY "Authenticated users only" ON bot_control FOR ALL TO authenticated USING (true) WITH CHECK (true);

-- logs
CREATE POLICY "Authenticated users only" ON logs FOR ALL TO authenticated USING (true) WITH CHECK (true);

-- price_ticks
CREATE POLICY "Authenticated users only" ON price_ticks FOR ALL TO authenticated USING (true) WITH CHECK (true);

-- settings
CREATE POLICY "Authenticated users only" ON settings FOR ALL TO authenticated USING (true) WITH CHECK (true);

-- trades
CREATE POLICY "Authenticated users only" ON trades FOR ALL TO authenticated USING (true) WITH CHECK (true);

-- watchlist
CREATE POLICY "Authenticated users only" ON watchlist FOR ALL TO authenticated USING (true) WITH CHECK (true);

-- ============================================================
-- NOTE: Views (active_positions, auto_trading_history,
-- auto_trading_positions, auto_trading_watchlist, trade_stats)
-- inherit security from their underlying tables.
-- RLS on the base tables above protects them automatically.
-- ============================================================

