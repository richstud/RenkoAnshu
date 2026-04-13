# STEP-BY-STEP DEPLOYMENT & TESTING GUIDE

## 🎯 What Was Fixed

✅ **Crosshair not visible on chart** - Canvas sizing issue  
✅ **Watchlist delete not working** - Better error handling  
✅ **No trade history or export** - New backend endpoints + UI component  

---

## 📋 PRE-DEPLOYMENT CHECKLIST

- [ ] Backend file copied to VPS: `backend/api/endpoints.py`
- [ ] Frontend files updated locally: `E:\Renko\frontend\src\components\`
- [ ] Backend service stopped on VPS
- [ ] Database backup created (recommended)
- [ ] All users notified of maintenance window (optional)

---

## 🚀 DEPLOYMENT STEPS

### STEP 1: Backend Deployment (VPS - c:\tradingbot\renko)

#### 1.1 Stop Backend Service
```bash
# On VPS, stop the FastAPI backend
taskkill /F /IM python.exe

# Or if using Windows Service:
net stop YourBackendServiceName
```

#### 1.2 Backup Current File
```bash
# On VPS, backup the old file
cd c:\tradingbot\renko\backend\api
copy endpoints.py endpoints.py.backup
```

#### 1.3 Deploy New File
**Option A: Using RDP/File Transfer**
1. Open RDP connection to VPS
2. Navigate to `c:\tradingbot\renko\backend\api\`
3. Copy new `endpoints.py` from `E:\Renko\backend\api\endpoints.py`
4. Paste into VPS location
5. Confirm file size is larger (new code added)

**Option B: Using SCP/Secure Copy**
```bash
# From local machine (if you have SSH/SCP tools)
scp E:\Renko\backend\api\endpoints.py user@vps-ip:c:\tradingbot\renko\backend\api\
```

#### 1.4 Restart Backend Service
```bash
# On VPS, start the backend again
cd c:\tradingbot\renko
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Or if using Windows Service:
net start YourBackendServiceName
```

#### 1.5 Verify Backend Started
```bash
# Check if service is running (should see no errors)
# Wait 5-10 seconds for startup
# Test endpoint: http://vps-ip:8000/api/trades
```

---

### STEP 2: Frontend Deployment (Local - E:\Renko)

#### 2.1 Build Frontend
```bash
cd E:\Renko\frontend
npm run build
```

**Expected output:**
```
✓ 1234 modules transformed
dist/index.html                 45.2 kB
dist/assets/index-xxx.js      234.5 kB
✓ built in 12.34s
```

#### 2.2 Deploy Build Output
- If using local server: Copy `dist/` folder contents to web server
- If using Vercel/Netlify: Push to GitHub, auto-deploys
- If using direct hosting: Copy files to production directory

#### 2.3 Verify Frontend
1. Clear browser cache: `Ctrl+Shift+Delete`
2. Open application in new tab
3. Should see no console errors (F12 → Console)

---

## ✅ TESTING (Do All 3 Tests)

### TEST 1: Crosshair Visibility ✅

**What to do:**
1. Open the app in browser
2. Select an account
3. Go to Renko Chart section
4. Select a symbol and timeframe
5. **Move your mouse over the chart area**

**Expected result:**
- Red vertical dashed line follows mouse
- Green horizontal dashed line follows mouse
- Yellow point at intersection
- Blue price label appears on right side
- Cursor changes to crosshair

**If failing:**
- Clear browser cache (Ctrl+Shift+Delete)
- Check F12 Console for errors
- Rebuild frontend: `npm run build`

---

### TEST 2: Watchlist Delete ✅

**What to do:**
1. Select an account
2. Go to Watchlist section
3. Click red "Delete" button on any symbol
4. Click "Yes" in confirmation dialog

**Expected result:**
- Item disappears immediately
- No error message appears
- Watchlist updates

**If failing:**
- Open F12 Console
- Click Delete button again
- Look for error messages in console
- Check network tab (F12 → Network)
- Delete URL should be: `/api/watchlist/{symbol}?account_id={id}`

---

### TEST 3: Trade History & Export ✅

**What to do:**
1. Select an account
2. Scroll to bottom right → "📊 Trade History" section
3. Should show today's date in date picker
4. Click "Load Trades" button

**Expected result:**
- Table appears with trades for that date
- Shows columns: Symbol, Type, Lot, Entry Price, SL, TP, Status, Time
- Shows trade count at bottom

**If no trades appear:**
- Try a different date (use a date with known trades)
- Check browser console for API errors

**Test Export:**
1. With trades loaded, click "📥 Export CSV"
2. File should download to Downloads folder
3. Filename should be: `trades_2026-04-13_101510620.csv`

**If export fails:**
- Check F12 Network tab for response
- Ensure trades are loaded first
- Check backend logs on VPS

---

## 🔍 VERIFICATION CHECKLIST

After deployment, verify:

- [ ] Backend started without errors on VPS
- [ ] Frontend builds successfully
- [ ] No 404 errors in browser console
- [ ] Crosshair appears on chart when hovering
- [ ] Watchlist delete removes items immediately
- [ ] Trade History loads trades for selected date
- [ ] CSV export downloads successfully
- [ ] CSV file opens in Excel/spreadsheet app

---

## 🐛 TROUBLESHOOTING

### Issue: Crosshair Still Not Visible
**Solution:**
1. Hard refresh: `Ctrl+F5`
2. Clear cache: Settings → Clear browsing data
3. Rebuild: `cd frontend && npm run build`
4. Check F12 Console for errors

### Issue: Watchlist Delete Still Fails
**Solution:**
1. Open F12 Console
2. Click Delete button
3. Look for error message
4. If 404: Check backend is running
5. If 500: Check VPS logs for backend errors

### Issue: Trade History Component Not Showing
**Solution:**
1. Verify import in `App.tsx`: Should have `import TradeHistory from './components/TradeHistory'`
2. Check if account is selected (component only shows when account is selected)
3. Rebuild frontend: `npm run build`

### Issue: Trade History Shows "Failed to fetch trades"
**Solution:**
1. Check VPS backend is running
2. Test endpoint directly: `curl http://vps-ip:8000/api/trades/by-date/101510620?date_str=2026-04-13`
3. Ensure date format is YYYY-MM-DD
4. Check backend logs for errors

