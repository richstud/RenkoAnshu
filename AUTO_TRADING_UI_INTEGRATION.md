# Auto-Trading Integration with Watchlist

## Changes Made ✅

### Backend Updated
Your backend now:
1. **Reads from existing `watchlist` table** (not separate auto_trading_watchlist)
2. **Checks `algo_enabled = true`** to start auto-trading
3. **Uses `brick_size` from watchlist** for each symbol
4. **Reloads watchlist every 30 seconds** to pick up new symbols added from UI

### How It Works Now

```
User adds symbol in watchlist UI (e.g., BTCUSD with brick_size=$1)
    ↓
User sets algo_enabled = true
    ↓
Backend loads watchlist (every 30 sec)
    ↓
Auto-trader finds BTCUSD with algo_enabled=true
    ↓
Auto-trader starts monitoring BTCUSD with brick_size=$1
    ↓
Every 1 minute: Evaluates Renko brick color
    ↓
On color change: Executes trade
    ↓
Trades logged to database
```

---

## Frontend UI Required

You need to add UI controls in your watchlist to enable/disable auto-trading. Here's what's needed:

### Component: WatchlistItem.tsx (or similar)

```tsx
// Add this to your watchlist component for each symbol

<tr>
  <td>{symbol}</td>
  <td>
    <input 
      type="number" 
      value={brickSize} 
      onChange={(e) => updateBrickSize(symbol, e.target.value)}
      placeholder="e.g., 1.0"
    />
  </td>
  <td>
    <input 
      type="number" 
      value={lotSize}
      onChange={(e) => updateLotSize(symbol, e.target.value)}
    />
  </td>
  <td>
    <label>
      <input 
        type="checkbox" 
        checked={algoEnabled}
        onChange={(e) => updateAlgoEnabled(symbol, e.target.checked)}
      />
      Auto-Trade
    </label>
  </td>
  <td>
    <button onClick={() => removeTicker(symbol)}>Remove</button>
  </td>
</tr>
```

### API Calls Needed

**Add/Update Symbol:**
```typescript
// POST to /api/watchlist/add or UPDATE
async function addToWatchlist(symbol: string, brickSize: number, algoEnabled: boolean) {
  const response = await fetch('/api/watchlist/add', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      symbol,
      brick_size: brickSize,
      algo_enabled: algoEnabled,
      lot_size: 0.01
    })
  });
  return response.json();
}
```

**Enable/Disable Auto-Trading:**
```typescript
async function toggleAutoTrading(symbol: string, enabled: boolean) {
  const response = await fetch(`/api/watchlist/${symbol}/algo`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ algo_enabled: enabled })
  });
  return response.json();
}
```

**Update Brick Size:**
```typescript
async function updateBrickSize(symbol: string, brickSize: number) {
  const response = await fetch(`/api/watchlist/${symbol}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ brick_size: brickSize })
  });
  return response.json();
}
```

---

## Database Table Schema

Your `watchlist` table already has these columns:

```sql
CREATE TABLE watchlist (
    id BIGSERIAL PRIMARY KEY,
    account_id BIGINT NOT NULL,
    symbol TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true,
    
    -- Trading Parameters (per symbol)
    lot_size FLOAT DEFAULT 0.01,
    stop_loss_pips FLOAT DEFAULT 50,
    take_profit_pips FLOAT DEFAULT 100,
    trailing_stop_pips FLOAT DEFAULT 30,
    use_trailing_stop BOOLEAN DEFAULT false,
    
    -- Renko brick size
    brick_size FLOAT DEFAULT 1.0,
    
    -- AUTO-TRADING CONTROL
    algo_enabled BOOLEAN DEFAULT false,  ← THIS ENABLES AUTO-TRADING
    
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    
    UNIQUE(account_id, symbol)
);
```

---

## How to Use (User Perspective)

1. **Open Watchlist page** in frontend
2. **Add Symbol:** Enter BTCUSD, brick_size=$1
3. **Set Brick Size:** e.g., 1.0 for BTCUSD
4. **Enable Auto-Trading:** Check the "Auto-Trade" checkbox
5. **Submit:** Save to database
6. **Auto-trading starts automatically** (within 30 seconds)

---

## Testing

### After Adding BTCUSD with algo_enabled=true:

**Check 1: Verify in Supabase**
```sql
SELECT symbol, brick_size, algo_enabled 
FROM watchlist 
WHERE symbol = 'BTCUSD';
-- Should show: BTCUSD | 1.0 | true
```

**Check 2: Check backend status**
```bash
curl http://localhost:8000/api/auto-trading/status
```

Should show:
```json
{
  "enabled_symbols": ["BTCUSD"],
  "symbol_count": 1
}
```

**Check 3: Wait 30 seconds**
Backend reloads watchlist every 30 seconds. After that, auto-trading starts.

**Check 4: Check logs**
Should see:
```
📊 Evaluating BTCUSD with brick_size=1.0...
```

**Check 5: Trades appear**
```bash
curl http://localhost:8000/api/auto-trading/positions
```

---

## Backend API Endpoints (To Create)

Add these endpoints if not already present:

```python
# GET watchlist for account
@router.get("/api/watchlist")
async def get_watchlist(account_id: int):
    # Return all symbols in watchlist for account
    pass

# POST add to watchlist
@router.post("/api/watchlist/add")
async def add_to_watchlist(symbol: str, brick_size: float, algo_enabled: bool):
    # Insert/update watchlist entry
    # Auto-trader will pick it up in 30 seconds
    pass

# PUT update algo_enabled
@router.put("/api/watchlist/{symbol}/algo")
async def update_algo(symbol: str, algo_enabled: bool):
    # Update algo_enabled flag
    pass

# PUT update brick_size
@router.put("/api/watchlist/{symbol}/brick-size")
async def update_brick_size(symbol: str, brick_size: float):
    # Update brick_size
    # Auto-trader picks up new brick_size in 30 seconds
    pass

# DELETE remove from watchlist
@router.delete("/api/watchlist/{symbol}")
async def remove_from_watchlist(symbol: str):
    # Delete from watchlist
    # Auto-trader stops monitoring in 30 seconds
    pass
```

---

## Key Points

✅ **Uses existing watchlist table** - No separate tables needed
✅ **Auto-picks up new symbols** - Reloads every 30 seconds
✅ **Uses brick_size from UI** - Whatever user sets
✅ **Starts automatically** - Set algo_enabled=true, it starts
✅ **Real-time updates** - UI changes reflect within 30 seconds

---

## Next Steps

1. **Update Frontend Watchlist Component**
   - Add checkbox for "algo_enabled"
   - Add input for "brick_size"
   - Add API calls to update database

2. **Create Backend API Endpoints**
   - POST /api/watchlist/add
   - PUT /api/watchlist/{symbol}/algo
   - PUT /api/watchlist/{symbol}/brick-size
   - DELETE /api/watchlist/{symbol}

3. **Test End-to-End**
   - Add BTCUSD from UI
   - Set brick_size=1.0
   - Enable algo_enabled
   - See auto-trading start in logs

4. **Monitor**
   - Watch backend logs
   - Check Supabase watchlist table
   - View trade execution in positions/history

---

## Summary

Your auto-trading system now:
- ✅ Reads from your existing watchlist table
- ✅ Checks algo_enabled flag to start trading
- ✅ Uses brick_size from watchlist settings
- ✅ Automatically reloads every 30 seconds
- ✅ Picks up new symbols added from UI
- ⏳ Needs frontend UI (checkboxes + inputs)
- ⏳ Needs API endpoints to update watchlist

Everything is ready! Just need frontend updates to complete the flow.
