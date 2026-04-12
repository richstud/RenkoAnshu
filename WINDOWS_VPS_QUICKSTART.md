# Renko Trading Bot - Windows VPS Deployment Summary

## 🎯 Quick Start for Windows VPS

**Fastest Auto-Start Solution (Recommended):**
```powershell
# Open PowerShell as Administrator
cd C:\Renko
.\scripts\Start-All.ps1
```

This single command will:
✅ Start Backend API on port 8000
✅ Start Trading Worker
✅ Build and start Frontend on port 5173
✅ Open browser automatically

---

## 📦 What's Included

### Deployment Scripts
- `scripts/Start-All.ps1` ⭐ **[RECOMMENDED]**
  - One-command startup for all services
  - Pretty console logging with timestamps
  - Auto-opens browser
  - Best for quick testing/setup

- `scripts/Install-WindowsServices.bat`
  - Uses NSSM to create Windows services
  - Services auto-restart on crash
  - Services auto-start on reboot
  - Best for production/hands-off operation

- `scripts/Setup-TaskScheduler.bat`
  - Schedule tasks for auto-start
  - Lightweight alternative to NSSM
  - Built-in Windows functionality
  - Best for VPS without admin tools

- `scripts/Start-Backend.bat`
  - Standalone backend startup
  - Use if you want to start manually

- `scripts/Start-Worker.bat`
  - Standalone worker startup

- `scripts/Start-Frontend.bat`
  - Standalone frontend startup

### Documentation
- `deploy/WINDOWS_VPS_DEPLOYMENT.md` - Complete deployment guide
- `deploy/IIS_SETUP.md` - IIS hosting with SSL/HTTPS
- `deploy/nginx.conf` - Nginx reverse proxy config (reference)
- `deploy/renko-backend.service` - Systemd service (Linux reference)
- `docker-compose.yml` - Docker containerization (reference)

---

## 🚀 3 Deployment Options

### ✅ Option 1: PowerShell (EASIEST - Start Here)

**When:** You want quick setup or testing
**Time:** 1 minute
**Steps:**

1. Open PowerShell as Administrator
2. Run:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   cd C:\Renko
   .\scripts\Start-All.ps1
   ```

3. Services start, browser opens to http://localhost:5173

4. To stop, press Ctrl+C in each console window

**Pros:**
- Simplest setup
- All services in separate windows (easy to see logs)
- Beautiful colored output
- Auto-opens browser

**Cons:**
- Requires manual restart if crashes
- Terminal windows must stay open

---

### ⚙️ Option 2: Windows Task Scheduler (AUTO-BOOT)

**When:** You want services to auto-start on VPS reboot
**Time:** 2 minutes
**Steps:**

1. Open Command Prompt as Administrator
2. Run:
   ```cmd
   cd C:\Renko\scripts
   Setup-TaskScheduler.bat
   ```

3. Tasks auto-create and will start on reboot

4. View tasks: Start > Administrative Tools > Task Scheduler > Renko folder

**Pros:**
- Services auto-start on reboot
- No terminal windows visible
- Runs in background
- Built-in Windows feature (no additional tools)

**Cons:**
- Limited logging/monitoring
- Harder to debug if issues occur

**To Stop Services:**
Open Task Scheduler and disable tasks under Renko folder

---

### 🏢 Option 3: NSSM Windows Services (PROFESSIONAL)

**When:** Production environment needs monitoring and service management
**Time:** 5 minutes
**Prerequisites:** Download NSSM first

**Steps:**

1. Download NSSM: https://nssm.cc/download
2. Extract to: `C:\nssm`
3. Open Command Prompt as Administrator
4. Run:
   ```cmd
   cd C:\Renko\scripts
   Install-WindowsServices.bat
   ```

5. Services install and auto-start

**Manage Services:**
```cmd
net start RenkoBackend    # Start backend service
net stop RenkoBackend     # Stop backend service
net start RenkoWorker     # Start worker service
net stop RenkoWorker      # Stop worker service
```

**View Services:**
- Press Windows+R, type `services.msc`, find RenkoBackend and RenkoWorker

**Pros:**
- Professional Windows service management
- Auto-restart on crash
- Auto-start on reboot
- Full logging and monitoring
- Service dependencies can be configured
- Event Log integration

**Cons:**
- Requires NSSM download
- Slightly more complex setup

---

## 🌐 Internet Access Options

### Local Network (For Testing)
Frontend accessible at: `http://<YOUR-VPS-IP>:5173`

