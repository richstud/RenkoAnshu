# 🚀 VPS Deployment Guide - Backend + MT5

## Architecture

```
VPS (Remote Server):
├── MetaTrader 5 Terminal (running)
├── Python Backend (FastAPI) ← RUN HERE
└── Supervisor/Gunicorn (process management)

Your Laptop (Local):
└── React Frontend (connects to VPS backend)
    
Cloud:
└── Supabase (database)
```

---

## PART 1: SETUP VPS BACKEND

### Prerequisites

Your VPS should have:
- [ ] Windows Server 2016+ OR Linux with WSL2
- [ ] Python 3.11+ installed
- [ ] MT5 Terminal running and logged in
- [ ] Static IP or Fixed hostname
- [ ] Port 8000 accessible (firewall opens it)
- [ ] Git installed (for easy code deployment)

---

### Step 1: Get Code on VPS

**Option A: Via Git (Recommended)**

```powershell
# SSH into your VPS
# Then:
cd C:\Users\YourUsername\Desktop
git clone https://github.com/YOUR_REPO/Renko.git
cd Renko
```

**Option B: Via SFTP/FTP**

Upload the entire `Renko` folder to VPS

**Option C: Via RDP**

Copy folder via RDP file transfer

---

### Step 2: Python Setup on VPS

```powershell
# Open PowerShell as Administrator on VPS

# Navigate to project
cd C:\Users\YourUsername\Desktop\Renko

# Create virtual environment
python -m venv .venv

# Activate it
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Or if that fails:
pip install fastapi uvicorn pydantic pydantic-settings MetaTrader5 supabase python-dotenv gunicorn
```

---

### Step 3: Configure Environment on VPS

**Create/Update `.env` file on VPS:**

```bash
# Verify .env exists
# E:\Renko\.env (or your path\Renko\.env)

# Most important: Supabase credentials (same as local)
SUPABASE_URL=https://mflakcwgbpghyzdyevsb.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# MT5 (should work on VPS where terminal is running)
MT5_PATH=C:\Program Files\MetaTrader 5\terminal64.exe
MT5_LOGIN=101510620
MT5_PASSWORD=RichAnshu@1987
MT5_SERVER=XMGlobal-MT5 5

# API Server
API_HOST=0.0.0.0
API_PORT=8000
```

---

### Step 4: Test Backend on VPS

```powershell
# Still in .venv

# Test startup
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Should see:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Connected account 101510620
```

✅ If you see "Connected account", MT5 communication works!

Test from your local laptop:

```powershell
# From your laptop:
curl http://<VPS_IP>:8000/health

# Should return:
# {"status":"ok","active":false,"mt5_connected":true,"connected_accounts":[101510620]}
```

---

### Step 5: Setup Auto-Start with Supervisor (Windows)

**On Windows VPS**, use NSSM (Non-Sucking Service Manager) to run backend as a service:

**A) Download NSSM:**
```
https://nssm.cc/download
Extract to: C:\nssm\nssm-2.24\win64\nssm.exe
```

**B) Create Batch Script:**

Create `C:\start_backend.bat`:

```batch
@echo off
cd /d C:\Users\YourUsername\Desktop\Renko
.venv\Scripts\activate
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

**C) Install Service:**

```powershell
# Run as Administrator
C:\nssm\nssm-2.24\win64\nssm.exe install RenkoBackend C:\start_backend.bat

# Start service
net start RenkoBackend

# Check status
netstat -ano | findstr :8000
```

**D) View Logs:**

```powershell
# Stop service
net stop RenkoBackend

# Check logs
C:\nssm\nssm-2.24\win64\nssm.exe dump RenkoBackend
```

---

### Alternative: Setup with Gunicorn (Production Standard)

```powershell
# Install Gunicorn (already installed)

# Create Gunicorn config file: C:\gunicorn_config.py
import multiprocessing

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
max_requests = 1000
max_requests_jitter = 50
timeout = 60
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s'

# Start with Gunicorn
gunicorn --config C:\gunicorn_config.py backend.main:app
```

---

### Step 6: Open Firewall Port on VPS

**Windows VPS:**

```powershell
# Open port 8000
netsh advfirewall firewall add rule name="Allow port 8000" dir=in action=allow protocol=tcp localport=8000

# Verify
netsh advfirewall firewall show rule name="Allow port 8000"
```

**Linux VPS:**

```bash
# UFW
sudo ufw allow 8000

# IPTables
sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT
```

---

### Step 7: Get Your VPS IP Address

**Windows:**
```powershell
ipconfig
# Look for: IPv4 Address (public IP from hosting provider)
```

**Linux:**
```bash
curl ifconfig.me
# Or: ip addr show
```

Or check your hosting provider's console for the public IP.

---

## PART 2: CONFIGURE FRONTEND (Local Laptop)

### Step 1: Update Frontend to Connect to VPS Backend

**On your local laptop**, edit `frontend/.env`:

```
VITE_API_URL=http://<VPS_IP>:8000
```

Replace `<VPS_IP>` with your actual VPS IP address.

**Example:**
```
VITE_API_URL=http://123.45.67.89:8000
```

---

### Step 2: Restart Frontend

```powershell
cd e:\Renko\frontend
npm run dev
```

Now your frontend will connect to the **VPS backend** instead of local!

---

### Step 3: Verify Connection

**In dashboard, you should see:**
- ✅ Accounts loaded
- ✅ Bid/Ask prices (connected to VPS MT5)
- ✅ Tickers available
- ✅ Can add to watchlist
- ✅ Can start/stop bot on VPS

---

## PART 3: MONITORING & MAINTENANCE

### Monitor Backend on VPS

```powershell
# SSH into VPS, then:

