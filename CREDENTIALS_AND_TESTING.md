# 📋 Credentials & Testing Checklist

## Current Configuration Status

✅ **Already Configured:**
- Supabase Project URL: `https://mflakcwgbpghyzdyevsb.supabase.co`
- Supabase API Key: Configured (valid)
- MT5 Account: `101510620`
- MT5 Server: `XMGlobal-MT5 5`
- MT5 Path: `C:\Program Files\XM Global MT5\terminal64.exe`

---

## ⚠️ Before Testing - Verify Your Credentials

### 1. Verify MT5 Terminal

```bash
# Check if MT5 is installed at the configured path
# Windows: Check if file exists at:
C:\Program Files\XM Global MT5\terminal64.exe

# If not found, update MT5_PATH in .env with correct path
```

**To find your MT5 path:**
1. Open File Explorer
2. Search for "terminal64.exe" or "MetaTrader 5"
3. Right-click > Properties > Copy full path
4. Update `MT5_PATH` in `.env`

### 2. Verify MT5 Login Credentials

**Your current credentials in `.env`:**
```
MT5_LOGIN=101510620
MT5_PASSWORD=RichAnshu@1987
MT5_SERVER=XMGlobal-MT5 5
```

**Test in MetaTrader 5:**
1. Launch MetaTrader 5
2. File > Login
3. Enter your login: `101510620`
4. Enter your password: `RichAnshu@1987`
5. Select server: `XMGlobal-MT5 5`
6. Click OK

If login fails, your credentials are incorrect. Update `.env` file.

### 3. Verify Supabase Connection

**Credentials are in `.env`:**
```
SUPABASE_URL=https://mflakcwgbpghyzdyevsb.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**To verify:**
1. Open [Supabase Dashboard](https://supabase.com)
2. Log in with your account
3. Find project: `mflakcwgbpghyzdyevsb`
4. Go to Settings > API
5. Verify URL and Key match `.env`

---

## 📋 Pre-Testing Checklist

| Item | Status | Notes |
|------|--------|-------|
| Python 3.11+ installed | ☐ | `python --version` |
| Node.js 18+ installed | ☐ | `node --version` |
| .env file configured | ☐ | MT5 and Supabase credentials |
| MT5 terminal installed | ☐ | Check path matches `.env` |
| MT5 login credentials work | ☐ | Test in MT5 manually |
| Supabase project accessible | ☐ | Login to dashboard |
| Virtual environment created | ☐ | `.venv\Scripts\activate` |
| Dependencies installed | ☐ | `pip install -r requirements.txt` |
| Supabase schema created | ☐ | Run SQL in Supabase dashboard |
| Frontend package.json ready | ☐ | Check `frontend/` folder |
| Node packages installed | ☐ | `cd frontend && npm install` |

---

## 🧪 Testing Sequence

### Test 1: Python Setup ✅

```bash
# Navigate to project
cd e:\Renko

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python verify_setup.py
```

**Expected:** All checks pass ✅

---

### Test 2: Backend Startup ✅

```bash
# Make sure venv is activated
.venv\Scripts\activate

# Start backend
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

**Test Health Endpoint:**
```bash
# In another terminal
curl http://localhost:8000/health

# Expected response:
{"status":"ok","active":false}
```

---

### Test 3: Frontend Setup ✅

```bash
# In a new terminal, navigate to frontend
cd e:\Renko\frontend

# Install npm packages
npm install

# Start development server
npm run dev
```

**Expected Output:**
```
  ➜  Local:   http://localhost:5173/
  ➜  press h to show help
```

**Open in Browser:**
- Navigate to `http://localhost:5173`
- Should see **"🟡 Renko Reversal Gold Bot"** dashboard

---

### Test 4: API Connection ✅

**In dashboard:**
1. Check if any error messages appear
2. Open browser DevTools (F12)
3. Go to Network tab
4. Refresh the page
5. Look for API calls to `/api/accounts`, `/api/trades`
6. Should see successful responses

**Alternative - Direct API call:**
```bash
curl http://localhost:8000/api/accounts

# Expected response:
{"count":0,"data":[]}
```

---

### Test 5: Database Integration ✅

**Create a test account:**
```bash
curl -X POST http://localhost:8000/api/accounts \
  -H "Content-Type: application/json" \
  -d '{
    "login": 101510620,
    "password": "RichAnshu@1987",
    "server": "XMGlobal-MT5 5"
  }'

# Expected response:
{"message":"Account added"}
```

**Verify in Supabase:**
1. Supabase Dashboard > SQL Editor
2. Run: `SELECT * FROM accounts;`
3. Should see your account entry

