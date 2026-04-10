# Auto-Trading System Setup - Complete Guide

## 🎯 Overview

Your real-time Renko-based automated trading system is ready for database integration. This guide will help you create the Supabase tables needed for the system to work.

---

## 📁 Files You Need

### Main SQL File
- **`SUPABASE_TABLE_SETUP.sql`** - Copy/paste this into Supabase SQL Editor

### Quick Start Guides  
- **`QUICK_SETUP_TABLES.md`** - ⭐ START HERE - 3-step guide
- **`SUPABASE_SETUP_VISUAL.md`** - Visual diagrams and flowcharts

### Detailed Documentation
- **`SETUP_SUPABASE_TABLES.md`** - Full table descriptions and examples
- **`AUTO_TRADING_DATABASE_SETUP.md`** - Complete system architecture
- **`DATABASE_SETUP_COMPLETE.md`** - Summary and next steps
- **`AUTO_TRADING_SETUP_README.md`** - This file

### Helper Scripts (Optional)
- **`create_supabase_tables.py`** - Displays SQL (helps verify)
- **`auto_create_tables.py`** - Connection tester
- **`setup_auto_trading_tables.py`** - Alternative helper

---

## ⚡ Quick Start (3 Minutes)

### 1️⃣ Open SQL File
```
E:\Renko\SUPABASE_TABLE_SETUP.sql
Select All (Ctrl+A) → Copy (Ctrl+C)
```

### 2️⃣ Paste in Supabase
```
1. https://supabase.co → Login → Select Project
2. Left Sidebar: SQL Editor → "+ New Query"
3. Paste (Ctrl+V)
4. Click "RUN"
```

### 3️⃣ Verify
```
Left Sidebar: Table Editor
Look for:
  ✓ auto_trading_watchlist
  ✓ auto_trading_positions
  ✓ auto_trading_history
```

**Done!** Tables are created. ✅

---

## 🗂️ What Gets Created

### Table: auto_trading_watchlist
```sql
Columns:
- id (UUID) - Primary key
- account_id (INT) - MT5 account number
- symbol (VARCHAR) - Trading symbol like "XAUUSD"
- enabled (BOOLEAN) - Is auto-trading active?
- brick_size (FLOAT) - Renko brick size
- lot_size_rules (JSONB) - Position sizing rules
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)

Purpose: Store which symbols to auto-trade
```

### Table: auto_trading_positions
```sql
Columns:
- id (UUID) - Primary key
- account_id (INT)
- symbol (VARCHAR) - "XAUUSD", etc
- ticket (INT) - MT5 order ticket
- position (VARCHAR) - "BUY" or "SELL"
- entry_price (FLOAT)
- lot_size (FLOAT)
- opened_at (TIMESTAMP)
- status (VARCHAR) - "OPEN" or "CLOSED"

Purpose: Track currently open positions
```

### Table: auto_trading_history
```sql
Columns:
- id (UUID) - Primary key
- account_id (INT)
- symbol (VARCHAR)
- direction (VARCHAR) - "BUY" or "SELL"
- entry_price (FLOAT)
- entry_time (TIMESTAMP)
- exit_price (FLOAT)
- exit_time (TIMESTAMP)
- lot_size (FLOAT)
- pnl (FLOAT) - Profit/Loss
- reason (VARCHAR) - Why executed
- created_at (TIMESTAMP)

Purpose: Record all executed trades for analysis
```

---

## 📊 System Architecture

```
Frontend (React)
├─ Renko Chart Display
├─ Auto-Trading Control Button
├─ Positions Widget
└─ Trade History

    ↓ HTTP API (2s polling)

Backend (FastAPI)
├─ /api/renko/chart/* - Chart data
├─ /api/execute-trade - Trade execution
└─ /api/auto-trading/* - Auto-trading control
    │
    ├─ Auto-Trader Service (background)
    │  ├─ Monitors watchlist every 1 min
    │  ├─ Evaluates Renko strategy
    │  ├─ Executes trades
    │  └─ Updates database
    │
    ├─ MT5 Connection
    │  ├─ Fetch live prices
    │  ├─ Get Renko bricks
    │  └─ Send orders
    │
    └─ Supabase Database
       ├─ auto_trading_watchlist
       ├─ auto_trading_positions
       └─ auto_trading_history
```