# Check if running
netstat -ano | findstr :8000

# Check if port is accessible from outside
# From laptop:
curl http://<VPS_IP>:8000/health

# View recent logs
# Find the running process PID and attach to it
tasklist | findstr python

# Real-time monitoring
wmic process where handle=<PID> list
```

---

### Restart Backend (if it crashes)

**If backend stops:**

```powershell
# SSH into VPS

# Restart service
net stop RenkoBackend
net start RenkoBackend

# Or manually restart
cd C:\Users\YourUsername\Desktop\Renko
.venv\Scripts\activate
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

---

### View Real-Time Logs

```powershell
# Option 1: While running in terminal
# Logs appear directly

# Option 2: Add logging to file
# Backend logs to: C:\Renko\logs\backend.log

# Create log directory
mkdir C:\Renko\logs

# Update backend to log to file (optional)
```

---

## PART 4: TROUBLESHOOTING

### Issue: "Cannot connect from laptop"

**Check:**
```powershell
# From laptop:
ping <VPS_IP>
# Should work

curl http://<VPS_IP>:8000/health
# Should return JSON

# If not, check firewall on VPS:
netsh advfirewall firewall show rule name="Allow port 8000"
```

---

### Issue: "MT5 not connecting on VPS"

**Check:**
```powershell
# SSH to VPS, run:
curl http://localhost:8000/diagnose

# Should show:
# "mt5_connected": true
# "connected_accounts": [101510620]

# If not:
# 1. Verify MT5 is running
# 2. Verify credentials in .env match MT5 login
# 3. Restart backend
```

---

### Issue: "Prices still showing --- on dashboard"

**Possible causes:**
1. MT5 on VPS not initialized when backend started
   - Stop and restart backend
   
2. Symbols not in MT5 Market Watch on VPS
   - Log into MT5 on VPS
   - View > Market Watch
   - Add XAUUSD, EURUSD, etc.
   - Restart backend

3. Network latency
   - Prices may take longer to fetch
   - Wait 10 seconds for data to populate

---

### Issue: "Trades not executing"

**Check:**
```powershell
# From dashboard, click a symbol, then check logs:
curl http://<VPS_IP>:8000/api/logs

# Should show trade execution attempts
# Common reasons:
# - Insufficient balance on account
# - Lot size too small
# - Market closed
# - Symbol not visible on VPS MT5
```

---

## PART 5: PRODUCTION CHECKLIST

- [ ] VPS IP is static (doesn't change)
- [ ] Port 8000 is open in firewall
- [ ] Backend starts automatically after VPS reboot
- [ ] MT5 is configured to restart auto-login
- [ ] `.env` file has Supabase credentials
- [ ] Frontend `.env` has correct VPS IP
- [ ] Backend test: `http://<VPS_IP>:8000/health` works from laptop
- [ ] Frontend connects and shows data
- [ ] Can add symbols to watchlist
- [ ] Can start/stop bot from dashboard
- [ ] Trades execute on VPS MT5

---

## PART 6: SECURITY NOTES

⚠️ **Before going to production:**

1. **Firewall:** Only open port 8000 if needed
   ```powershell
   # Current: Open to all IPs
   # Better: Open only to your laptop IP
   netsh advfirewall firewall add rule name="Renko" dir=in action=allow protocol=tcp localport=8000 remoteip=YOUR_LAPTOP_IP
   ```

2. **API Key:** Move Supabase key to environment variable (not in .env)
   ```powershell
   # Set system environment variable
   setx SUPABASE_KEY "your_key_here"
   ```

3. **HTTPS:** In production, use HTTPS (port 443)
   - Install SSL certificate
   - Use Nginx or IIS as reverse proxy

4. **Credentials:** Rotate MT5 password regularly

---

## PART 7: SETUP SUMMARY

### Quick Reference

| Component | Location | Command |
|-----------|----------|---------|
| Backend | VPS | `python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000` |
| MT5 | VPS | Runs as terminal application |
| Frontend | Laptop | `npm run dev` |
| Database | Cloud | Supabase (no action needed) |

### Environment Variables

**VPS (`C:\Renko\.env`):**
```
SUPABASE_URL=...
SUPABASE_KEY=...
MT5_PATH=...
MT5_LOGIN=...
MT5_PASSWORD=...
MT5_SERVER=...
```

**Laptop (`frontend/.env`):**
```
VITE_API_URL=http://<VPS_IP>:8000
```

---

## 🚀 QUICK START FOR VPS

1. **SSH into VPS**
2. **Copy Renko folder to VPS**
3. **Run on VPS:**
   ```powershell
   cd Renko
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
   ```
4. **On Laptop:**
   ```powershell
   # Edit frontend/.env with VPS IP
   cd frontend
   npm run dev
   # Open http://localhost:5173
   ```
5. **Done!** Dashboard connects to VPS backend 🎉

---

## 📞 Need Help?

**Backend not starting on VPS?**
- Check Python is 3.11+: `python --version`
- Check dependencies: `pip list | findstr fastapi`
- Check MT5 is running

**Can't connect from laptop?**
- Check VPS IP is correct
- Check port 8000 is open: `netstat -ano | findstr 8000`
- Check: `curl http://<VPS_IP>:8000/health`

**Trades not executing?**
- Check MT5 is logged in on VPS
- Check symbols in MT5 Market Watch
- Check account balance
- Check logs: `curl http://<VPS_IP>:8000/api/logs`
