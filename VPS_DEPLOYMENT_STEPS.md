# VPS Deployment Steps - Backend Performance Optimization

## ✅ Changes Pushed to GitHub

**Commit:** `d15d333 - Backend Performance Optimization - Non-Blocking Renko Chart`

**Files Updated:**
- `backend/api/renko_chart.py` - Non-blocking calculations + caching + bid/ask
- `frontend/src/components/RenkoChart.tsx` - Bid/ask display + calculating indicator

**Documentation Added:**
- `BACKEND_PERFORMANCE_FIX.md`
- `SOLUTION_SUMMARY.md`
- `DEPLOYMENT_COMPLETE.md`
- `QUICK_START.txt`

---

## VPS Deployment Instructions

### Step 1: SSH to Your VPS
```bash
ssh root@your-vps-ip
# or
ssh user@your-vps-ip
```

### Step 2: Navigate to Backend Directory
```bash
cd /path/to/renko  # or wherever your backend is deployed
# Usually something like: cd ~/renko or cd /app/renko
```

### Step 3: Pull Latest Changes
```bash
git pull origin main
```

Expected output:
```
Updating 71596ee..d15d333
Fast-forward
 backend/api/renko_chart.py             | 294 ++++++++++---
 frontend/src/components/RenkoChart.tsx | 735 +++++++++++++++++++++---------
 BACKEND_PERFORMANCE_FIX.md             | 225 +++++++++
 DEPLOYMENT_COMPLETE.md                 | 285 ++++++++++
 QUICK_START.txt                        | 71 +++
 SOLUTION_SUMMARY.md                    | 153 ++++++
 6 files changed, 1903 insertions(+), 258 deletions(-)
```

### Step 4: Verify Changes
```bash
git log --oneline -1
# Should show: Backend Performance Optimization - Non-Blocking Renko Chart
```

### Step 5: Check Backend File
```bash
cat backend/api/renko_chart.py | grep "ThreadPoolExecutor"
# Should output: from concurrent.futures import ThreadPoolExecutor
```

### Step 6: Restart Backend Service

**Option A: Manual Process (if running in terminal)**
```bash
# Stop current process
Ctrl+C

# Start new backend
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

**Option B: Systemd Service**
```bash
sudo systemctl restart renko-backend
# Verify it's running
sudo systemctl status renko-backend
```

**Option C: Docker Container**
```bash
docker-compose pull
docker-compose up -d renko-backend
# Check logs
docker-compose logs -f renko-backend
```

**Option D: PM2 (if using PM2)**
```bash
pm2 restart renko-backend
# or
pm2 reload renko-backend

# Verify
pm2 status
pm2 logs renko-backend
```

### Step 7: Verify Backend is Running
```bash
# Check if port 8000 is listening
netstat -tlnp | grep 8000
# or
ss -tlnp | grep 8000

# Or test the API
curl http://localhost:8000/api/tickers | head -20
```

### Step 8: Check Backend Logs
```bash
# If running in terminal: watch the console output
# If systemd: 
sudo journalctl -u renko-backend -f

# If PM2:
pm2 logs renko-backend -f

# If Docker:
docker-compose logs -f renko-backend
```

### Step 9: Test Chart Endpoint
```bash
# Test the Renko chart endpoint
curl "http://localhost:8000/api/renko/chart/EURUSD?brick_size=0.005&timeframe=1"

# Should return:
# {
#   "symbol": "EURUSD",
#   "brick_size": 0.005,
#   "bricks": [...],
#   "current_price": 1.0234,
#   "bid": 1.0232,      <-- NEW: bid/ask prices
#   "ask": 1.0236,      <-- NEW: bid/ask prices
#   "timestamp": "2026-04-10T17:51:46.801Z"
# }
```

### Step 10: Refresh Frontend
```bash
# If frontend is also on VPS:
cd /path/to/frontend
git pull origin main
# Then rebuild/restart frontend:
npm run build
npm run start
```

Or just tell users to **hard refresh their browser:**
- Windows/Linux: `Ctrl+F5`
- Mac: `Cmd+Shift+R`

---

## Verification Checklist

- [ ] `git pull` completed successfully
- [ ] Files show correct changes (see Step 4-5)
- [ ] Backend process started without errors
- [ ] Port 8000 listening (or your configured port)
- [ ] `/api/tickers` endpoint responds
- [ ] `/api/renko/chart` endpoint returns bid/ask
- [ ] No errors in backend logs
- [ ] Frontend refreshed (Ctrl+F5)

---

## Testing After Deployment

### Test 1: Verify Non-Blocking Performance
```bash
# Open frontend, select XPTUSD
# Brick size: 0.0005
# Observe:
# ✅ Bid/ask shows immediately (< 1 second)
# ✅ "Calculating..." indicator appears
# ✅ Chart loads in 2-3 seconds
# ✅ No backend disconnect
```

### Test 2: Verify Other Requests Work
```bash
# While chart calculating:
# ✅ Can execute trades
# ✅ Can fetch accounts
# ✅ Can get quotes

# Should respond normally (not blocked)
```

### Test 3: Check Backend Logs
```bash
# Should see logs like:
# INFO:backend.api.renko_chart:📊 Fetching 1-min data for XPTUSD from MT5...
# INFO:backend.api.renko_chart:📦 Cache hit for XPTUSD_0.0005_1
# [No freezing, no errors]
```

---

## If Something Goes Wrong

### Backend won't start
```bash
# Check Python syntax
python -m py_compile backend/api/renko_chart.py

# Check imports
python -c "from concurrent.futures import ThreadPoolExecutor; print('OK')"

# Check full error
python -m uvicorn backend.main:app
```

### Chart still slow
```bash
# Verify MT5 connection
curl http://localhost:8000/api/tickers | wc -l
# Should return list of tickers

# Check candle count
grep "candle_count = " backend/api/renko_chart.py
# Should be 100 for 1M, 150 for 5M
```

### Rollback if needed
```bash
# Revert to previous commit
git reset --hard 71596ee

# Restart backend
# Process will work but be slow again
```

---

## What Changed

### Backend Performance
- **Before:** XPTUSD chart freezes backend for 10+ seconds
- **After:** XPTUSD chart loads in 2-3 seconds, other requests work normally

### Key Improvements
1. Thread pool prevents event loop blocking
2. Reduced data (100 vs 500 candles)
3. Smart caching (1-second TTL)
4. Live bid/ask display
5. Calculating indicator UI

### Files Changed
```
backend/api/renko_chart.py             | 294 ++++++++++---
frontend/src/components/RenkoChart.tsx | 735 +++++++++++++++++++++---------
```

---

## Commands Summary

```bash
# Pull changes
git pull origin main

# Verify changes
git log --oneline -1

# Restart backend
sudo systemctl restart renko-backend
# or
pm2 restart renko-backend
# or
docker-compose up -d renko-backend

# Test endpoint
curl "http://localhost:8000/api/renko/chart/EURUSD?brick_size=0.005"

# Check logs
pm2 logs renko-backend -f
# or
docker-compose logs -f renko-backend
```

---

## Support

If you encounter issues:
1. Check backend logs first
2. Verify MT5 connection: `/api/tickers`
3. Test chart endpoint: `/api/renko/chart/EURUSD`
4. Ensure frontend is refreshed (Ctrl+F5)
5. Restart backend if needed

---

**Status:** Ready for VPS deployment
**Version:** Backend Performance Optimization - Non-Blocking Renko Chart
**Date:** 2026-04-10

