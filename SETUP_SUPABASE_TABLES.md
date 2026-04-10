# Setting Up Supabase Tables for Auto-Trading

## Quick Steps

### Option 1: Manual SQL Execution (Easiest)

1. **Open Supabase Dashboard**
   - Go to https://supabase.co → Your Project → SQL Editor
   - Or click the "SQL" icon in left sidebar

2. **Create New Query**
   - Click "+ New Query"

3. **Copy SQL Commands**
   - Open `SUPABASE_TABLE_SETUP.sql` in your repo
   - Copy the entire content

4. **Paste and Execute**
   - Paste into the SQL Editor
   - Click "RUN" button (or Ctrl+Enter)
   - Wait for success message

5. **Verify Tables**
   - Go to "Table Editor" in Supabase dashboard
   - You should see:
     - `auto_trading_watchlist`
     - `auto_trading_positions`
     - `auto_trading_history`

### Option 2: Python Script

```bash
cd E:\Renko
python create_supabase_tables.py
```

This will display the SQL commands to run in Supabase SQL Editor.

---

## Tables Overview

### 1. auto_trading_watchlist
Stores symbols enabled for auto-trading monitoring.

| Field | Type | Purpose |
|-------|------|---------|
| id | UUID | Primary key |
| account_id | INT | MT5 account number |
| symbol | VARCHAR(20) | Trading symbol (e.g., "XAUUSD") |
| enabled | BOOLEAN | Whether auto-trading is active |
| brick_size | FLOAT | Renko brick size for this symbol |
| lot_size_rules | JSONB | JSON with balance thresholds |
| created_at | TIMESTAMP | When added |
| updated_at | TIMESTAMP | Last modified |

**Example:**
```json
{
  "account_id": 12345,
  "symbol": "XAUUSD",
  "enabled": true,
  "brick_size": 0.5,
  "lot_size_rules": {
    "balance_less_100": 0.001,
    "balance_101_500": 0.01,
    "balance_501_plus": 0.1
  }
}
```

### 2. auto_trading_positions
Tracks currently open positions from auto-trading service.

| Field | Type | Purpose |
|-------|------|---------|
| id | UUID | Primary key |
| account_id | INT | MT5 account |
| symbol | VARCHAR(20) | Trading symbol |
| ticket | INT | MT5 order ticket number |
| position | VARCHAR(10) | "BUY" or "SELL" |
| entry_price | FLOAT | Entry price |
| lot_size | FLOAT | Position size |
| opened_at | TIMESTAMP | When opened |
| status | VARCHAR(20) | "OPEN" or "CLOSED" |

### 3. auto_trading_history
Records all trades executed by auto-trading.

| Field | Type | Purpose |
|-------|------|---------|
| id | UUID | Primary key |
| account_id | INT | MT5 account |
| symbol | VARCHAR(20) | Trading symbol |
| direction | VARCHAR(10) | "BUY" or "SELL" |
| entry_price | FLOAT | Entry price |
| entry_time | TIMESTAMP | When entered |
| exit_price | FLOAT | Exit price (when closed) |
| exit_time | TIMESTAMP | When exited |
| lot_size | FLOAT | Position size |
| pnl | FLOAT | Profit/Loss |
| reason | VARCHAR(100) | Why trade was executed |
| created_at | TIMESTAMP | Record created time |

---

## Testing Tables

After creating tables, verify with these queries in Supabase SQL Editor:

```sql
-- Check watchlist table
SELECT COUNT(*) FROM auto_trading_watchlist;

-- Check positions table
SELECT COUNT(*) FROM auto_trading_positions;

-- Check history table
SELECT COUNT(*) FROM auto_trading_history;

-- View table structure
\d auto_trading_watchlist
\d auto_trading_positions
\d auto_trading_history
```

---

## Next Steps

1. **Tables Created** ✓
2. Update backend `auto_trader.py` to connect to tables
3. Add frontend UI for enabling/disabling symbols
4. Test auto-trading service with real data
5. Monitor trade execution via `auto_trading_history`

---

## Troubleshooting

### Tables Don't Appear After SQL Execution

1. Refresh the Supabase dashboard (F5)
2. Check for SQL errors in the console output
3. Verify your Supabase project is selected
4. Check RLS policies (may be blocking visibility)

### Permission Errors

If you see permission errors, uncomment the GRANT statements in `SUPABASE_TABLE_SETUP.sql`:

```sql
GRANT ALL ON auto_trading_watchlist TO authenticated;
GRANT ALL ON auto_trading_positions TO authenticated;
GRANT ALL ON auto_trading_history TO authenticated;
```

### Connection Errors from Backend

Make sure `.env` has correct credentials:
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

---

## Quick Reference

**SQL File Location:** `E:\Renko\SUPABASE_TABLE_SETUP.sql`

**Python Helper Scripts:**
- `create_supabase_tables.py` - Helper to display SQL commands
- `setup_auto_trading_tables.py` - Alternative setup script

**Backend Integration:** `backend/services/auto_trader.py` uses these tables for persistent storage.