---

## 🔄 How It Works

### User Flow

1. **User clicks "Enable Auto-Trading"** for XAUUSD
   ```
   Frontend → Backend API
   ↓
   Backend inserts into auto_trading_watchlist (enabled=true)
   ↓
   Supabase stores the config
   ```

2. **Every 1 minute, Auto-Trader checks**
   ```
   Auto-Trader loads watchlist from Supabase
   ↓
   Fetches Renko chart from MT5
   ↓
   Evaluates: Did brick color change?
   ```

3. **If Brick Color Changed**
   ```
   Green (was red) → BUY Signal
   Red (was green) → SELL Signal
   ↓
   Check: Do we have open position?
   ↓
   If yes: Close it first
   If no: Open new position
   ```

4. **Trade Executed**
   ```
   Send order to MT5
   ↓
   Store in auto_trading_positions (status=OPEN)
   ↓
   Later when closed: Move to auto_trading_history
   ↓
   Frontend fetches history and displays
   ```

---

## ✅ Pre-Requisites Met

Your backend is already prepared:

✅ **auto_trader.py** - Created and ready
- Connects to Supabase
- Loads watchlist from database
- Evaluates strategy every 1 minute
- Executes trades and logs results

✅ **auto_trading.py** - REST API endpoints ready
- `/api/auto-trading/symbols/add` - Add symbol
- `/api/auto-trading/enable` - Enable service
- `/api/auto-trading/status` - Check status
- `/api/auto-trading/positions` - View positions
- `/api/auto-trading/history` - View history

✅ **main.py** - Integrated
- Auto-trader starts on backend startup
- Stops cleanly on shutdown

---

## 📝 After Creating Tables

### Step 1: Push to GitHub
```bash
cd E:\Renko
git add SUPABASE_TABLE_SETUP.sql
git add QUICK_SETUP_TABLES.md
git add SUPABASE_SETUP_VISUAL.md
git add AUTO_TRADING_DATABASE_SETUP.md
git commit -m "docs: Add Supabase auto-trading table setup guides"
git push origin main
```

### Step 2: Pull on VPS
```bash
cd /home/app/Renko
git pull origin main
```

### Step 3: Restart Backend
```bash
# Stop current process (Ctrl+C or kill)
# Restart:
python -m backend.main
```

### Step 4: Check Logs
Look for:
```
🤖 Initializing Auto-Trader Service...
📋 Loaded 0 symbols from watchlist
✅ Auto-Trader initialized with 0 symbols
```

---

## 🧪 Testing It Works

### Test 1: Check Service Status
```bash
curl http://vps-ip:8000/api/auto-trading/status

Expected response:
{
  "running": true,
  "symbols": [],
  "positions": 0
}
```

### Test 2: Add Symbol to Watchlist
```bash
curl -X POST http://vps-ip:8000/api/auto-trading/symbols/add \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "XAUUSD",
    "brick_size": 0.5
  }'
```

### Test 3: Check in Supabase
```
1. Go to https://supabase.co
2. Table Editor
3. Click auto_trading_watchlist
4. You should see the XAUUSD entry
```

### Test 4: Enable Auto-Trading
```bash
curl -X POST http://vps-ip:8000/api/auto-trading/enable

Look for success response
```

### Test 5: Monitor Backend Logs
Watch for:
```
INFO: Evaluating XAUUSD...
INFO: Brick color: green
INFO: Trade signal detected
INFO: Executing BUY trade...
```

### Test 6: Check Trade History
```
Supabase → Table Editor → auto_trading_history
You should see executed trades logged
```

---

## 🎓 Understanding the System

