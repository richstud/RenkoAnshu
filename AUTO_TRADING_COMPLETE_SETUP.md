# ✅ Auto-Trading from Watchlist - Complete Setup Guide

## What's Ready

✅ **Backend Updated:**
- Auto-trader now reads from existing `watchlist` table
- Checks `algo_enabled = true` to start auto-trading
- Uses `brick_size` from watchlist for each symbol
- Reloads watchlist every 30 seconds to pick up UI changes

✅ **New Watchlist API Endpoints Created:**
- `POST /api/watchlist/add` - Add symbol to watchlist with auto-trading
- `PUT /api/watchlist/{symbol}/algo` - Enable/disable auto-trading
- `PUT /api/watchlist/{symbol}/brick-size` - Update brick size
- `GET /api/watchlist` - Get all watchlist items
- `DELETE /api/watchlist/{symbol}` - Remove from watchlist

---

## How It Works (User Flow)

```
1. User adds BTCUSD to watchlist (brick_size=$1)
   ↓
2. User checks "Auto-Trade" checkbox
   ↓
3. Frontend sends: PUT /api/watchlist/BTCUSD/algo?algo_enabled=true
   ↓
4. Backend updates watchlist table (algo_enabled=true)
   ↓
5. Auto-trader reloads in 30 seconds
   ↓
6. Auto-trader sees BTCUSD with algo_enabled=true
   ↓
7. Starts monitoring with brick_size=$1
   ↓
8. Every 1 minute: Evaluates brick color
   ↓
9. On color change: Executes trade
   ↓
10. Trades logged to auto_trading_positions & auto_trading_history
```

---

## Setup Steps

### Step 1: Restart Backend

```bash
cd E:\Renko
# Stop current backend (Ctrl+C)
# Then restart:
python -m backend.main
```

Should see:
```
✅ Auto-Trader initialized with 0 symbols
📋 Loaded 0 symbols from watchlist (algo_enabled=true)
```

### Step 2: Test API (Add BTCUSD)

```bash
# Add BTCUSD to watchlist with auto-trading enabled
curl -X POST http://localhost:8000/api/watchlist/add \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTCUSD",
    "brick_size": 1.0,
    "lot_size": 0.1,
    "algo_enabled": true,
    "stop_loss_pips": 50,
    "take_profit_pips": 100
  }' \
  -G --data-urlencode "account_id=12345"
```

### Step 3: Verify in Database

```sql
SELECT symbol, brick_size, algo_enabled 
FROM watchlist 
WHERE symbol = 'BTCUSD';
```

Should show:
```
BTCUSD | 1.0 | true
```

### Step 4: Wait 30 Seconds

Backend reloads watchlist every 30 seconds.

### Step 5: Check Status

```bash
curl http://localhost:8000/api/auto-trading/status
```

Should now show:
```json
{
  "service": {
    "running": true,
    "enabled_symbols": ["BTCUSD"],
    "symbol_count": 1
  }
}
```

### Step 6: Watch Logs

In backend terminal, you should see:
```
📊 Evaluating BTCUSD with brick_size=1.0...
🟢 Brick color: green
💰 Executing BUY...
✅ Trade executed
```

---

## Frontend Integration (What to Build)

Your watchlist component needs:

### 1. Display Columns

```
Symbol | Brick Size | Lot Size | Auto-Trade | Status | Actions
BTCUSD | 1.0        | 0.1      | ☑ ON       | 🟢     | Edit Remove
EURUSD | 0.0005     | 0.01     | ☐ OFF      | ⚫     | Edit Remove
```

### 2. Add Symbol Form

```html
<form>
  <input type="text" placeholder="Symbol" id="symbol" />
  <input type="number" placeholder="Brick Size" id="brickSize" value="1.0" />
  <input type="number" placeholder="Lot Size" id="lotSize" value="0.01" />
  <label>
    <input type="checkbox" id="autoTrade" /> Enable Auto-Trading
  </label>
  <button type="submit">Add to Watchlist</button>
</form>
```

### 3. JavaScript Example

```javascript
// Add symbol to watchlist
async function addToWatchlist(e) {
  e.preventDefault();
  
  const symbol = document.getElementById('symbol').value;
  const brickSize = parseFloat(document.getElementById('brickSize').value);
  const lotSize = parseFloat(document.getElementById('lotSize').value);
  const autoTrade = document.getElementById('autoTrade').checked;
  const accountId = 12345; // Your account ID
  
  const response = await fetch(`/api/watchlist/add?account_id=${accountId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      symbol,
      brick_size: brickSize,
      lot_size: lotSize,
      algo_enabled: autoTrade
    })
  });
  
  const result = await response.json();
  console.log('Added to watchlist:', result);
  
  // Refresh watchlist display
  loadWatchlist();
}

