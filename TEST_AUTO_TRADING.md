# Testing Auto-Trading - BTCUSD Live Test

## Status: BTCUSD Added to Watchlist ✅

You've added BTCUSD with brick size $1. Now let's enable and monitor it.

---

## Step 1: Enable Auto-Trading for BTCUSD

### Update in Supabase (Enable the Symbol)

Go to Supabase → Table Editor → `auto_trading_watchlist`

Find the BTCUSD row and update:
```
enabled = true
```

Or use SQL:
```sql
UPDATE auto_trading_watchlist 
SET enabled = true 
WHERE symbol = 'BTCUSD';
```

### Verify
```sql
SELECT * FROM auto_trading_watchlist WHERE symbol = 'BTCUSD';
```

Should show:
```
symbol    | enabled | brick_size
BTCUSD    | true    | 1.0
```

---

## Step 2: Check Backend is Running

### Test Backend Connection
```bash
curl http://localhost:8000/api/auto-trading/status
```

Expected response:
```json
{
  "running": true,
  "symbols": ["BTCUSD"],
  "positions": 0
}
```

If you get error, backend isn't running. Start it:
```bash
cd E:\Renko
python -m backend.main
```

---

## Step 3: Monitor Auto-Trading Execution

### Check 1: Backend Logs
Watch the terminal where backend is running. Look for:

```
📊 Evaluating BTCUSD...
Brick color: green
Trade signal detected!
Executing BUY trade...
```

Or for SELL:
```
Brick color: red
Trade signal detected!
Executing SELL trade...
```

### Check 2: Check Open Positions
```bash
curl http://localhost:8000/api/auto-trading/positions
```

Expected when trade is open:
```json
{
  "positions": [
    {
      "symbol": "BTCUSD",
      "direction": "BUY",
      "entry_price": 42500.00,
      "lot_size": 0.1,
      "status": "OPEN"
    }
  ]
}
```

### Check 3: View in Supabase

**Open Positions:**
```
Supabase → Table Editor → auto_trading_positions
Look for BTCUSD entry with status=OPEN
```

**Trade History:**
```
Supabase → Table Editor → auto_trading_history
Look for recent BTCUSD trades
Should see: symbol, direction (BUY/SELL), entry_price, entry_time
```

---

## Step 4: Full Monitoring Command

Get comprehensive status:

```bash
# Check if service is running
curl http://localhost:8000/api/auto-trading/status

# Check current positions
curl http://localhost:8000/api/auto-trading/positions

# Get trade history
curl http://localhost:8000/api/auto-trading/history
```

---

## What Auto-Trading Does (Every 1 Minute)

```
1 min: Auto-trader runs
   ↓
Gets Renko chart for BTCUSD
   ↓
Evaluates brick color:
   - Green brick = BUY signal
   - Red brick = SELL signal
   ↓
If signal detected:
   - Check for existing position
   - If yes: Close it first (sell if long)
   - Then: Open new position (buy if green, sell if red)
   ↓
Trade executed on MT5
   ↓
Logged to auto_trading_positions (status=OPEN)
   ↓
Later when closed: Moved to auto_trading_history with P&L
```

---

## Real-Time Monitoring Setup

### Terminal 1: Watch Backend Logs
```bash
cd E:\Renko
python -m backend.main
```

Watch for:
```
🤖 Auto-Trader running...
📊 Evaluating BTCUSD...
🟢 Green brick detected
💰 Executing BUY...
✅ Trade executed
```

### Terminal 2: Poll Status Every 10 Seconds
```bash
# Linux/Mac
watch -n 10 'curl -s http://localhost:8000/api/auto-trading/positions | jq .'

# Windows (PowerShell)
while($true) { 
  curl http://localhost:8000/api/auto-trading/positions; 
  Start-Sleep -Seconds 10 
}
```

### Terminal 3: Check Supabase (In Browser)
Keep Supabase Table Editor open showing:
1. auto_trading_positions (current trades)
2. auto_trading_history (all trades)

Refresh every 10 seconds to see new trades.

---

## Expected Behavior

### First 1 Minute
- Auto-trader evaluates BTCUSD
- Checks if brick color changed
- If yes: Executes first trade
- Trade shows in auto_trading_positions with status=OPEN

