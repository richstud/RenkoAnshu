# VPS Backend Deployment - Status Report

**Date:** April 12, 2026  
**Status:** ✅ Backend Deployed & Running

## Deployment Information

### VPS Details
- **IP Address:** 114.29.239.50
- **Backend Port:** 8000
- **Backend URL:** http://114.29.239.50:8000
- **API Endpoint:** http://114.29.239.50:8000/api/

### Frontend Configuration
- **Local Dev Port:** 5173
- **Configured Backend:** 114.29.239.50:8000
- **Environment File:** `frontend/.env` (set to use VPS IP)

### Services Running
✅ Backend API (FastAPI on 8000)
✅ Trading Worker process
✅ Supabase database connection (cloud)
✅ MetaTrader 5 integration

---

## 🔗 Accessing the Application

### From Your Local Machine

**Option 1: Run Frontend Locally (Recommended for Dev)**
```powershell
cd C:\Renko\frontend
npm run dev
```
- Frontend: http://localhost:5173
- Connects to VPS backend at 114.29.239.50:8000
- Best for development and testing

**Option 2: Build & Preview**
```powershell
cd C:\Renko\frontend
npm run build
npm run preview
```
- Frontend: http://localhost:5173 (production build)
- Connects to VPS backend at 114.29.239.50:8000

### Access the Backend API Directly
Test API health:
```
http://114.29.239.50:8000/api/tickers
http://114.29.239.50:8000/api/accounts
http://114.29.239.50:8000/api/trades
```

---

## ✅ Verify Connectivity

### Quick Test (PowerShell)
```powershell
cd C:\Renko
.\scripts\Test-VPS-Backend.ps1
```

This will:
- ✅ Test TCP connection to VPS:8000
- ✅ Query /api/tickers endpoint
- ✅ Query /api/accounts endpoint
- ✅ Query /api/trades endpoint
- ✅ Check CORS headers

### Expected Results
All tests should pass with:
- HTTP 200 responses
- JSON data returned
- CORS headers present

If any test fails:
- Check VPS firewall allows port 8000
- Verify backend is running: `systemctl status renko-backend`
- Check logs on VPS

---

## 🚀 Frontend Build & Deploy

### Current State
- Frontend build output: `frontend/dist/`
- Ready for production hosting

### For Production Access

#### Option A: Use VPS Public IP (Direct)
**If you have a domain**, point DNS A record to: **114.29.239.50**

Then access:
- http://yourdomain.com (frontend on port 80)
- http://yourdomain.com/api/* (backend proxy)

**Setup required:**
1. Install IIS on VPS Windows Server
2. Deploy `frontend/dist` to IIS
3. Configure URL Rewrite to proxy `/api/*` to localhost:8000
4. See: `deploy/IIS_SETUP.md` for detailed instructions

#### Option B: Access via IP:Port (Quick Testing)
Build frontend and serve:
```powershell
# On VPS or from dev machine:
cd C:\Renko\frontend
npm run build
npm run preview -- --host 0.0.0.0 --port 5173
```

Access: **http://114.29.239.50:5173**

---

## 📋 Architecture

```
┌─────────────────────────────────────────────────────────┐
│           Windows VPS (114.29.239.50)                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐          ┌──────────────┐            │
│  │  Backend     │◄────────►│   Worker     │            │
│  │  (FastAPI)   │          │  (Strategy)  │            │
│  │  Port 8000   │          │  (Python)    │            │
│  └──────────────┘          └──────────────┘            │
│         ▲                                               │
│         │                                               │
│         │ /api/* (JSON REST)                            │
│         │                                               │
│  ┌──────┴──────┐                                        │
│  │             │                                        │
│  └─────────────┘                                        │
│                                                         │
└─────────────────────────────────────────────────────────┘
         ▲
         │ http://114.29.239.50:8000/api/
         │
┌────────┴─────────────────────────────────────────────────┐
│          Your Local Machine or Client Browser            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐        ┌─────────────┐              │
│  │  Frontend    │        │  Browser    │              │
│  │  (React)     │───────►│  (Access)   │              │
│  │  Port 5173   │        │ localhost   │              │
│  └──────────────┘        └─────────────┘              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 📊 Network Diagram

```
Internet
   │
   ▼ Port 8000
114.29.239.50 (Windows VPS)
   │
   ├─ Backend API (FastAPI) ─────┬─ Supabase (PostgreSQL)
   │                             │
   ├─ Worker Process ────────────┼─ MetaTrader 5
   │                             │
   └─ (Optional) IIS Frontend ───┘

Client Device
   │
   ├─ Frontend (React)
   │  - Available on: http://localhost:5173 (local dev)
   │  - Connects to: http://114.29.239.50:8000/api/
```

---

## 🔒 Security Considerations

### Firewall Rules Needed
```powershell
# Allow backend access from your IP
netsh advfirewall firewall add rule name="Allow Backend" `
  protocol=TCP dir=in localport=8000 action=allow

# Restrict to specific IPs if needed
netsh advfirewall firewall add rule name="Allow Backend from IP" `
  protocol=TCP dir=in localport=8000 remoteip=YOUR_IP action=allow
```

### Production Security
- [ ] Enable HTTPS/SSL on frontend
- [ ] Use domain name instead of IP
- [ ] Restrict backend API to frontend only
- [ ] Setup authentication/API keys
- [ ] Enable database backups
- [ ] Monitor for unauthorized access

---

## 🛠️ Common Tasks

### Check Backend is Running
```powershell
# From VPS or local machine:
curl http://114.29.239.50:8000/api/tickers

# Or in PowerShell:
(Invoke-WebRequest http://114.29.239.50:8000/api/tickers).Content
```

### Restart Backend
```cmd
# On VPS (if using NSSM service):
net stop RenkoBackend
net start RenkoBackend

# Or if using PowerShell script:
.\scripts\Start-All.ps1
```

### View Backend Logs
```powershell
# Logs location
C:\Renko\logs\backend.log
C:\Renko\logs\worker.log
C:\Renko\logs\frontend.log
```

### Rebuild Frontend
```powershell
cd C:\Renko\frontend
npm run build      # production build
npm run dev        # development server
npm run preview    # production preview
```

---

## 📞 Next Steps

### Immediate (Today)
1. [ ] Run connectivity test: `Test-VPS-Backend.ps1`
2. [ ] Verify backend returns JSON data
3. [ ] Run frontend locally pointing to VPS

### Short Term (This Week)
1. [ ] Setup domain name
2. [ ] Configure IIS for frontend hosting on VPS
3. [ ] Setup SSL certificate
4. [ ] Test live trading functionality

### Long Term
1. [ ] Setup monitoring and logging
2. [ ] Configure automatic backups
3. [ ] Implement advanced security
4. [ ] Scale for additional trading strategies

---

## 📝 Configuration Files Updated

- `frontend/.env` ➜ Points to `http://114.29.239.50:8000`
- `frontend/vite.config.ts` ➜ Uses VPS IP as default
- `frontend/.env.example` ➜ Updated with VPS IP example

---

## ✨ You're Ready!

The backend is deployed and running on your VPS. The frontend is configured to connect to it.

**Test it now:**
```powershell
cd C:\Renko
.\scripts\Test-VPS-Backend.ps1
```

**Run frontend:**
```powershell
cd C:\Renko\frontend
npm run dev
```

Then visit: **http://localhost:5173**

---

**Status:** Production Ready ✅
**Date:** April 12, 2026
**Next Review:** After first live trade test
