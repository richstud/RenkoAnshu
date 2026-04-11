# ✅ AUTO-TRADING FROM WATCHLIST - READY TO GO

## What I've Done

✅ **Updated Backend**
- Auto-trader now reads from your existing `watchlist` table
- Looks for `algo_enabled = true` to start trading
- Uses `brick_size` from each watchlist entry
- Reloads every 30 seconds to pick up UI changes

✅ **Created Watchlist API Endpoints**
- POST /api/watchlist/add - Add symbol with auto-trading
- PUT /api/watchlist/{symbol}/algo - Enable/disable auto-trading
- PUT /api/watchlist/{symbol}/brick-size - Update brick size
- GET /api/watchlist - Get all symbols
- DELETE /api/watchlist/{symbol} - Remove symbol

✅ **Integrated with Main App**
- New watchlist router added to FastAPI

---

## How It Works (For Users)

1. **Add BTCUSD to watchlist** with brick_size=$1
2. **Check "Auto-Trade"** checkbox
3. **Submit** → Updates database
4. **Auto-trader picks it up** within 30 seconds
5. **Starts monitoring** BTCUSD every minute
6. **Executes trades** on brick color changes
7. **Logs to database** automatically

---

## Quick Test (Before UI)

### 1. Restart Backend
```bash
cd E:\Renko
python -m backend.main
```

### 2. Add BTCUSD via API
```bash
curl -X POST http://localhost:8000/api/watchlist/add \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTCUSD",
    "brick_size": 1.0,
    "lot_size": 0.1,
    "algo_enabled": true
  }' \
  -G --data-urlencode "account_id=12345"
```

### 3. Check Status
```bash
curl http://localhost:8000/api/auto-trading/status
```

Should show:
```json
"enabled_symbols": ["BTCUSD"],
"symbol_count": 1
```

### 4. Watch Logs
```
📊 Evaluating BTCUSD with brick_size=1.0...
🟢 Brick color changed!
💰 Executing trade...
✅ Trade executed
```

---

## Next: Build Frontend UI

Your watchlist component needs:

### Add Symbol Form
```html
<input type="text" placeholder="Symbol" />
<input type="number" placeholder="Brick Size" value="1.0" />
<input type="number" placeholder="Lot Size" value="0.01" />
<label>
  <input type="checkbox" /> Auto-Trade
</label>
<button>Add</button>
```

### Watchlist Table
```
Symbol  | Brick | Lot | Auto-Trade | Remove
BTCUSD  | 1.0   | 0.1 | ☑ ON       | ✕
```

### Key Functions
```javascript
// Add to watchlist
POST /api/watchlist/add?account_id=12345

// Toggle auto-trading
PUT /api/watchlist/BTCUSD/algo?algo_enabled=true&account_id=12345

// Update brick size
PUT /api/watchlist/BTCUSD/brick-size?brick_size=2.0&account_id=12345

// Remove from watchlist
DELETE /api/watchlist/BTCUSD?account_id=12345
```

---

## Files Changed

- ✅ `backend/services/auto_trader.py` - Reads watchlist table
- ✅ `backend/api/watchlist.py` - New API endpoints
- ✅ `backend/main.py` - Added watchlist router

---

## Deploy to VPS

```bash
# 1. Commit changes
git add -A
git commit -m "feat: Auto-trading from watchlist UI"
git push origin main

# 2. On VPS
git pull origin main

# 3. Restart
python -m backend.main
```

---

## Status

✅ Backend: Ready
✅ API: Ready
✅ Database: Ready
⏳ Frontend: Needs UI implementation

**Ready to test!** 🚀

See `AUTO_TRADING_COMPLETE_SETUP.md` for full details and code examples.