### For Internet Access (Production)

**Option A: Buy Domain + Use IIS (Windows Native)**
1. Buy domain from registrar (GoDaddy, Namecheap, etc.)
2. Point DNS A record to your VPS IP
3. Follow guide: `deploy/IIS_SETUP.md`
4. IIS handles SSL, routing, and hosting
5. Access at: `https://yourdomain.com`

**Option B: Use Cloud Provider**
- AWS: IIS on EC2 + Route 53 for DNS
- Azure: App Service + Application Gateway
- Google Cloud: Compute Engine + Cloud DNS
- DigitalOcean: App Platform or Droplet

**Option C: Use Reverse Proxy (Nginx)**
- Reference: `deploy/nginx.conf`
- Requires: Linux VPS or WSL on Windows
- Benefits: Can run multiple apps behind single IP

---

## 📊 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   WINDOWS VPS                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐   ┌──────────────┐  ┌────────────┐   │
│  │  Frontend    │   │   Backend    │  │   Worker   │   │
│  │ (React)      │   │  (FastAPI)   │  │ (Strategy) │   │
│  │ Port 5173    │   │  Port 8000   │  │ (Python)   │   │
│  └──────────────┘   └──────────────┘  └────────────┘   │
│         │                   │                  │         │
│         └───────────────────┼──────────────────┘         │
│                             │                            │
│                   ┌─────────▼──────────┐                │
│                   │  Supabase          │                │
│                   │  PostgreSQL        │                │
│                   │  (Cloud Database)  │                │
│                   └────────────────────┘                │
│                             │                            │
│                   ┌─────────▼──────────┐                │
│                   │  MetaTrader 5      │                │
│                   │  (Live Trading)    │                │
│                   └────────────────────┘                │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  Logs: C:\Renko\logs\                                  │
│  - backend.log                                          │
│  - worker.log                                           │
│  - frontend.log                                         │
│  - build.log                                            │
└─────────────────────────────────────────────────────────┘
```

---

## 🔄 Service Startup Flow

```
User clicks .\Start-All.ps1
    ↓
Check Python & Node.js installed
    ↓
Kill existing processes (cleanup)
    ↓
Start Backend (uvicorn on 8000)
    ↓
Wait for Backend to respond ← ← ← (validates connection)
    ↓
Start Worker (trading strategy)
    ↓
Build Frontend (npm run build)
    ↓
Start Frontend (port 5173)
    ↓
Open http://localhost:5173 in browser
    ↓
