# Auto-Trading Quick Start Checklist

## ✅ Your Setup

- [x] BTCUSD added to watchlist
- [x] Brick size set to $1
- [x] Tables created in Supabase
- [ ] BTCUSD enabled (DO THIS FIRST)
- [ ] Backend running
- [ ] Monitoring activated

---

## 🚀 Do These 3 Things Now

### 1️⃣ Enable BTCUSD in Supabase (2 minutes)

**Method A: Via Supabase UI**
1. Go to https://supabase.co
2. Table Editor → `auto_trading_watchlist`
3. Find BTCUSD row
4. Click `enabled` cell
5. Change from `false` to `true`
6. Done!

**Method B: Via SQL**
```sql
UPDATE auto_trading_watchlist 
SET enabled = true 
WHERE symbol = 'BTCUSD';
```

**Verify:**
```sql
SELECT * FROM auto_trading_watchlist WHERE symbol = 'BTCUSD';
-- Should show: enabled = true
```

---

### 2️⃣ Make Sure Backend is Running (1 minute)

**Check Status:**
```bash
curl http://localhost:8000/api/auto-trading/status
```

**Expected Response:**
```json
{
  "running": true,
  "symbols": ["BTCUSD"],
  "positions": 0
}
```

**If Error:**
Start backend in terminal:
```bash
cd E:\Renko
python -m backend.main
```

---

### 3️⃣ Monitor for Trades (Continuous)

**Open 2 terminals side by side:**

**Terminal 1: Watch Backend Logs**
```bash
cd E:\Renko
python -m backend.main
```

Look for:
```
📊 Evaluating BTCUSD...
🟢 Brick color: green
💰 Executing BUY...
✅ Trade executed
```

**Terminal 2: Check Positions Every Minute**
```bash
# Run this every minute:
curl http://localhost:8000/api/auto-trading/positions
```

---

## 📊 Where to See Results

### Option 1: Backend Logs (Real-Time)
- Start backend and watch terminal
- See trade execution as it happens
- Most detailed information

### Option 2: Supabase UI
**Open Positions:**
```
Table Editor → auto_trading_positions
Refresh every minute
Should see BTCUSD with status=OPEN
```

**Trade History:**
```
Table Editor → auto_trading_history
Shows all trades with entry/exit prices
Shows P&L for closed trades
```

### Option 3: API Endpoints
```bash
# Current positions
curl http://localhost:8000/api/auto-trading/positions

# Trade history
curl http://localhost:8000/api/auto-trading/history

# Service status
curl http://localhost:8000/api/auto-trading/status
```

---

## ⏰ Timeline Expectations

| Time | What Happens | Where to Check |
|------|--------------|-----------------|
| Now | Enable BTCUSD | Supabase watchlist |
| +1 min | First evaluation | Backend logs |
| +1 min | First trade (maybe) | auto_trading_positions |
| +2 min | Second evaluation | Backend logs |
| +2 min | Second trade (maybe) | auto_trading_history |
| +5 min | Clear pattern | Both tables |

---

## 🔍 Signs It's Working

### ✅ Working Indicators
```
✅ Logs show "Evaluating BTCUSD..."
✅ auto_trading_positions has BTCUSD entry
✅ auto_trading_history shows trades
✅ /api/auto-trading/status shows running=true
✅ Prices moving, bricks forming
```

### ❌ Not Working Indicators
```
❌ No logs about BTCUSD evaluation
❌ auto_trading_positions is empty
❌ No entries in auto_trading_history
❌ Status endpoint errors
❌ MT5 disconnected
```

---

## 📝 Step-by-Step Instructions

### Step 1: Enable (Right Now)

Go to Supabase:
```
1. https://supabase.co
2. Select your project
3. Table Editor
4. Click: auto_trading_watchlist
5. Find BTCUSD row
6. Change: enabled = true
7. Done!
```

### Step 2: Verify Backend

In terminal:
```bash
curl http://localhost:8000/api/auto-trading/status
```

Should return:
```
"running": true
```

If not, start backend:
```bash
python -m backend.main
```

### Step 3: Start Monitoring

**Terminal 1:**
```bash
cd E:\Renko
python -m backend.main
```

**Terminal 2 (Optional):**
```bash
# Watch positions every 10 seconds
while true; do 
  curl http://localhost:8000/api/auto-trading/positions; 
  echo "---"; 
  sleep 10; 
done
```

**Browser:**
- Keep Supabase Table Editor open
- Watch auto_trading_positions
- Refresh periodically

---

## 💡 What to Expect

### Minute 1
- Auto-trader evaluates BTCUSD
- Gets current Renko brick color (green/red)
- This is the FIRST observation (no previous state to compare)
- Might not trade yet (needs comparison)

### Minute 2
- Auto-trader evaluates BTCUSD again
- Compares to previous brick color
- If color CHANGED: Executes trade!
- Trade appears in positions table

### Minute 3+
- Keeps evaluating every minute
- On each color change: Closes previous + opens new
- All trades logged to history

---

## 🆘 If No Trades After 5 Minutes

### Check 1: Is BTCUSD Enabled?
```sql
SELECT enabled, symbol FROM auto_trading_watchlist WHERE symbol = 'BTCUSD';
-- Must show: enabled = true
```

### Check 2: Is Backend Running?
```bash
curl http://localhost:8000/api/auto-trading/status
-- Must show: "running": true, and "BTCUSD" in symbols
```

### Check 3: Are Prices Updating?
```bash
curl http://localhost:8000/api/tickers/BTCUSD/quote
-- Should show current bid/ask prices
```

### Check 4: Any Errors in Logs?
Look at backend terminal for ERROR messages

### Check 5: Increase Brick Size
```sql
UPDATE auto_trading_watchlist 
SET brick_size = 5.0 
WHERE symbol = 'BTCUSD';
```

Larger brick size = fewer trades = more reliable signals

---

## 📱 Quick Commands

```bash
# Check status
curl http://localhost:8000/api/auto-trading/status

# View positions
curl http://localhost:8000/api/auto-trading/positions

# View history
curl http://localhost:8000/api/auto-trading/history

# Check BTCUSD quote
curl http://localhost:8000/api/tickers/BTCUSD/quote

# Check if BTCUSD enabled
curl "http://localhost:8000/api/auto-trading/watchlist"
```

---

## 🎯 SUCCESS = One of These

Within 5 minutes, you'll see:

**Option 1: In Backend Logs**
```
📊 Evaluating BTCUSD...
🟢 Brick: green → red (COLOR CHANGE!)
💰 Executing SELL trade...
✅ SELL executed at 42500.00
```

**Option 2: In Supabase**
```
auto_trading_positions:
  symbol: BTCUSD
  direction: SELL
  entry_price: 42500.00
  status: OPEN
```

**Option 3: Via API**
```bash
curl http://localhost:8000/api/auto-trading/positions
# Returns BTCUSD with status=OPEN
```

---

## 🚀 Go Live Now!

1. **Enable BTCUSD** in Supabase (do this first!)
2. **Start backend** (if not already running)
3. **Watch logs** in terminal
4. **Monitor Supabase** for trades
5. **See results** in 1-2 minutes

Your auto-trading system is live! 🎉

---

## Files for Reference

- `TEST_AUTO_TRADING.md` - Detailed monitoring guide
- `QUICK_REFERENCE.txt` - Quick command reference

All in `E:\Renko\`

---

## Questions?

The system will:
- Evaluate BTCUSD every 1 minute
- Execute trades on brick color changes
- Log everything to Supabase
- Show P&L on trade close

Good luck! 🚀
