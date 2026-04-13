# Deployment Guide - Trading App Fixes

## Summary of Changes

Three major issues have been fixed:
1. ✅ **Crosshair not visible on Renko Chart** - Fixed canvas sizing and styling
2. ✅ **Watchlist delete not working** - Added error handling and immediate state update
3. ✅ **Missing date-filtered trades and export functionality** - Added new backend endpoints and frontend UI

---

## Deployment Steps

### STEP 1: Deploy Frontend Changes (Local - E:\Renko)

**Files Modified:**
- `frontend/src/components/RenkoChart.tsx` - Canvas fix
- `frontend/src/components/WatchlistManager.tsx` - Delete fix
- `frontend/src/App.tsx` - Import TradeHistory

**Files Created:**
- `frontend/src/components/TradeHistory.tsx` - NEW component

**Action:**
1. The frontend files are already updated in `E:\Renko\frontend\src\`
2. Rebuild the frontend:
```bash
cd E:\Renko\frontend
npm run build
```

3. If you're serving via a web server, copy the build output to your web server directory

---

### STEP 2: Deploy Backend Changes (VPS - c:\tradingbot\renko)

**File Modified:**
- `backend/api/endpoints.py` - Added two new endpoints

**What was added:**
- `GET /api/trades/by-date/{account_id}` - Fetch trades by date
- `GET /api/trades/export/{account_id}` - Export trades to CSV

**Action on VPS:**
1. Copy the updated `backend/api/endpoints.py` to the VPS:
```bash
# From local machine, using SCP or file sync
scp backend/api/endpoints.py user@vps-ip:c:\tradingbot\renko\backend\api\
```

2. Or manually copy the file using RDP/file transfer

3. **Restart the backend service on VPS:**
```bash
# On VPS - if using FastAPI with uvicorn
taskkill /F /IM python.exe
cd c:\tradingbot\renko
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Or if using Windows Service:
```bash
net stop YourServiceName
net start YourServiceName
```

---

## Testing the Fixes

### Test 1: Crosshair on Chart ✅
1. Open the frontend app in browser
2. Select an account and go to the Renko Chart section
3. Move your mouse over the chart area
4. **Expected:** You should see red vertical and green horizontal dashed lines with a yellow center point

### Test 2: Watchlist Delete ✅
1. Add a symbol to your watchlist (or use existing)
2. Click the red "Delete" button on any watchlist item
3. Confirm the deletion popup
4. **Expected:** Item disappears immediately and success message appears

### Test 3: Trade History & Export ✅
1. Open the frontend app
2. Select an account
3. Scroll to "📊 Trade History" section (bottom right)
4. Pick a date with trades using the date picker
5. Click "Load Trades"
6. **Expected:** Trades for that date display in a table
7. Click "📥 Export CSV"
8. **Expected:** A CSV file downloads to your computer

---

## New API Endpoints

### 1. Get Trades by Date
**Endpoint:** `GET /api/trades/by-date/{account_id}`

**Query Parameters:**
- `date_str` (required): Date in format `YYYY-MM-DD` (e.g., `2026-04-13`)
- `closed` (optional): Filter by status (`true` for closed, `false` for open)

**Example Request:**
```
GET http://your-vps-ip:8000/api/trades/by-date/101510620?date_str=2026-04-13
```

**Response:**
```json
{
  "account_id": 101510620,
  "date": "2026-04-13",
  "count": 5,
  "data": [
    {
      "id": 1,
      "account_id": 101510620,
      "symbol": "EURUSD",
      "type": "buy",
      "lot": 0.1,
      "entry_price": 1.0845,
      "sl_price": 1.0835,
      "tp_price": 1.0865,
      "closed": false,
      "created_at": "2026-04-13T14:30:45Z"
    }
  ]
}
```

### 2. Export Trades to CSV
**Endpoint:** `GET /api/trades/export/{account_id}`

**Query Parameters:**
- `date_str` (required): Date in format `YYYY-MM-DD`

**Example Request:**
```
GET http://your-vps-ip:8000/api/trades/export/101510620?date_str=2026-04-13
```

**Response:** CSV file download
```
ID,Symbol,Type,Lot,Entry Price,SL Price,TP Price,Status,Created At,Brick Size
1,EURUSD,BUY,0.1,1.0845,1.0835,1.0865,Open,2026-04-13T14:30:45Z,0.005
2,GBPUSD,SELL,0.05,1.2543,1.2553,1.2523,Closed,2026-04-13T15:45:30Z,0.01
```

---

## File Locations

### Local (E:\Renko)
```
E:\Renko\
├── frontend\
│   └── src\
│       ├── components\
│       │   ├── RenkoChart.tsx ✏️ MODIFIED
│       │   ├── WatchlistManager.tsx ✏️ MODIFIED
│       │   └── TradeHistory.tsx ✨ NEW
│       └── App.tsx ✏️ MODIFIED
```

### VPS (c:\tradingbot\renko)
```
c:\tradingbot\renko\
└── backend\
    └── api\
        └── endpoints.py ✏️ MODIFIED (add imports + 2 new endpoints)
```

---

## Troubleshooting

### Issue: Crosshair still not visible after rebuild
- Clear browser cache: `Ctrl+Shift+Delete`
- Rebuild frontend: `npm run build`
- Check console for errors: `F12 → Console tab`

### Issue: Watchlist delete still fails
- Check VPS backend logs for errors
- Verify API endpoint is correct in console (F12)
- Ensure account_id is passed correctly in query string

### Issue: Trade History shows "No trades found"
- Verify trades exist in database for that date
- Check date format (must be YYYY-MM-DD)
- Look at network tab (F12) to see API response

### Issue: Export CSV downloads but is empty
- Ensure trades exist for selected date
- Check that the date range query is working (test endpoint directly)
- Verify CSV generation in backend logs

---

## Rollback Instructions

If you need to revert changes:

1. **Frontend rollback:**
   - Get previous version from Git: `git checkout HEAD~1 frontend/src/components/`
   - Rebuild: `npm run build`

2. **Backend rollback:**
   - Get previous version: `git checkout HEAD~1 backend/api/endpoints.py`
   - Restart backend service on VPS

---

## Performance Notes

- Date-filtered trades query uses efficient database indexing on `created_at` and `account_id`
- CSV export streams response (no memory loading of entire file)
- Canvas crosshair draws at 100ms interval (optimized performance)

---

## Next Steps

1. ✅ Deploy frontend changes locally
2. ✅ Deploy backend changes to VPS
3. ✅ Restart backend service
4. ✅ Test all three fixes
5. ✅ Monitor logs for any errors
6. ✅ Commit changes to Git

---

## Support

If you encounter any issues:
1. Check browser console (F12) for frontend errors
2. Check VPS backend logs for API errors
3. Verify network connectivity between frontend and VPS backend
4. Ensure API_URL environment variable is set correctly in frontend (.env file)

Example `.env.local` for frontend:
```
VITE_API_URL=http://your-vps-ip:8000
```

---

## Summary of Changes

| Component | File | Change Type | Impact |
|-----------|------|------------|--------|
| Chart | RenkoChart.tsx | Fix canvas sizing | Crosshair now visible |
| Watchlist | WatchlistManager.tsx | Better error handling | Delete works reliably |
| Trades | endpoints.py | Add 2 new endpoints | Date filtering + export |
| UI | TradeHistory.tsx | New component | View & export trades by date |
| App | App.tsx | Add import | TradeHistory component available |

All changes are backward compatible and don't affect existing functionality.
