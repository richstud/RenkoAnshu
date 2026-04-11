# Enabling BTCUSD - Why No Symbols Yet

## The Problem ❌

Your API response shows:
```json
"enabled_symbols": [],
"symbol_count": 0
```

**Translation:** The watchlist has NO symbols enabled for auto-trading

You added BTCUSD but it's not **enabled** yet.

---

## The Solution ✅

### Option 1: Enable via Supabase UI (Easiest)

1. **Go to:** https://supabase.co
2. **Select project → Table Editor**
3. **Click:** `auto_trading_watchlist` table
4. **Find:** BTCUSD row
5. **Change:** `enabled` column from `false` → `true`
6. **Done!**

Verify by running status again:
```bash
curl http://localhost:8000/api/auto-trading/status
```

Should now show:
```json
"enabled_symbols": ["BTCUSD"],
"symbol_count": 1
```

---

### Option 2: Enable via SQL

Run this in Supabase SQL Editor:

```sql
-- Check current state
SELECT symbol, enabled, brick_size 
FROM auto_trading_watchlist 
WHERE symbol = 'BTCUSD';

-- Enable BTCUSD
UPDATE auto_trading_watchlist 
SET enabled = true 
WHERE symbol = 'BTCUSD';

-- Verify
SELECT symbol, enabled, brick_size 
FROM auto_trading_watchlist 
WHERE symbol = 'BTCUSD';
```

Expected result:
```
symbol  | enabled | brick_size
BTCUSD  | true    | 1.0
```

---

## After Enabling

### Step 1: Restart Backend
```bash
# Stop current backend (Ctrl+C)
# Then start fresh:
python -m backend.main
```

This reloads the watchlist from database.

### Step 2: Check Status Again
```bash
curl http://localhost:8000/api/auto-trading/status
```

Now should show:
```json
{
  "service": {
    "running": true,
    "enabled_symbols": ["BTCUSD"],
    "symbol_count": 1,
    "last_evaluation": "2026-04-11T17:15:30.000000"
  },
  "positions": {
    "open_count": 0,
    "details": []
  }
}
```

### Step 3: Wait 1 Minute
Auto-trader evaluates every 1 minute. After 1 minute:
- Check logs in backend terminal
- Look for: `📊 Evaluating BTCUSD...`

### Step 4: Check Positions After Next Evaluation
```bash
curl http://localhost:8000/api/auto-trading/positions
```

Should show trade if brick color changed.

---

## Troubleshooting

### Still No Symbols After Enabling?

**Check what's in watchlist:**
```sql
SELECT * FROM auto_trading_watchlist;
```

Should show:
```
id | account_id | symbol  | enabled | brick_size | ...
1  | 12345      | BTCUSD  | true    | 1.0        | ...
```

**If BTCUSD not there:**
Add it manually:
```sql
INSERT INTO auto_trading_watchlist (account_id, symbol, enabled, brick_size)
VALUES (12345, 'BTCUSD', true, 1.0)
ON CONFLICT DO NOTHING;
```

**If enabled still false:**
```sql
UPDATE auto_trading_watchlist 
SET enabled = true 
WHERE symbol = 'BTCUSD';
```

---

## Verify Steps Completed

- [ ] Go to Supabase Table Editor
- [ ] Open auto_trading_watchlist table
- [ ] Find BTCUSD row
- [ ] Change enabled = true
- [ ] Restart backend
- [ ] Run status check
- [ ] Confirm symbol_count = 1
- [ ] Wait 1 minute
- [ ] Check logs for evaluation

---

## Expected Timeline After Enabling

| Time | Action | Where to Check |
|------|--------|-----------------|
| Now | Enable in Supabase | Table Editor |
| +10s | Restart backend | Terminal |
| +30s | Check status | curl command |
| +1m | First evaluation | Backend logs |
| +1m | First trade (maybe) | auto_trading_positions |

---

## Debug Commands

```bash
# Check if BTCUSD is enabled
curl http://localhost:8000/api/auto-trading/status

# If empty, check database
# In Supabase SQL:
SELECT * FROM auto_trading_watchlist WHERE symbol = 'BTCUSD';

# Check BTCUSD price is updating
curl http://localhost:8000/api/tickers/BTCUSD/quote

# Check Renko chart exists
curl "http://localhost:8000/api/renko/chart/BTCUSD?brick_size=1&timeframe=1"
```

---

## Do This Right Now

1. **Go to Supabase** → Table Editor → auto_trading_watchlist
2. **Find BTCUSD** row
3. **Click** enabled column
4. **Change** false → true
5. **Save** (should auto-save)
6. **Go to terminal** and restart backend
7. **Run:** `curl http://localhost:8000/api/auto-trading/status`
8. **Verify:** symbol_count shows 1

You'll be good to go! 🚀