🎉 User sees trading dashboard with live data
```

---

## 📝 Configuration

### File: `.env` (in root C:\Renko\)
```
SUPABASE_URL=https://mflakcwgbpghyzdyevsb.supabase.co
SUPABASE_KEY=your-anon-key-here
MT5_LOGIN=101510620
MT5_PASSWORD=your-password
MT5_SERVER=XMGlobal-MT5 5
MT5_PATH=C:\Program Files\XM Global MT5\terminal64.exe
```

### Ports
- Backend: `8000` (internal, change in `backend/main.py`)
- Frontend: `5173` (accessible at http://localhost:5173)
- Logs: `C:\Renko\logs\`

---

## ✅ Verification Checklist

After startup, verify everything works:

- [ ] Browser opens to http://localhost:5173
- [ ] Frontend loads without errors
- [ ] AccountsPanel shows MT5 account (login 101510620)
- [ ] TickersPanel shows 7 symbols with live prices
- [ ] Live positions panel visible (empty if no trades)
- [ ] Can add symbols to watchlist
- [ ] No red error messages in UI

**Test Backend Directly:**
```powershell
# In PowerShell:
Invoke-WebRequest -Uri "http://localhost:8000/api/tickers"
Invoke-WebRequest -Uri "http://localhost:8000/api/accounts"
```

Should get JSON responses with market data and account info.

---

## 🐛 Troubleshooting

### Problem: Backend won't start
**Solutions:**
1. Check Python: `python --version`
2. Check .env exists: `C:\Renko\.env`
3. Check port 8000 free: `netstat -ano | findstr :8000`
4. View logs: `C:\Renko\logs\backend.log`

### Problem: Frontend won't start
**Solutions:**
1. Check Node.js: `npm --version`
2. Install dependencies: `cd C:\Renko\frontend && npm install`
3. Check port 5173: `netstat -ano | findstr :5173`
4. View build error: `C:\Renko\logs\build.log`

### Problem: Can't see prices/data
**Solutions:**
1. Check Supabase credentials in .env
2. Verify backend is running: `curl http://localhost:8000/api/tickers`
3. Check browser console for errors (F12)
4. Verify MT5 terminal is running

### Problem: Services won't auto-start on reboot
**Solutions:**
1. For Task Scheduler: Verify Task Scheduler service is running
2. For NSSM: Verify service startup type is "Automatic"
3. Check Windows Event Log for startup errors

---

## 📈 Next Steps

### Immediate
1. ✅ Run PowerShell startup script
2. ✅ Verify frontend loads
3. ✅ Test trading functionality

### Short Term (This Week)
1. Buy domain name (~$12/year)
2. Setup IIS or Nginx for internet access
3. Get SSL certificate (Let's Encrypt is free)
4. Configure DNS pointing to VPS

### Medium Term (This Month)
1. Setup monitoring/alerts
2. Configure database backups
3. Test live trading thoroughly
4. Implement auto-trading strategies

### Long Term (Ongoing)
1. Monitor performance metrics
2. Implement advanced strategies
3. Scale to multiple accounts
4. Add advanced analytics

---

## 📞 Quick Reference

**Start Services (Easiest):**
```powershell
cd C:\Renko
.\scripts\Start-All.ps1
```

**Access Frontend:**
- http://localhost:5173

**Access Backend:**
- http://localhost:8000/api/tickers

**View Logs:**
- C:\Renko\logs\backend.log
- C:\Renko\logs\worker.log
- C:\Renko\logs\frontend.log

**Stop Services:**
- Ctrl+C in PowerShell windows
- Or Task Manager > Details > End Process

---

## 🎁 Files Created for You

| File | Purpose | Run As |
|------|---------|---------|
| `scripts/Start-All.ps1` | One-click startup | Admin PowerShell |
| `scripts/Install-WindowsServices.bat` | Create Windows services | Admin CMD |
| `scripts/Setup-TaskScheduler.bat` | Schedule auto-start | Admin CMD |
| `scripts/Start-Backend.bat` | Backend only | Admin CMD |
| `scripts/Start-Worker.bat` | Worker only | Admin CMD |
| `scripts/Start-Frontend.bat` | Frontend only | Admin CMD |
| `deploy/WINDOWS_VPS_DEPLOYMENT.md` | Full guide | N/A |
| `deploy/IIS_SETUP.md` | IIS hosting+SSL | N/A |

---

## 🏆 Recommended Setup

**For Maximum Ease & Reliability:**

1. **Initial Testing:** Use `Start-All.ps1` PowerShell script
2. **For Production:** Use `Install-WindowsServices.bat` with NSSM
3. **For Internet:** Use IIS (native Windows) for hosting

This gives you:
- ✅ Automatic startup on reboot
- ✅ Automatic restart if services crash
- ✅ Professional service management
- ✅ HTTPS/SSL support
- ✅ Easy monitoring

---

**Platform:** Windows Server/VPS
**Last Updated:** April 12, 2026
**Status:** Production Ready ✅
