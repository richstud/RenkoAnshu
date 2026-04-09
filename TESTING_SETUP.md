# 🚀 Complete Testing Setup Guide

## ✅ Prerequisites Checklist

Before starting, ensure you have:
- [ ] Python 3.11+ installed (`python --version`)
- [ ] Node.js 18+ installed (`node --version`)
- [ ] Git installed (optional but recommended)
- [ ] MetaTrader 5 installed on your machine
- [ ] Supabase account with project created
- [ ] Your MT5 trading account credentials

---

## **PART 1: BACKEND SETUP**

### Step 1: Create Python Virtual Environment

```bash
# Navigate to project root
cd e:\Renko

# Create virtual environment
python -m venv .venv

# Activate it
.venv\Scripts\activate
```

### Step 2: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

Your `.env` file is already configured with:
- ✅ Supabase credentials (already set)
- ✅ MT5 path and account details (already set)
- ⚠️ Review and verify the following:

```
# Verify these are correct in .env:
SUPABASE_URL=https://mflakcwgbpghyzdyevsb.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1mbGFrY3dnYnBnaHl6ZHlldnNiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU1Nzc3OTQsImV4cCI6MjA5MTE1Mzc5NH0.2Ev5gdEz-9rSgDkKTC_siX_SH5iEfFK6SPM8S8uRx9Q
MT5_PATH=C:\Program Files\XM Global MT5\terminal64.exe
MT5_LOGIN=101510620
MT5_PASSWORD=RichAnshu@1987
MT5_SERVER=XMGlobal-MT5 5
```

### Step 4: Verify Supabase Connection

```bash
# While .venv is activated, run:
python -c "
from backend.supabase.client import supabase_client
print('Supabase connected successfully!' if supabase_client else 'Connection failed')
"
```

### Step 5: Initialize Supabase Schema

Option A: **Via Supabase Dashboard** (Recommended for first time)
1. Log in to [Supabase](https://supabase.com)
2. Go to SQL Editor
3. Click "New Query"
4. Copy-paste the content of `backend/supabase/schema.sql`
5. Click "Run"

Option B: **Via Python Script** (if you have psql installed)
```bash
python setup_supabase.py
```

### Step 6: Start Backend Server

```bash
# Make sure .venv is activated and you're in project root
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

**Test Endpoints:**
```bash
# In another terminal/Postman:
curl http://localhost:8000/health
# Should return: {"status":"ok","active":false}

curl http://localhost:8000/api/accounts
# Should return: {"count":0,"data":[]} (or your accounts)

curl http://localhost:8000/api/tickers
# Should return available symbols
```

---

## **PART 2: FRONTEND SETUP**

### Step 1: Navigate to Frontend

```bash
cd frontend
```

### Step 2: Install Dependencies

```bash
npm install
```

### Step 3: Configure API URL

Verify `frontend/.env` contains:
```
VITE_API_URL=http://localhost:8000
```

### Step 4: Start Development Server

```bash
npm run dev
```

**Expected Output:**
```
  ➜  Local:   http://localhost:5173/
```

### Step 5: Open in Browser

Navigate to: `http://localhost:5173`

You should see:
- **Renko Reversal Gold Bot Dashboard**
- Accounts Panel on the left
- Trading controls
- Live positions and logs viewer

---

## **PART 3: TESTING THE COMPLETE FLOW**

### Test 1: Verify Dashboard Loads

1. Open Frontend: `http://localhost:5173`
2. Check if it connects to backend (no errors in console)
3. Should display accounts (even if empty initially)

### Test 2: Add a Trading Account

**Via API** (Postman or curl):
```bash
curl -X POST http://localhost:8000/api/accounts \
  -H "Content-Type: application/json" \
  -d '{
    "login": 101510620,
    "password": "RichAnshu@1987",
    "server": "XMGlobal-MT5 5"
  }'
```

**Expected Response:**
```json
{
  "message": "Account added"
}
```

### Test 3: Get Accounts

```bash
curl http://localhost:8000/api/accounts
```

**Expected Response:**
```json
{
  "count": 1,
  "data": [
    {
      "login": 101510620,
      "server": "XMGlobal-MT5 5",
      "status": "added"
    }
  ]
}
```

### Test 4: Add Symbol to Watchlist

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
```

### Test 5: Get Signal for Symbol

```bash
curl http://localhost:8000/signal/XAUUSD/2050.45
```

**Expected Response:**
```json
{
  "symbol": "XAUUSD",
  "price": 2050.45,
  "signal": null,
  "brick_info": null
}
```

### Test 6: Start Bot

**Via API:**
```bash
curl -X POST http://localhost:8000/start-bot
```

**In Dashboard:**
Click the **"Start Bot"** button

### Test 7: Check Bot Status

```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "ok",
  "active": true  // After bot starts
}
```

---

## **PART 4: TROUBLESHOOTING**

### Issue: "ModuleNotFoundError: No module named 'backend'"

**Solution:**
```bash
# Make sure you're in the project root directory
cd e:\Renko
# Activate virtual environment
.venv\Scripts\activate
```

### Issue: "ConnectionError: Supabase connection failed"

**Solution:**
```bash
# Check .env file has correct credentials
# Test with:
python -c "from backend.config import settings; print(f'URL: {settings.SUPABASE_URL}')"
```

### Issue: "MT5 initialize failed"

**Solution:**
1. Ensure MT5 is installed at the path specified in `.env`
2. Replace `C:\Program Files\XM Global MT5\terminal64.exe` with your actual MT5 installation path
3. Verify MT5 can be launched manually

### Issue: "Port 8000 already in use"

**Solution:**
```bash
# Kill the process using port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or use a different port
uvicorn backend.main:app --port 8001
```

### Issue: Frontend shows blank or "Cannot reach API"

**Solution:**
```bash
# Check if backend is running
curl http://localhost:8000/health

