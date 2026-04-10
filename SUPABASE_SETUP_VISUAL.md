# Supabase Setup - Visual Guide

## The 3-Step Process

```
┌─────────────────────────────────────────────────────────┐
│  STEP 1: Copy SQL                                       │
│  ────────────────────────────────────────────────────── │
│                                                         │
│  1. Open file: SUPABASE_TABLE_SETUP.sql               │
│  2. Select All (Ctrl+A)                               │
│  3. Copy (Ctrl+C)                                      │
│                                                         │
│  ✓ SQL is now in your clipboard                        │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│  STEP 2: Paste in Supabase                             │
│  ────────────────────────────────────────────────────── │
│                                                         │
│  1. Go to https://supabase.co                          │
│  2. Login and select your project                      │
│  3. Find SQL Editor (left sidebar)                     │
│  4. Click "+ New Query"                               │
│  5. Paste SQL (Ctrl+V)                                │
│  6. Click "RUN" button                                 │
│                                                         │
│  ✓ SQL is executing in Supabase                        │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│  STEP 3: Verify Tables                                 │
│  ────────────────────────────────────────────────────── │
│                                                         │
│  1. Go to "Table Editor" (left sidebar)               │
│  2. Look for 3 new tables:                            │
│     • auto_trading_watchlist                          │
│     • auto_trading_positions                          │
│     • auto_trading_history                            │
│                                                         │
│  ✓ Tables are created and ready!                       │
└─────────────────────────────────────────────────────────┘
```

---

## What Each Table Does

### Table 1: auto_trading_watchlist
```
┌──────────────────────────────────────────────────┐
│ Stores which symbols you want to auto-trade      │
├──────────────────────────────────────────────────┤
│ Example data:                                    │
│                                                  │
│ account_id │ symbol  │ enabled │ brick_size    │
│ 12345      │ XAUUSD  │ true    │ 0.5           │
│ 12345      │ BTCUSD  │ false   │ 50            │
└──────────────────────────────────────────────────┘
```

### Table 2: auto_trading_positions
```
┌──────────────────────────────────────────────────┐
│ Tracks currently open trades                    │
├──────────────────────────────────────────────────┤
│ Example data:                                    │
│                                                  │
│ account_id │ symbol  │ direction │ entry_price │
│ 12345      │ XAUUSD  │ BUY       │ 2050.25     │
│ 12345      │ BTCUSD  │ SELL      │ 42000.00    │
└──────────────────────────────────────────────────┘
```

### Table 3: auto_trading_history
```
┌──────────────────────────────────────────────────┐
│ Records all trades executed by auto-trader       │
├──────────────────────────────────────────────────┤
│ Example data:                                    │
│                                                  │
│ symbol  │ direction │ entry_price │ exit_price │
│ XAUUSD  │ BUY       │ 2050.25     │ 2051.00    │
│ BTCUSD  │ SELL      │ 42000.00    │ 41900.00   │
└──────────────────────────────────────────────────┘
```

---

## Complete Flow After Setup

```
┌──────────────┐
│   Frontend   │
│   (React)    │
└──────┬───────┘
       │
       │ HTTP / WebSocket
       ↓
┌─────────────────────────┐
│   Backend (FastAPI)     │
├─────────────────────────┤
│ • Renko Chart API       │
│ • Trade Execution API   │
│ • Auto-Trading API      │
└──────┬──────────────────┘
       │
       ├─────────────────────────┐
       │                         │
       ↓                         ↓
┌──────────────┐        ┌─────────────────┐
│     MT5      │        │  Supabase DB    │
│ (Broker)     │        │  (PostgreSQL)   │
│              │        │                 │
│ • Quotes     │        │ • Watchlist     │
│ • Orders     │        │ • Positions     │
│ • Execution  │        │ • History       │
└──────────────┘        └─────────────────┘
```

---

## What Happens Next

### Minute 0: User Enables Auto-Trading
```
Frontend Button
    ↓
Backend API
    ↓
Insert into auto_trading_watchlist (enabled=true)
    ↓
Supabase Database
```

### Minute 1: Auto-Trader Checks Symbol
```
Auto-Trader Service
    ↓
Fetch symbol from watchlist
    ↓
Get Renko chart from MT5
    ↓
Evaluate brick color
```

### Minute 1 (continued): Trade Signal Detected
```
Green brick detected (BUY signal)
    ↓
Check if already have position
    ↓
Execute trade on MT5
    ↓
Log to auto_trading_positions
    ↓
Frontend updates with new position
```

### Later: Trade Closes
```
Brick turns red (SELL signal)
    ↓
Close BUY position
    ↓
Log to auto_trading_history
    ↓
Remove from auto_trading_positions
    ↓
Frontend shows closed trade in history
```

---

## Expected Results

### After Running SQL

✅ Supabase Dashboard shows:
```
- auto_trading_watchlist (0 rows)
- auto_trading_positions (0 rows)
- auto_trading_history (0 rows)
```

### After Backend Restart

✅ Backend logs show:
```
🤖 Initializing Auto-Trader Service...
✅ Auto-Trader initialized with 0 symbols
```

### After Adding Symbol

✅ Supabase shows:
```
- auto_trading_watchlist (1 row)
  account_id=12345, symbol=XAUUSD, enabled=true
```

### After Auto-Trade Executed

✅ Supabase shows:
```
- auto_trading_positions (1 row)
  account_id=12345, symbol=XAUUSD, direction=BUY
  
- auto_trading_history (1 row)
  symbol=XAUUSD, direction=BUY, entry_price=2050.25
```

---

## Troubleshooting Flow

```
Tables don't appear?
├─ Check SQL had no errors
├─ Refresh page (F5)
├─ Wrong project selected?
└─ Ask: DB > Table Editor > Look for auto_trading_*

Backend won't connect?
├─ Check .env has SUPABASE_URL and KEY
├─ Restart backend
├─ Check logs for errors
└─ Ask: What error in logs?

Auto-Trader won't execute?
├─ Check tables exist
├─ Check symbol in watchlist table
├─ Check enabled=true in watchlist
├─ Check MT5 is connected
└─ Ask: Any errors in backend logs?
```

---

## 🚀 Ready to Start?

1. Copy `SUPABASE_TABLE_SETUP.sql`
2. Open https://supabase.co
3. Paste in SQL Editor
4. Click RUN
5. Done!

Total time: 2-3 minutes

---

## 📍 File Locations

**SQL File:** `E:\Renko\SUPABASE_TABLE_SETUP.sql`

**Guides:**
- `QUICK_SETUP_TABLES.md` - Quick start
- `SETUP_SUPABASE_TABLES.md` - Details
- `AUTO_TRADING_DATABASE_SETUP.md` - Full system
- `DATABASE_SETUP_COMPLETE.md` - Summary

**Scripts:**
- `create_supabase_tables.py` - Helper
- `auto_create_tables.py` - Tester

---

## Next Steps Summary

✅ **Right Now:**
- Copy SQL and paste in Supabase SQL Editor
- Click RUN
- Verify tables appear

✅ **After SQL Runs:**
- Push changes to GitHub: `git push`
- Pull on VPS: `git pull`
- Restart backend

✅ **After Backend Restart:**
- Test auto-trading with a symbol
- Monitor trade execution
- Check history in Supabase

✅ **Finally:**
- Add frontend UI for enabling/disabling
- Create positions widget
- Build trading dashboard

---

Good luck! Your auto-trading system is almost complete! 🎉