### Next Trade
- After 1 minute: Checks again
- If brick color changed from previous: Closes last trade + opens new one
- Old trade moves to history with P&L

### Continuous
- Every minute: Evaluates, detects color changes, executes trades
- Positions stay open until color changes
- All trades logged to history

---

## Troubleshooting

### No trades executing

**Check 1: Is BTCUSD enabled?**
```sql
SELECT enabled FROM auto_trading_watchlist WHERE symbol = 'BTCUSD';
-- Should return: true
```

**Check 2: Is backend running?**
```bash
curl http://localhost:8000/api/auto-trading/status
-- Should return: "running": true
```

**Check 3: Are there any errors in backend logs?**
Look for ERROR or WARNING messages in terminal

**Check 4: Is MT5 connected?**
- Open MT5 terminal
- Check if it's logged in
- Verify BTCUSD symbol is available

**Check 5: Wait for 1 minute**
Auto-trader only evaluates every 1 minute (on 1-min candle close)

### Trades executing but closing immediately

**Reason:** Brick color might be oscillating

**Solution:**
- Increase brick size to $2 or $5
- This reduces false signals
- Update in Supabase:
```sql
UPDATE auto_trading_watchlist 
SET brick_size = 5.0 
WHERE symbol = 'BTCUSD';
```

### Lot size too small

**Check current lot:**
```sql
SELECT lot_size_rules FROM auto_trading_watchlist WHERE symbol = 'BTCUSD';
```

**Update lot sizing:**
```sql
UPDATE auto_trading_watchlist 
SET lot_size_rules = '{"balance_less_100": 0.01, "balance_101_500": 0.1, "balance_501_plus": 0.5}'
WHERE symbol = 'BTCUSD';
```

---

## Quick Reference: Commands to Run Now

### 1. Enable BTCUSD in Supabase
```sql
UPDATE auto_trading_watchlist SET enabled = true WHERE symbol = 'BTCUSD';
SELECT * FROM auto_trading_watchlist WHERE symbol = 'BTCUSD';
```

### 2. Check Backend Running
```bash
curl http://localhost:8000/api/auto-trading/status
```

### 3. Monitor Positions
```bash
curl http://localhost:8000/api/auto-trading/positions
```

### 4. View Recent Trades
```bash
curl http://localhost:8000/api/auto-trading/history
```

### 5. Watch Backend Logs
```bash
# In separate terminal
cd E:\Renko && python -m backend.main
```

---

## Expected Results After 5 Minutes

| Item | Status |
|------|--------|
| BTCUSD enabled | ✅ true in watchlist |
| Backend running | ✅ /status responds with running=true |
| First evaluation | ✅ "Evaluating BTCUSD..." in logs |
| First trade | ✅ Entry appears in auto_trading_positions |
| Trade logged | ✅ Shows in auto_trading_history |

---

## Next Steps

1. ✅ Enable BTCUSD (enabled = true)
2. ✅ Check backend running
3. ✅ Wait 1 minute for first evaluation
4. ✅ Watch logs for trade execution
5. ✅ Check positions table for open trade
6. ✅ Wait for next brick color change (next trade)

---

## Real-Time Chart

Your chart on frontend should:
- Show live BTCUSD Renko bricks
- Display bid/ask prices
- Update every 2 seconds
- Auto-trader evaluates this data every 1 minute

When auto-trader executes trade:
- Your open positions should update
- Trade history should show execution
- Next trade triggers on next brick color change

---

## Success Indicators

### ✅ Everything Working
```
Log: "✅ Trade executed for BTCUSD"
Supabase: Entry in auto_trading_positions with status=OPEN
Backend: /api/auto-trading/status shows symbol in list
```

### ❌ Not Working
```
No logs about evaluation
Supabase: auto_trading_positions is empty
Backend: Error messages in terminal
MT5: Not connected or price not updating
```

---

## Start Now! 🚀

1. Update BTCUSD enabled = true in Supabase
2. Verify backend is running
3. Watch the logs
4. Monitor Supabase tables
5. Check positions after each evaluation

Good luck! Your auto-trading system is live! 🎉
