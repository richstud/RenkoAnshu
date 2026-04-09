# 🔧 Bid/Ask Not Fetching & Trade Placement Issues

## ❌ Problem

You're seeing `---` for bid/ask prices instead of actual values, and trades can't be placed. This means **MT5 is not being recognized or initialized**.

## 🔍 Quick Diagnostic

In your browser, check:
```
http://localhost:8000/diagnose
```

This will show you exactly what's wrong.

---

## ✅ Solution: Setup MT5 Connection

### Step 1: Ensure MT5 is Running & Logged In

**CRITICAL:** MetaTrader 5 **MUST** be running and logged in before the backend can fetch prices!

1. **Launch MetaTrader 5** on your computer
2. **File > Login** with your credentials:
   - Login: `101510620`
   - Password: `RichAnshu@1987`
   - Server: `XMGlobal-MT5 5`
3. **Wait for MT5 to fully sync** (you'll see market prices in Market Watch)
4. **Keep MT5 running** in the background

### Step 2: Restart Backend

The backend needs MT5 running to initialize. Kill and restart:

**Kill current backend:**
```powershell
# Press Ctrl+C in the terminal running the backend
```

**Restart backend:**
```powershell
cd e:\Renko
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

**You should see in the terminal:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Added default account 101510620 from environment
INFO:     Attempting to connect 1 account(s)
INFO:     Connected account 101510620
```

### Step 3: Verify MT5 Connection

**Check health endpoint:**
```powershell
curl http://localhost:8000/health
```

**Expected response:**
```json
{
  "status": "ok",
  "active": false,
  "mt5_connected": true,
  "total_accounts": 1,
  "connected_accounts": [101510620]
}
```

**If `mt5_connected` is still `false`:**
```powershell
curl http://localhost:8000/diagnose
```

This will tell you exactly what's wrong.

---

## 🎯 Common Issues & Solutions

### Issue 1: "MT5 Terminal is not running"

**Error in `/diagnose`:**
```
"MT5 Terminal is not running. Launch MetaTrader 5..."
```

**Solution:**
1. Open MetaTrader 5 application
2. Log in with your account
3. Wait for prices to load (you'll see symbols in Market Watch)
4. Don't close MT5 while using the bot
5. Restart backend

---

### Issue 2: "No MT5 accounts connected"

**Error in `/diagnose`:**
```
"No MT5 accounts connected. Check your credentials..."
```

**Solutions:**

**A) Verify MT5 path in .env:**
```
MT5_PATH=C:\Program Files\XM Global MT5\terminal64.exe
```

Check if this path exists on your computer:
```powershell
Test-Path "C:\Program Files\XM Global MT5\terminal64.exe"
```

If it returns `False`, find your MT5 location:
```powershell
Get-ChildItem -Path "C:\Program Files" -Recurse -Filter "terminal64.exe" 2>$null
```

Update `.env` with the correct path.

**B) Verify credentials in .env:**
```
MT5_LOGIN=101510620
MT5_PASSWORD=RichAnshu@1987
MT5_SERVER=XMGlobal-MT5 5
```

Test manually in MT5:
- File > Login
- Enter these credentials
- If it fails, credentials are wrong - update .env

**C) Restart after changes:**
```powershell
# Stop backend (Ctrl+C)
# Restart:
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

---

### Issue 3: Symbols Still Showing "---"

Even after MT5 connects, if prices show `---`:

**A) Add symbols to MT5 Market Watch:**
1. Open MT5
2. View > Market Watch (or Ctrl+M)
3. Right-click > Show All
4. Select symbols (XAUUSD, EURUSD, etc.)
5. Click OK

**B) Restart backend again:**
```powershell
# Ctrl+C to stop
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

**C) Test single symbol:**
```powershell
curl http://localhost:8000/api/tickers/XAUUSD/quote
```

Should return actual bid/ask values.

---

### Issue 4: Trade Placement Fails

**After MT5 connects and prices load**, trades still fail?

**Check backend logs for errors:**
1. Look in terminal where backend is running
2. You'll see error messages like:
   ```
   ERROR: MT5 order_send failed: insufficient funds
   ERROR: Symbol not visible
   ```

**Common trade failures:**

| Error | Solution |
|-------|----------|
| **"Symbol not visible"** | Add to MT5 Market Watch (see Issue 3) |
| **"Insufficient funds"** | Your account balance is too low |
| **"Invalid lot size"** | Lot is too small/large for that symbol |
| **"Connection lost"** | MT5 terminal crashed, restart it |

---

## 📋 Complete Checklist

- [ ] MetaTrader 5 installed at `C:\Program Files\XM Global MT5\terminal64.exe`
- [ ] MT5 is running and shows prices in Market Watch
- [ ] MT5 login works (test: File > Login)
- [ ] `.env` file has correct MT5 credentials
- [ ] Backend started AFTER MT5 is running
- [ ] `http://localhost:8000/health` shows `mt5_connected: true`
- [ ] `http://localhost:8000/api/tickers/XAUUSD/quote` returns bid/ask values
- [ ] Frontend shows prices in "Available Tickers"
- [ ] Can click "Add" button on symbols
- [ ] Symbols appear in "Watchlist"
- [ ] Can click "Start Bot"
- [ ] Trades appear in "Live Trades" after bot starts

---

## 🚀 Expected Flow After Fixes

1. ✅ Start MT5 → Log in → Wait for prices
2. ✅ Restart backend → See "Connected account" in logs
3. ✅ Refresh frontend → Prices load in "Available Tickers"
4. ✅ Add symbols to watchlist
5. ✅ Click "Start Bot"
6. ✅ Watch trades execute in real-time

---

## 🆘 Still Not Working?

**Run full diagnostic:**
```powershell
curl http://localhost:8000/diagnose | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

**Check backend startup logs:**
- Look in the terminal where backend is running
- Copy any error messages
- Common errors will tell you exactly what's wrong

**Minimal test:**
```powershell
# Test if MT5 can be imported
python -c "import MetaTrader5; print('MT5 OK')"

# Test if backend can initialize MT5
python -c "from backend.main import app; print('Backend OK')"
```

---

## 📊 What Happens Behind The Scenes

When you refresh the dashboard:

```
Browser → /api/tickers → Backend
    ↓
Backend calls: price_manager.get_quote(symbol)
    ↓
price_manager does: mt5.symbol_info_tick(symbol)
    ↓
MT5 returns: bid/ask prices → Backend returns JSON → Browser displays
```

**If MT5 is not initialized:**
```
mt5.symbol_info_tick() returns None → Backend returns null → Browser shows "---"
```

---

## ✅ Next Steps

1. **Restart MT5** if not running
2. **Restart Backend** (should see "Connected account")
3. **Test health endpoint** (should show `mt5_connected: true`)
4. **Refresh frontend** (should show prices)
5. **Add XAUUSD to watchlist**
6. **Click Start Bot**
7. **Monitor trades in real-time**

Let me know if you're still seeing `---` after these steps!
