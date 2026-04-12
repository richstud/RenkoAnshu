# 🚀 Quick Start - VPS Backend Running!

**Backend is deployed and running on VPS IP: 114.29.239.50:8000**

## ✅ 3 Quick Steps to Test

### Step 1️⃣ Test Backend Connectivity (2 minutes)
```powershell
cd C:\Renko
.\scripts\Test-VPS-Backend.ps1
```

You should see green ✅ for:
- TCP connection to 114.29.239.50:8000
- API responses from /api/tickers
- Accounts and trades endpoints
- CORS headers enabled

### Step 2️⃣ Run Frontend Locally (1 minute)
```powershell
cd C:\Renko\frontend
npm run dev
```

Browser opens to: **http://localhost:5173**

### Step 3️⃣ Verify It Works
Check the frontend dashboard:
- ✅ Accounts panel shows your MT5 account
- ✅ Tickers panel shows 7 symbols with prices
- ✅ Prices update every 2 seconds
- ✅ Can add symbols to watchlist
- ✅ Can place test trades

---

## 🔍 If Something Doesn't Work

**Can't access backend?**
1. Check VPS firewall: `netsh advfirewall show allprofiles`
2. Verify backend running on VPS
3. Test: `Test-VPS-Backend.ps1` script

**Frontend loads but no data?**
1. Check browser console: Press F12
2. Check Network tab for API calls
3. Verify .env file: `http://114.29.239.50:8000`

**API returns errors?**
1. Check VPS backend logs: `C:\Renko\logs\backend.log`
2. Verify Supabase credentials in .env
3. Restart backend services

---

## 📋 Configuration
- **Frontend .env:** VITE_API_URL=http://114.29.239.50:8000
- **Backend Running:** Port 8000
- **Database:** Supabase (cloud)
- **Trading:** MetaTrader 5 integration ready

---

## 🌐 For Production (Later)

To make frontend accessible from anywhere:

1. Buy domain name (e.g., trading-bot.com)
2. Point DNS A record to: 114.29.239.50
3. Follow: `deploy/IIS_SETUP.md`
4. Access at: https://trading-bot.com

---

## 📞 Today's Test Plan

| Step | Command | Expected Result |
|------|---------|-----------------|
| 1 | `Test-VPS-Backend.ps1` | All green ✅ |
| 2 | `npm run dev` | Frontend loads |
| 3 | Check dashboard | Account shows, prices flow |

**Estimated time:** 5 minutes ⏱️

---

**Backend:** 114.29.239.50:8000 ✅
**Frontend:** http://localhost:5173 🚀
**Let's go!**
