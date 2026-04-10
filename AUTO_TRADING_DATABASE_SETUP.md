# Auto-Trading System - Database Setup Complete

## Summary

Your real-time auto-trading system is ready for database integration. Here's what's been done:

### Backend Components (Already Implemented)

✅ **Auto-Trading Engine** (`backend/services/auto_trader.py`)
- Monitors enabled symbols 24/7
- Evaluates Renko brick colors every 1 minute
- Auto-executes trades based on strategy

✅ **REST API Endpoints** (`backend/api/auto_trading.py`)
- Add/remove symbols for auto-trading
- Enable/disable auto-trading
- Check service status
- View open positions

✅ **Integration** (`backend/main.py`)
- Auto-trader starts on backend startup
- Gracefully stops on shutdown

### Database Schema Created

Three tables are ready to be created in Supabase:

1. **auto_trading_watchlist**
   - Stores symbols enabled for auto-trading
   - Contains brick_size and lot_size_rules configuration
   - One entry per account_id + symbol pair

2. **auto_trading_positions**
   - Tracks currently open positions
   - Stores ticket number, entry price, lot size
   - Helps prevent duplicate positions

3. **auto_trading_history**
   - Records all trades executed
   - Tracks entry/exit prices and P&L
   - Useful for analysis and backtesting

### SQL Files

- **SUPABASE_TABLE_SETUP.sql** - Ready-to-use SQL script
- **SETUP_SUPABASE_TABLES.md** - Detailed setup guide

---

## How to Create Tables

### Step 1: Open Supabase Dashboard
1. Go to https://supabase.co
2. Select your project
3. Click "SQL Editor" in left sidebar

### Step 2: Create New Query
- Click "+ New Query" button

### Step 3: Copy SQL
- Open `SUPABASE_TABLE_SETUP.sql` in your repo
- Copy all content (Ctrl+A, Ctrl+C)

### Step 3: Paste and Execute
- Paste into Supabase SQL Editor
- Click "RUN" button
- Wait for success message: "Query executed successfully"

### Step 4: Verify
- Go to "Table Editor"
- You should see the three new tables

---

## Next: Integration with Frontend

Once tables are created, you'll need to:

### 1. Create "Enable Auto-Trading" UI
Location: `frontend/src/components/RenkoChart.tsx` or watchlist component

Features:
- Toggle button to enable/disable auto-trading for each symbol
- Display current position status
- Show recent trades

### 2. Add Settings Page
- Configure lot sizing rules
- Set brick size per symbol
- Set trading hours

### 3. Monitor Dashboard
- Show open positions
- Display trade history
- Show P&L

---

## Testing the System

### After Tables Created:

```bash
# 1. On VPS, pull the latest changes
git pull origin main

# 2. Restart backend
# (stop current process)
# python -m backend.main

# 3. Check auto-trader initialized
# Look for: "✅ Auto-Trader initialized with X symbols"

# 4. Test API endpoints
curl http://vps-ip:8000/api/auto-trading/status
curl http://vps-ip:8000/api/auto-trading/positions

# 5. Add a symbol to watchlist
curl -X POST http://vps-ip:8000/api/auto-trading/symbols/add \
  -H "Content-Type: application/json" \
  -d '{"symbol": "XAUUSD", "brick_size": 0.5}'

# 6. Enable auto-trading
curl -X POST http://vps-ip:8000/api/auto-trading/enable

# 7. Check if trades are being executed
# Monitor trade history table in Supabase
```

---

## Architecture Overview

```
Frontend (React)
    ↓ HTTP Polling (2s interval)
    ↓ WebSocket (optional for streaming)
Backend (FastAPI)
    ├── /api/renko/chart/* - Chart data
    ├── /api/auto-trading/* - Control auto-trader
    └── Auto-Trader Service (background)
            ↓
        Every 1 minute
            ↓
        Evaluate Renko + Strategy
            ↓
        If Signal Detected
            ↓
        Execute Trade via MT5
            ↓
        Log in Supabase
            ↓
        Update Frontend Dashboard
```

---

## Key Files

| File | Purpose |
|------|---------|
| `SUPABASE_TABLE_SETUP.sql` | SQL to create tables |
| `backend/services/auto_trader.py` | Core trading engine |
| `backend/api/auto_trading.py` | REST API endpoints |
| `backend/main.py` | Integration point |
| `create_supabase_tables.py` | Helper script |
| `SETUP_SUPABASE_TABLES.md` | Detailed guide |

---

## Troubleshooting

### Q: Tables don't appear after running SQL?
A: 
1. Check for errors in SQL Editor output
2. Refresh browser (F5)
3. Check if you're in the correct Supabase project

### Q: Backend can't connect to tables?
A:
1. Verify `.env` has correct SUPABASE_URL and SUPABASE_KEY
2. Check backend logs for connection errors
3. Ensure tables are public (check RLS policies)

### Q: Auto-trader not executing trades?
A:
1. Check if symbols are in watchlist table with enabled=true
2. Check backend logs for strategy evaluation results
3. Verify MT5 account is connected
4. Check trade history table for any errors

---

## Commands Reference

### Create Tables (Manual)
1. Open Supabase SQL Editor
2. Paste content from `SUPABASE_TABLE_SETUP.sql`
3. Click RUN

### Add Symbol to Watchlist
```bash
curl -X POST http://localhost:8000/api/auto-trading/symbols/add \
  -H "Content-Type: application/json" \
  -d '{"symbol": "XAUUSD", "brick_size": 0.5}'
```

### Enable Auto-Trading
```bash
curl -X POST http://localhost:8000/api/auto-trading/enable
```

### Check Status
```bash
curl http://localhost:8000/api/auto-trading/status
```

### View Open Positions
```bash
curl http://localhost:8000/api/auto-trading/positions
```

---

## What Happens When You Enable Auto-Trading

1. **User clicks "Enable Auto-Trading"** for symbol XAUUSD
   - Backend inserts into `auto_trading_watchlist` with `enabled=true`

2. **Auto-Trader Service runs every minute**
   - Fetches Renko chart for XAUUSD
   - Evaluates strategy (color change?)
   - If brick turns GREEN → execute BUY
   - If brick turns RED → execute SELL

3. **Trade Executed**
   - Order sent to MT5
   - Ticket number stored in `auto_trading_positions`
   - Trade details logged to `auto_trading_history`

4. **Frontend Updates**
   - Position shows as OPEN
   - Recent trades display
   - P&L calculated when closed

---

## Status: Ready for Deployment

✅ Backend: Ready
✅ Database Schema: Ready  
✅ SQL Scripts: Ready
⏳ Tables: Awaiting creation in Supabase
⏳ Frontend: Awaiting UI implementation
⏳ Testing: Awaiting table creation

**Next Step:** Create the Supabase tables using `SUPABASE_TABLE_SETUP.sql`