// Toggle auto-trading
async function toggleAutoTrade(symbol, enabled) {
  const accountId = 12345;
  
  const response = await fetch(
    `/api/watchlist/${symbol}/algo?algo_enabled=${enabled}&account_id=${accountId}`,
    { method: 'PUT' }
  );
  
  const result = await response.json();
  console.log('Updated:', result);
  
  // Refresh watchlist
  loadWatchlist();
}

// Update brick size
async function updateBrickSize(symbol, brickSize) {
  const accountId = 12345;
  
  const response = await fetch(
    `/api/watchlist/${symbol}/brick-size?brick_size=${brickSize}&account_id=${accountId}`,
    { method: 'PUT' }
  );
  
  const result = await response.json();
  console.log('Updated:', result);
  
  // Refresh
  loadWatchlist();
}

// Load watchlist
async function loadWatchlist() {
  const accountId = 12345;
  
  const response = await fetch(`/api/watchlist?account_id=${accountId}`);
  const result = await response.json();
  
  console.log('Watchlist:', result.symbols);
  
  // Render symbols in table
  renderWatchlist(result.symbols);
}

// Remove from watchlist
async function removeFromWatchlist(symbol) {
  const accountId = 12345;
  
  const response = await fetch(
    `/api/watchlist/${symbol}?account_id=${accountId}`,
    { method: 'DELETE' }
  );
  
  const result = await response.json();
  console.log('Removed:', result);
  
  // Refresh
  loadWatchlist();
}
```

---

## Testing Checklist

- [ ] Restart backend with new code
- [ ] Add BTCUSD via API (or UI when built)
- [ ] Set algo_enabled = true in watchlist table
- [ ] Wait 30 seconds for auto-trader to reload
- [ ] Check status endpoint shows BTCUSD enabled
- [ ] Watch backend logs for evaluation messages
- [ ] See trades appear in auto_trading_positions
- [ ] View trade history in auto_trading_history

---

## API Reference

### Add to Watchlist
```bash
POST /api/watchlist/add?account_id=12345

{
  "symbol": "BTCUSD",
  "brick_size": 1.0,
  "lot_size": 0.1,
  "algo_enabled": true,
  "stop_loss_pips": 50,
  "take_profit_pips": 100
}

Response:
{
  "status": "success",
  "message": "Symbol BTCUSD added/updated in watchlist",
  "algo_enabled": true,
  "note": "Auto-trading will start within 30 seconds if algo_enabled=true"
}
```

### Toggle Auto-Trading
```bash
PUT /api/watchlist/BTCUSD/algo?algo_enabled=true&account_id=12345

Response:
{
  "status": "success",
  "symbol": "BTCUSD",
  "algo_enabled": true,
  "message": "Auto-trading enabled for BTCUSD"
}
```

### Update Brick Size
```bash
PUT /api/watchlist/BTCUSD/brick-size?brick_size=2.0&account_id=12345

Response:
{
  "status": "success",
  "symbol": "BTCUSD",
  "brick_size": 2.0,
  "message": "Brick size updated to 2.0"
}
```

### Get Watchlist
```bash
GET /api/watchlist?account_id=12345

Response:
{
  "status": "success",
  "account_id": 12345,
  "symbols": [
    {
      "id": 1,
      "symbol": "BTCUSD",
      "brick_size": 1.0,
      "algo_enabled": true,
      "lot_size": 0.1
    }
  ],
  "count": 1
}
```

### Remove from Watchlist
```bash
DELETE /api/watchlist/BTCUSD?account_id=12345

Response:
{
  "status": "success",
  "symbol": "BTCUSD",
  "message": "Symbol BTCUSD removed from watchlist"
}
```

---

## Expected Behavior

### After Adding BTCUSD with algo_enabled=true:

**Within 30 seconds:**
- Backend loads watchlist
- Sees BTCUSD with algo_enabled=true
- Starts monitoring with brick_size=1.0

**Every minute:**
- Evaluates brick color change
- On color change: Executes trade
- Logs to database

**Visible in UI:**
- Backend logs show evaluation
- Supabase shows trade in positions
- Status endpoint shows BTCUSD enabled

---

## Files Updated

- ✅ `backend/services/auto_trader.py` - Reads from watchlist table
- ✅ `backend/api/watchlist.py` - New watchlist API endpoints
- ✅ `backend/main.py` - Added watchlist router

---

## Summary

Your system now:
1. ✅ Reads from existing watchlist table
2. ✅ Checks algo_enabled to start auto-trading
3. ✅ Uses brick_size from UI settings
4. ✅ Automatically reloads every 30 seconds
5. ✅ Picks up UI changes immediately
6. ⏳ Needs frontend UI integration

**Everything is ready for testing!**

Push to GitHub, pull on VPS, restart backend, and start trading! 🚀
