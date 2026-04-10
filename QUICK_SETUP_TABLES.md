# Quick Setup: Create Supabase Tables in 5 Minutes

## Method 1: Copy-Paste SQL (Easiest & Fastest)

### Step 1: Open Supabase Dashboard
```
https://supabase.co → Login → Select Your Project
```

### Step 2: Go to SQL Editor
```
Left Sidebar → SQL Editor → "+ New Query"
```

### Step 3: Copy SQL from File
Open this file in your repo:
```
E:\Renko\SUPABASE_TABLE_SETUP.sql
```

Copy the ENTIRE content.

### Step 4: Paste in Supabase
1. In Supabase SQL Editor, paste the SQL
2. Click "RUN" button (or press Ctrl+Enter)
3. Wait for: ✅ "Query executed successfully"

### Step 5: Verify
1. Go to "Table Editor" (left sidebar)
2. You should see 3 new tables:
   - auto_trading_watchlist
   - auto_trading_positions
   - auto_trading_history

**Done!** Your database is ready.

---

## What the Tables Do

### auto_trading_watchlist
Stores which symbols you want to auto-trade:
```
account_id  | symbol  | enabled | brick_size
12345       | XAUUSD  | true    | 0.5
```

### auto_trading_positions
Tracks open trades:
```
account_id  | symbol  | direction | entry_price | lot_size | status
12345       | XAUUSD  | BUY       | 2050.25     | 0.1      | OPEN
```

### auto_trading_history
Records all past trades:
```
account_id  | symbol  | direction | entry_price | exit_price | pnl    | created_at
12345       | XAUUSD  | BUY       | 2050.25     | 2051.00    | 75.00  | 2024-01-15
```

---

## After Tables are Created

### 1. Push to GitHub
```bash
cd E:\Renko
git add -A
git commit -m "feat: Add Supabase table setup scripts"
git push origin main
```

### 2. Pull on VPS
```bash
cd /home/app/Renko
git pull origin main
```

### 3. Restart Backend
```bash
# Stop current process (Ctrl+C or kill)
# Then restart:
python -m backend.main
```

### 4. Check Backend Logs
Look for:
```
🤖 Initializing Auto-Trader Service...
✅ Auto-Trader initialized with 0 symbols
```

This means the tables are connected!

---

## Test It Works

### Add a Symbol to Watch
```bash
# From your PC or VPS
curl -X POST http://vps-ip:8000/api/auto-trading/symbols/add \
  -H "Content-Type: application/json" \
  -d '{"symbol": "XAUUSD", "brick_size": 0.5}'
```

### Enable Auto-Trading
```bash
curl -X POST http://vps-ip:8000/api/auto-trading/enable
```

### Check Status
```bash
curl http://vps-ip:8000/api/auto-trading/status
```

Expected response:
```json
{
  "running": true,
  "symbols": ["XAUUSD"],
  "positions": 0
}
```

### View Trades in Supabase
1. Go to Supabase → Table Editor
2. Click on `auto_trading_history`
3. You should see executed trades logged there

---

## Files Created for You

| File | Purpose |
|------|---------|
| **SUPABASE_TABLE_SETUP.sql** | The SQL to copy-paste ⭐ |
| **SETUP_SUPABASE_TABLES.md** | Detailed table descriptions |
| **AUTO_TRADING_DATABASE_SETUP.md** | Full system overview |
| **create_supabase_tables.py** | Python helper (displays SQL) |
| **auto_create_tables.py** | Alternative helper script |

---

## Troubleshooting

### SQL Error: "relation already exists"
- This is fine! It means tables were already created
- The `IF NOT EXISTS` clause prevents errors
- Proceed to next step

### Can't Find SQL Editor
- In Supabase: left sidebar → "SQL" icon (looks like terminal)
- Or: left sidebar → "SQL Editor"

### Refresh Not Showing Tables
- Press F5 to hard refresh browser
- Close and reopen Supabase tab

### Backend Says: "Table not found"
- Make sure tables were actually created (check Supabase)
- Verify `.env` has correct SUPABASE_URL and SUPABASE_KEY
- Restart backend after tables are created

---

## Summary of Your Auto-Trading System

**Frontend** (React)
- Shows Renko chart with real-time prices
- Button to enable/disable auto-trading per symbol
- Displays open positions and trade history

**Backend** (Python/FastAPI)
- Monitors enabled symbols every 1 minute
- Evaluates Renko brick color changes
- Executes trades automatically when signal detected
- Logs trades to database

**Database** (Supabase PostgreSQL)
- Stores watchlist (which symbols to trade)
- Stores positions (currently open trades)
- Stores history (all past trades)

---

## Next Steps

1. ✅ Create tables (you're here)
2. ⏳ Push changes to GitHub
3. ⏳ Pull on VPS
4. ⏳ Restart backend
5. ⏳ Test auto-trading with a symbol
6. ⏳ Monitor trade execution

---

## Contact & Support

If you hit any issues:

1. Check backend logs for errors
2. Verify Supabase tables exist
3. Check `.env` credentials
4. Look in `auto_trading_history` table for error details

Good luck! Your automated trading system is almost ready.