### Issue: CSV Export Downloads But Is Empty/Corrupted
**Solution:**
1. Ensure trades exist for selected date
2. Check that `closed` parameter is not set (or set correctly)
3. Try different date
4. Test endpoint directly with curl

---

## 📞 QUICK SUPPORT

### Get Backend Status
```bash
# On VPS, check if service running
tasklist | find "python.exe"
```

### View Backend Logs
```bash
# If running in console, logs appear in terminal
# If running as service, check Windows Event Viewer
```

### Test API Directly
```bash
# Test if backend is responding
curl http://vps-ip:8000/api/trades?account_id=101510620

# Test new endpoint
curl "http://vps-ip:8000/api/trades/by-date/101510620?date_str=2026-04-13"

# Test export
curl "http://vps-ip:8000/api/trades/export/101510620?date_str=2026-04-13" > trades.csv
```

### Check Frontend Build
```bash
cd E:\Renko\frontend
npm run build
# Should see "✓ built in X.XXs" at end
```

---

## 📊 WHAT TO EXPECT

### Trade History Component
- Appears in bottom right panel
- Only visible when account is selected
- Date defaults to today
- Shows up to 50 trades per day (typical)
- CSV exports with headers

### Crosshair on Chart
- Red vertical line
- Green horizontal line
- Yellow center point (3px)
- Blue price label
- Responsive to mouse movement

### Watchlist Delete
- Immediate removal from UI
- Confirmation dialog
- Error alerts if fails
- Console logs for debugging

---

## ⏰ ESTIMATED TIME

- Backend deployment: 5-10 minutes
- Frontend build: 2-3 minutes
- Testing: 5-10 minutes
- **Total: 15-25 minutes**

---

## 📝 NOTES

1. All changes are **backward compatible**
2. No database schema changes required
3. Existing functionality not affected
4. Can rollback by restoring backup file

---

## ✨ SUCCESS INDICATORS

When everything works:
1. ✅ Crosshair visible and smooth on chart
2. ✅ Watchlist items delete immediately
3. ✅ Trade History shows current day trades
4. ✅ CSV export downloads and opens in Excel
5. ✅ No errors in browser console (F12)
6. ✅ Backend logs show no errors

---

## 🎉 COMPLETION

After all tests pass:
- ✅ All three issues are fixed
- ✅ New features are working
- ✅ Ready for production use
- ✅ Users can view and export trades

**Great job! Your trading app is now fully updated!**
