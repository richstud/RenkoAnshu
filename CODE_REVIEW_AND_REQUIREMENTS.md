# Code Review & Requirements Analysis

## Current Architecture ✅

Your app follows the correct architecture:
```
Frontend (React) → Backend (FastAPI on VPS) → MT5 Terminal (on VPS) + Supabase
```

## ✅ What's Working Well

1. **Backend Structure**: FastAPI with modular design (signals, execution, MT5 connection)
2. **Renko Strategy**: Logic is implemented correctly (brick-based reversals)
3. **Multi-Account Support**: MT5Manager handles multiple accounts
4. **Supabase Integration**: Trades are being logged correctly
5. **Worker Pattern**: Background bot with signal generation is properly designed

---

## ❌ Critical Gaps to Fix

### 1. **Missing Frontend Features (HIGH PRIORITY)**

Your requirements ask for these, but they're NOT implemented:

#### A. Ticker Selection & Display with Real-Time Bid/Ask
- ❌ NO endpoint to get available tickers from MT5
- ❌ NO endpoint to get real-time bid/ask prices
- ❌ NO frontend UI to select tickers
- ❌ NO frontend watchlist UI

#### B. Per-Ticker Trading Parameters (UI Controls)
- ❌ NO way to change SL (Stop Loss) from UI
- ❌ NO way to change TP (Take Profit) from UI
- ❌ NO way to change SL Trail from UI
- ❌ Brick size can be set globally, NOT per-ticker

#### C. Per-Ticker Algo Toggle
- ❌ NO way to enable/disable algo for specific ticker
- ❌ Currently bot runs on entire watchlist at once
- ❌ NO per-ticker on/off control from UI

---

### 2. **Missing Backend Endpoints**

```
GET /tickers                    ❌ Get available tickers from MT5
GET /tickers/{symbol}/quote     ❌ Get live bid/ask for a symbol
POST /watchlist                 ❌ Add symbol to watchlist
GET /watchlist                  ✅ Get watchlist (partially done)
DELETE /watchlist/{symbol}      ❌ Remove symbol from watchlist
GET /watchlist/{symbol}         ❌ Get watchlist entry details
PUT /watchlist/{symbol}         ❌ Update trading params (SL, TP, trail, brick size)
POST /algo/toggle/{symbol}      ❌ Enable/Disable algo for specific ticker
GET /algo/status/{symbol}       ❌ Get algo status for ticker
```

---

### 3. **Missing Database Tables/Fields**

Current Supabase schema is incomplete. Missing:

```sql
-- Missing: watchlist table extended fields
-- Current: Only has symbol, is_active, lot_size
-- Needs: SL, TP, slope_trail_stop, brick_size (per symbol)

-- Missing: algo_control table
-- Needs: Track enabled/disabled algo per symbol per account

-- Missing: proper indexes and constraints
```

---

### 4. **Trade Execution Issues**

```
place_buy() and place_sell() signature:
  Current:  place_buy(session, symbol, price)
  Missing:  place_buy(session, symbol, price, sl, tp, trail_sl, lot_size)
```

The functions don't implement:
- ❌ Stop Loss (SL) in orders
- ❌ Take Profit (TP) in orders  
- ❌ Trailing Stop Loss in real-time monitoring
- ❌ Uses fixed lot_size from watchlist, not dynamic

---

### 5. **Worker/Bot Logic Issues**

Current behavior:
- ✅ Gets watchlist
- ✅ Checks if bot is running
- ⚠️ Missing: Per-symbol algo toggle check
- ❌ No logging of SL/TP levels
- ❌ No trailing stop implementation
- ❌ Doesn't monitor open positions for SL/TP

---

### 6. **Missing .env Example & Schema Files**

```
.env.example          ❌ Not created
supabase/schema.sql   ❌ Not created - NO TABLES EXIST!
```

---

## 🔧 What Needs to Be Done

### Phase 1: Database & Backend Setup (CRITICAL)
1. Create `supabase/schema.sql` with all tables
2. Create `.env.example` file
3. Add missing endpoints for tickers and watchlist management
4. Update trade execution functions with SL/TP/Trail

### Phase 2: Backend Enhancements
1. Add per-ticker algo toggle support
2. Implement trailing stop monitoring
3. Add SL/TP order parameters
4. Add per-symbol parameter storage

### Phase 3: Frontend Build-Out
1. Create Tickers Panel (show available symbols with bid/ask)
2. Create Watchlist Manager (add/remove/edit tickers)
3. Create Per-Ticker Controls (SL, TP, Trail, Brick Size)
4. Create Per-Ticker Toggle (enable/disable algo)

### Phase 4: Deployment
1. Prepare VPS environment setup guide
2. Create MT5 configuration checklist
3. Document deployment procedures

---

## 📋 Details You Need to Provide

### For MT5 VPS Setup:

1. **MT5 Installation Path**
   - Where is MT5 terminal installed? (e.g., `C:\Program Files\MetaTrader 5`)

2. **MT5 Broker Account**
   - Broker Name
   - Server Name (from MT5)
   - Account Login
   - Account Password

3. **Available Symbols**
   - List all symbols you want to trade (XAUUSD, EURUSD, etc.)
   - Which symbols are available on your broker?

4. **Position Management**
   - Max number of positions per symbol? (currently 1)
   - Max total positions per account?

5. **Trading Hours**
   - When should the bot run? (24/5, specific hours?)
   - Any weekends/holidays to skip?

6. **Risk Management**
   - What are your standard SL values? (pips or points)
   - What are your standard TP values?
   - Min/Max lot sizes per account?

---

## 🚀 Next Steps

I recommend:

1. **Read** the VPS Deployment Guide (I'll create it next)
2. **Gather** the 6 information items above
3. **Run the fixes** I'll provide:
   - Database schema
   - Backend endpoints
   - Frontend components
4. **Deploy** following the step-by-step guide

---

## Summary of Your Setup

| Component | Status | Details |
|-----------|--------|---------|
| Frontend | 40% Done | Missing ticker UI, watchlist, per-ticker controls |
| Backend API | 50% Done | Missing endpoints for tickers, watchlist params |
| Database | 0% Done | Schema not created yet |
| Trade Execution | 60% Done | Works but no SL/TP/Trail |
| Worker/Strategy | 70% Done | Works but needs per-symbol controls |
| Deployment | 0% Done | Not documented |

**Estimated code changes: ~2000 lines across backend + frontend**