---

### Test 6: Watchlist Management ✅

**Add symbol to watchlist:**
```bash
curl -X POST http://localhost:8000/api/watchlist \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": 101510620,
    "symbol": "XAUUSD",
    "lot_size": 0.01,
    "stop_loss_pips": 50,
    "take_profit_pips": 100,
    "brick_size": 1.0,
    "algo_enabled": true
  }'

# Expected response includes message and data with the created watchlist item
```

**Get watchlist:**
```bash
curl "http://localhost:8000/api/watchlist?account_id=101510620"
```

---

### Test 7: Signal Generation ✅

**Get trading signal:**
```bash
curl http://localhost:8000/signal/XAUUSD/2050.45

# Expected response:
{
  "symbol": "XAUUSD",
  "price": 2050.45,
  "signal": null,
  "brick_info": null
}
```

---

### Test 8: Bot Control ✅

**Start bot:**
```bash
curl -X POST http://localhost:8000/start-bot

# Expected response:
{"message":"Bot started"}
```

**Check status:**
```bash
curl http://localhost:8000/health

# Expected response after starting:
{"status":"ok","active":true}
```

**Stop bot:**
```bash
curl -X POST http://localhost:8000/stop-bot
```

---

## 🐛 Common Issues & Solutions

### Issue 1: Module Import Error

```
ModuleNotFoundError: No module named 'backend'
```

**Solution:**
```bash
# Make sure you're in project root
cd e:\Renko

# Activate venv
.venv\Scripts\activate

# Then run
uvicorn backend.main:app --reload
```

---

### Issue 2: Supabase Connection Failed

```
Error: Connection refused or timeout
```

**Solution:**
1. Check internet connection
2. Verify `SUPABASE_URL` in `.env`
3. Verify `SUPABASE_KEY` in `.env`
4. Check firewall isn't blocking supabase.co

```bash
# Test connection
python -c "from backend.supabase.client import supabase_client; print('Connected!')"
```

---

### Issue 3: Port Already in Use

```
Address already in use: ('0.0.0.0', 8000)
```

**Solution:**
```bash
# Use different port
uvicorn backend.main:app --port 8001

# Or kill process on 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

---

### Issue 4: MT5 Connection Failed

```
MT5 initialize failed
```

**Solution:**
1. Verify MT5 is installed
2. Check `MT5_PATH` in `.env`
3. Try with just directory path instead of executable:
   ```
   MT5_PATH=C:\Program Files\XM Global MT5
   ```

---

### Issue 5: Frontend Can't Reach Backend

**Browser Console Error:**
```
Failed to fetch http://localhost:8000/api/accounts
```

**Solution:**
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check `VITE_API_URL` in `frontend/.env`
3. Clear browser cache (Ctrl+Shift+Del)
4. Hard refresh page (Ctrl+F5)

---

## 📊 Expected Test Results

### Successful Backend Start
```
✓ Application startup complete
✓ Connected to Supabase
✓ Health endpoint returns {"status":"ok"}
✓ /api/accounts endpoint accessible
✓ /api/tickers endpoint returns symbols
```

### Successful Frontend Start
```
✓ React app compiles without errors
✓ Dashboard loads at localhost:5173
✓ No console errors (F12 to check)
✓ API calls show in Network tab
✓ Data displays in dashboard
```

### Successful Integration
```
✓ Can add MT5 account via API
✓ Account appears in Supabase
✓ Can add symbol to watchlist
✓ Can start/stop bot
✓ Dashboard reflects changes
```

---

## ✅ Final Verification

Run this to confirm everything is set up:

```bash
# In project root with venv activated
python verify_setup.py

# Should show:
# ✅ Python Version Check
# ✅ Environment Configuration Check
# ✅ Python Dependency Check
# ✅ Project Structure Check
# ✅ Frontend Configuration Check
# ✅ Supabase Connection Check
# ✅ All checks passed! You're ready to test:
```

---

## 🚀 You're Ready!

Once all tests pass, you can:

1. **Start Backend:**
   ```bash
   .venv\Scripts\activate
   uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Start Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Open Dashboard:**
   - Navigate to `http://localhost:5173`
   - Add your MT5 account
   - Add symbols to watchlist
   - Start trading!

---

## 📞 Need Help?

1. Check **TESTING_SETUP.md** for detailed step-by-step guide
2. Check **VPS_DEPLOYMENT_GUIDE.md** for production deployment
3. See **DELIVERABLES.md** for complete API documentation
4. Check browser console (F12) for error messages
5. Check backend terminal for Python error messages

**Your current setup is configured and ready for testing!** ✅
