# Understanding "UNRESTRICTED" Tables in Supabase

## What Does "UNRESTRICTED" Mean?

**UNRESTRICTED** means **Row Level Security (RLS) is NOT enabled** on the table.

### This is FINE for your use case because:
1. ✅ Your backend has direct Supabase credentials
2. ✅ Only your backend can write to the database
3. ✅ Frontend uses read-only or controlled access
4. ✅ No multi-user auth needed for trading data

### When RLS is Needed:
- ❌ Multiple users with different permissions
- ❌ Public API endpoints
- ❌ Complex authorization rules
- ❌ Sensitive data needing fine-grained control

---

## Your Current Table Status

### ✅ Tables You Already Have

```
accounts              - Your MT5 accounts
watchlist            - Symbols to trade (existing structure)
trades               - Historical trades
logs                 - System logs
bot_control          - Bot settings
settings             - Global settings
price_ticks          - Live quotes
available_symbols    - Symbol definitions
```

### ⏳ Tables You Need to Add for Auto-Trading

The schema only needs these 3 NEW tables for the auto-trading service:

```sql
-- NEW: Track auto-trading positions separately from manual trades
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

-- NEW: Track auto-trading history separately
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

-- NEW: Track which symbols are enabled for auto-trading
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

-- Add indexes
CREATE INDEX idx_auto_trading_watchlist_account ON auto_trading_watchlist(account_id);
CREATE INDEX idx_auto_trading_positions_account ON auto_trading_positions(account_id);
CREATE INDEX idx_auto_trading_history_account ON auto_trading_history(account_id);
```

---

## Should You Enable RLS?

### ❌ Don't Enable RLS Unless You Need It

Your system works perfectly with UNRESTRICTED because:

1. **Backend Controls Access**
   - Only backend has Supabase keys
   - Frontend can't directly connect
   - All data access goes through API endpoints

2. **Single Account Per Instance**
   - Each VPS instance = one MT5 account
   - No sharing of data between users

3. **Production Ready**
   - UNRESTRICTED is common for enterprise systems
   - The database itself is private (Supabase project)
   - Network is protected

### ✅ If You Want to Enable RLS (Optional)

Only do this if you plan to:
- Add web-based user authentication
- Let multiple users access their own data
- Expose direct Supabase API to frontend

If you want to enable it, SQL would be:

```sql
-- Enable RLS on all tables
ALTER TABLE accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE trades ENABLE ROW LEVEL SECURITY;
ALTER TABLE watchlist ENABLE ROW LEVEL SECURITY;
ALTER TABLE logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE bot_control ENABLE ROW LEVEL SECURITY;
ALTER TABLE settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE price_ticks ENABLE ROW LEVEL SECURITY;
ALTER TABLE available_symbols ENABLE ROW LEVEL SECURITY;
ALTER TABLE auto_trading_watchlist ENABLE ROW LEVEL SECURITY;
ALTER TABLE auto_trading_positions ENABLE ROW LEVEL SECURITY;
ALTER TABLE auto_trading_history ENABLE ROW LEVEL SECURITY;

-- Then create policies for authenticated users
-- (This gets complex - don't do this now)
```

---

## Action Items

### ✅ Your Existing Tables Are Fine
- Keep them as UNRESTRICTED
- No changes needed

### ⏳ Add 3 New Auto-Trading Tables
1. Go to Supabase SQL Editor
2. Run the 3 new CREATE TABLE statements above
3. Verify in Table Editor

### For Now
- Tables work perfectly
- Keep UNRESTRICTED
- Focus on functionality, not security
- Can add RLS later if needed

---

## Summary

| Status | Table | RLS | Action |
|--------|-------|-----|--------|
| ✅ Exists | accounts | OFF | Keep as is |
| ✅ Exists | trades | OFF | Keep as is |
| ✅ Exists | watchlist | OFF | Keep as is |
| ✅ Exists | logs | OFF | Keep as is |
| ✅ Exists | bot_control | OFF | Keep as is |
| ✅ Exists | settings | OFF | Keep as is |
| ✅ Exists | price_ticks | OFF | Keep as is |
| ✅ Exists | available_symbols | OFF | Keep as is |
| ⏳ Add | auto_trading_watchlist | OFF | Add now |
| ⏳ Add | auto_trading_positions | OFF | Add now |
| ⏳ Add | auto_trading_history | OFF | Add now |

---

## Next Step

The only missing tables are the 3 auto-trading tables. Copy the SQL above and run in Supabase SQL Editor to complete your setup.

Your system is **ready to go!** 🚀