# In browser console (F12), check for CORS or network errors
# If CORS error, backend needs to allow your frontend domain
```

---

## **PART 5: CREDENTIALS & SECURITY**

⚠️ **IMPORTANT**: Your `.env` file contains sensitive credentials:

```
MT5_PASSWORD=RichAnshu@1987
SUPABASE_KEY=<your-key>
```

### Security Best Practices:

1. **Never commit `.env` to git**
2. **On VPS, use environment variables instead of .env file:**
   ```bash
   export SUPABASE_URL="your-url"
   export MT5_PASSWORD="your-password"
   # Run with: uvicorn backend.main:app
   ```

3. **Rotate credentials regularly**
4. **Use strong MT5 passwords**
5. **On production, enable Supabase RLS (Row Level Security)**

---

## **VERIFICATION CHECKLIST**

- [ ] Python virtual environment created and activated
- [ ] All Python packages installed (`pip list` includes fastapi, supabase, etc.)
- [ ] Backend starts without errors on `http://localhost:8000`
- [ ] `/health` endpoint returns `{"status":"ok"}`
- [ ] Frontend installs dependencies successfully
- [ ] Frontend starts on `http://localhost:5173`
- [ ] Frontend can reach backend (no connection errors)
- [ ] Can add account via API
- [ ] Supabase tables exist and are accessible
- [ ] MT5 path is correct in `.env`

---

## **READY TO TEST! 🚀**

1. **Start Backend:**
   ```bash
   .venv\Scripts\activate
   uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Start Frontend** (in another terminal):
   ```bash
   cd frontend
   npm run dev
   ```

3. **Open Dashboard:**
   Navigate to `http://localhost:5173`

4. **Test Trading:**
   - Add your MT5 account
   - Add XAUUSD to watchlist
   - Start the bot
   - Monitor the dashboard

---

## **NEXT STEPS FOR PRODUCTION**

For deploying to VPS:
- See [VPS_DEPLOYMENT_GUIDE.md](./VPS_DEPLOYMENT_GUIDE.md)

For detailed architecture:
- See [ARCHITECTURE.md](./ARCHITECTURE.md)

For API documentation:
- See [DELIVERABLES.md](./DELIVERABLES.md)