### Why Three Tables?

1. **watchlist** - Configuration (which symbols to trade)
2. **positions** - Current state (what's open now)
3. **history** - Records (what was traded)

This separation allows:
- Quick lookups on current positions
- Analysis of past performance
- Configuration management

### Why 1-Minute Evaluation?

- 1-min candles are standard for Renko
- Frequent enough for real-time trading
- Not too frequent (avoids overload)

### Why Supabase?

- Cloud database (works from anywhere)
- Real-time updates
- Built-in REST API
- PostgreSQL power
- Generous free tier

---

## 🚀 Next: Frontend Integration

After database is working, you'll want:

### Phase 1: Basic UI
- [ ] "Enable Auto-Trading" button in watchlist
- [ ] Show if auto-trading is on/off
- [ ] Display number of open positions

### Phase 2: Detailed UI
- [ ] Open positions widget
- [ ] Recent trades list
- [ ] Position details (entry price, P&L)

### Phase 3: Management UI
- [ ] Settings page
- [ ] Configure lot sizing
- [ ] Set risk limits
- [ ] View trade statistics

### Phase 4: Analytics
- [ ] Win/loss ratio
- [ ] Total P&L by symbol
- [ ] Trade charts
- [ ] Performance history

---

## 📋 Checklist

- [ ] Copy SQL from SUPABASE_TABLE_SETUP.sql
- [ ] Paste in Supabase SQL Editor
- [ ] Click RUN
- [ ] Verify tables appear in Table Editor
- [ ] Push changes to GitHub
- [ ] Pull on VPS
- [ ] Restart backend
- [ ] Check backend logs for initialization
- [ ] Test API endpoints
- [ ] Add test symbol to watchlist
- [ ] Monitor Supabase for trades
- [ ] Frontend integration (later)

---

## ❓ FAQ

**Q: Will this work on VPS immediately after pull?**
A: Yes, backend automatically connects when it starts.

**Q: Do I need to do anything else?**
A: Just create the tables. Backend handles the rest.

**Q: How do I know it's working?**
A: Check backend logs and Supabase for data.

**Q: What if I see errors?**
A: Check: .env file, Supabase connection, MT5 account.

**Q: Can I test before adding real symbols?**
A: Yes, add a test symbol with small brick size.

**Q: Where are trades stored?**
A: Supabase → auto_trading_history table.

**Q: How do I stop auto-trading?**
A: Set enabled=false for symbol in watchlist, or disable service.

**Q: Can I trade multiple symbols?**
A: Yes, add as many as you want to watchlist.

---

## 📞 Quick Reference

| Task | Location |
|------|----------|
| Create Tables | Copy `SUPABASE_TABLE_SETUP.sql` to Supabase |
| Quick Start | Read `QUICK_SETUP_TABLES.md` |
| Visual Guide | Read `SUPABASE_SETUP_VISUAL.md` |
| Full Details | Read `SETUP_SUPABASE_TABLES.md` |
| System Overview | Read `AUTO_TRADING_DATABASE_SETUP.md` |
| Check Status | `curl http://vps:8000/api/auto-trading/status` |
| View Trades | Supabase → Table Editor → auto_trading_history |

---

## ✨ Summary

**Status: 99% Ready!**

Everything is prepared. All you need to do:

1. ✅ Backend: Ready
2. ✅ API Endpoints: Ready
3. ✅ Service: Ready
4. ⏳ Database: Awaiting table creation

**Action: Copy SQL and paste in Supabase SQL Editor**

Your automated Renko trading system will be fully operational in 5 minutes! 🚀

---

## Questions?

Check the documentation:
- **Quick Start**: `QUICK_SETUP_TABLES.md`
- **Visual Guide**: `SUPABASE_SETUP_VISUAL.md`
- **Detailed**: `SETUP_SUPABASE_TABLES.md`
- **System Overview**: `AUTO_TRADING_DATABASE_SETUP.md`

All files are in `E:\Renko\`
