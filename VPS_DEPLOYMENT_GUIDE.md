# VPS DEPLOYMENT GUIDE - STEP BY STEP

## Overview
This guide covers deploying your Renko Trading Bot on a VPS where:
- **MT5 Terminal** runs (pulls live prices) 
- **Backend API** (FastAPI) runs (processes signals, places trades)
- **Frontend** connects to backend API remotely

**Architecture:**
```
VPS:
├── MetaTrader 5 Terminal (running as service)
├── Python Backend (FastAPI + Worker)
└── Nginx/Supervisor (for process management)

Local/Separate Server:
└── React Frontend (deployed on any host)
```

---

## PART 1: VPS PREREQUISITES

### A. VPS Requirements
- **OS**: Windows Server 2016+ OR Linux with Windows RDP/VNC
- **RAM**: Minimum 4GB (8GB recommended)
- **Storage**: 50GB SSD
- **CPU**: 2 cores minimum
- **Network**: Static IP, port 8000 accessible

### B. Software to Install

#### On Windows VPS:
1. **Python 3.11+**
   ```
   Download from python.org
   Check: Admin Command Prompt → python --version
   ```

2. **MetaTrader 5 Terminal**
   ```
   Download from your broker
   Install normally
   ```

3. **Git** (optional, for pulling code)
   ```
   Download from https://git-scm.com/
   ```

#### On Linux VPS (if using WSL or Linux MT5):
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv git
```

---

## PART 2: MT5 TERMINAL SETUP (VPS)

### Step 1: Install MT5 on VPS
1. Download from your broker's website
2. Install normally on VPS (C:\Program Files\MetaTrader 5)
3. Don't launch yet - we'll configure it

### Step 2: Create/Add Trading Account
1. Launch MT5 → File → Login
2. Enter your credentials:
   - **Login**: Your account number
   - **Password**: Your password
   - **Server**: Select correct broker server
3. Click OK and wait for sync
4. Once logged in, note:
   - Account Login #
   - Server name
   - Available symbols

### Step 3: Verify Available Symbols
1. In MT5, go to Market Watch (Ctrl+M)
2. Right-click → Show All
3. Select symbols you want to trade
4. Note: Your backend config must match these exact symbol names

### Step 4: Configure MT5 Options (Important!)
Menu → Tools → Options → Expert Advisors:
- ✅ Allow automated trading
- ✅ Allow WebRequest (for api calls if needed)
- Set DLL imports: Allow if needed

---

## PART 3: BACKEND DEPLOYMENT

### Step 1: Clone/Upload Code to VPS

**Option A: Via Git (recommended)**
```powershell
# Open PowerShell as Administrator on VPS
cd C:\Users\YourUser\Desktop
git clone https://github.com/yourrepo/renko.git
cd renko
```

**Option B: Via File Transfer**
- Use WinSCP or RDP to copy your project folder to VPS
- Example: `C:\Users\trader\renko`

### Step 2: Setup Python Virtual Environment
```powershell
cd C:\Users\trader\renko

# Create venv
python -m venv .venv

# Activate venv
.\.venv\Scripts\Activate.ps1

# If you get permission error, run:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Create .env File
```powershell
# In your renko folder, create .env from .env.example
# IMPORTANT: Fill in these values:

Copy-Item .env.example .env
# Now edit .env with your actual values (use Notepad)
```

**Your .env should have:**
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key_here
MT5_PATH=C:\Program Files\MetaTrader 5
RENKO_BRICK_SIZE=1.0
SYMBOL=XAUUSD
POLL_INTERVAL=0.5
API_HOST=0.0.0.0
API_PORT=8000
ENVIRONMENT=production
```

### Step 4: Test Backend Locally
```powershell
# Activate venv first
.\.venv\Scripts\Activate.ps1

# Start server
uvicorn backend.main:app --host 0.0.0.0 --port 8000

# You should see:
# INFO:     Application startup complete
# INFO:     Uvicorn running on http://0.0.0.0:8000

# From another PowerShell window, test:
curl http://localhost:8000/accounts

# If it works, you should get JSON response: []
```

**If it fails:**
- Check .env file has all required values
- Check MT5_PATH is correct
- Check Supabase credentials are valid

---

## PART 4: SETUP PROCESS MANAGEMENT

### Option A: Using Supervisor (Recommended for Linux/WSL)

**Install Supervisor:**
```bash
sudo apt install supervisor
```

**Create supervisor config:**
```bash
sudo nano /etc/supervisor/conf.d/renko-bot.conf
```

**Add this content:**
```ini
[program:renko-bot]
directory=/home/trader/renko
command=/home/trader/renko/.venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000
user=trader
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/renko-bot.log
environment=PATH="/home/trader/renko/.venv/bin"
```

**Enable:**
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start renko-bot
sudo supervisorctl status renko-bot
```

### Option B: Using NSSM (Non-Sucking Service Manager) - Windows

**Download NSSM:**
1. Go to: https://nssm.cc/download
2. Extract to `C:\nssm`

**Install as service:**
```powershell
cd C:\nssm\win64

.\nssm.exe install RenkoBot "C:\Users\trader\renko\.venv\Scripts\python.exe" "-m uvicorn backend.main:app --host 0.0.0.0 --port 8000"

# Set working directory
.\nssm.exe set RenkoBot AppDirectory C:\Users\trader\renko

# Start service
.\nssm.exe start RenkoBot

# Check status
.\nssm.exe status RenkoBot
```

### Option C: Using Task Scheduler (Windows - Simple)

1. Open Task Scheduler
2. Create Basic Task → "RenkoBot"
3. Trigger: At system startup
4. Action → Start a program:
   - Program: `C:\Users\trader\renko\.venv\Scripts\python.exe`
   - Arguments: `-m uvicorn backend.main:app --host 0.0.0.0 --port 8000`
   - Start in: `C:\Users\trader\renko`

---

## PART 5: NGINX SETUP (Reverse Proxy)

### For Better Performance & Security

**Install Nginx:**
```bash
# Linux
sudo apt install nginx

# Windows: Download from https://nginx.org/en/download.html
```

**Configuration:**
```nginx
# /etc/nginx/sites-available/renko (Linux)
# or C:\nginx\conf\nginx.conf (Windows)

server {
    listen 80;
    server_name your-vps-ip.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

**Enable (Linux):**
```bash
sudo ln -s /etc/nginx/sites-available/renko /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## PART 6: SUPABASE SCHEMA SETUP

### Step 1: Create Supabase Project
1. Go to https://app.supabase.com
2. Create new project
3. Wait for initialization
4. Note your:
   - **Project URL** → SUPABASE_URL
   - **Anon Key** → SUPABASE_KEY

### Step 2: Create Database Schema
1. In Supabase Dashboard → SQL Editor
2. Copy entire content from: `backend/supabase/schema.sql`
3. Paste into SQL Editor
4. Click "Run" or Execute
5. Wait for all tables to be created

**Verify:**
- Go to "Tables" section
- You should see: accounts, watchlist, trades, logs, bot_control, etc.

### Step 3: Test Connection from Backend
```powershell
# From your renko folder with venv activated
python -c "
from backend.supabase.client import supabase_client
result = supabase_client.table('accounts').select('*').execute()
print('✅ Supabase connected!')
print(result)
"
```

---

## PART 7: FRONTEND DEPLOYMENT

### Option A: Deploy on Vercel (Recommended - Easiest)

1. **Push frontend to GitHub**
```bash
cd frontend
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/youruser/renko-frontend
git push -u origin main
```

2. **Deploy on Vercel**
   - Go to https://vercel.com
   - Connect GitHub account
   - Import `renko-frontend` repository
   - Add Environment Variable:
     - `VITE_API_URL=http://your-vps-ip:8000`
   - Deploy

3. **Update Frontend Config**
   - In `frontend/src/services/api.ts`, ensure:
   ```typescript
   const BASE_URL = import.meta.env.VITE_API_URL || 'http://your-vps-ip:8000';
   ```

### Option B: Deploy on VPS with Nginx

**Build Frontend:**
```bash
cd frontend
npm install
npm run build

# Creates dist/ folder with static files
```

**Nginx Configuration:**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /var/www/renko-frontend;

    location / {
        try_files $uri /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
    }
}
```

### Option C: Docker (Advanced)

Create `Dockerfile` for backend and `docker-compose.yml` for full stack.

---

## PART 8: VERIFY EVERYTHING WORKS

### Test 1: Backend is Running
```powershell
Invoke-WebRequest http://localhost:8000/accounts
# Should return: [] or list of accounts
```

### Test 2: MT5 Connection
```powershell
python -c "
import MetaTrader5 as mt5
print('MT5 Path:', 'C:\\Program Files\\MetaTrader 5')
# Should not error
"
```

### Test 3: Supabase Connection
```powershell
python -c "
from backend.supabase.client import supabase_client
result = supabase_client.table('accounts').select('*').execute()
print('✅ Connected to Supabase')
"
```

### Test 4: Frontend Can Connect
- Open frontend in browser
- Open DevTools (F12) → Network tab
- Check if API calls to `/accounts` succeed (200 status)

---

## PART 9: MONITORING & LOGS

### Check Service Status
```powershell
# If using NSSM
nssm status RenkoBot

# If using Task Scheduler
# Check Task Scheduler → RenkoBot → Last Run Result

# If using Supervisor
sudo supervisorctl status renko-bot
```

### View Logs
```powershell
# Windows - Task Scheduler
# Right-click task → View Logs

# Linux - Supervisor
sudo tail -f /var/log/renko-bot.log

# FastAPI built-in logging:
# Logs appear in the console/service output
```

### Create Log Rotation (Linux)
```bash
sudo nano /etc/logrotate.d/renko-bot
```

```
/var/log/renko-bot.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 trader trader
    sharedscripts
}
```

---

## PART 10: FIREWALL & SECURITY

### Configure Windows Firewall
```powershell
# Allow port 8000
New-NetFirewallRule -DisplayName "Allow Renko API" `
    -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

### Configure Linux Firewall
```bash
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw allow 8000/tcp    # Backend API (if no Nginx)
sudo ufw enable
```

### Use HTTPS (SSL/TLS)
1. **Get Free SSL from Let's Encrypt:**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d your-domain.com
```

2. **Update Nginx:**
```nginx
server {
    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
    }
}
```

---

## PART 11: TROUBLESHOOTING

### Backend won't start
1. Check Python version: `python --version` (must be 3.9+)
2. Check venv activated: Should see `(.venv)` in prompt
3. Check .env file exists and has all variables
4. Check MT5_PATH is correct
5. Check Supabase credentials

### MT5 Connection Fails
1. Verify MT5 is logged in and running
2. Check account login/password are correct
3. Check server name matches (e.g., "XM Real5" not "XM Demo5")
4. Restart MT5

### Supabase Connection Fails
1. Check internet connection
2. Check SUPABASE_URL is correct (including https://)
3. Check SUPABASE_KEY is correct
4. Verify tables exist in Supabase (run schema.sql again)

### Frontend can't reach backend
1. Check backend is running: `Invoke-WebRequest http://localhost:8000`
2. Check firewall allows port 8000
3. Check VITE_API_URL in frontend is correct VPS IP/domain
4. Check CORS is enabled on backend (add to main.py if needed)

### Add CORS Support (if needed)
```python
# In backend/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## PART 12: MAINTENANCE

### Weekly Tasks
- Check logs for errors
- Verify all processes are running
- Test a manual trade to ensure everything works

### Monthly Tasks
- Update Python packages: `pip install --upgrade -r requirements.txt`
- Review Supabase logs for large data issues
- Backup database: Export from Supabase dashboard

### Security
- Change MT5 password periodically
- Rotate Supabase keys yearly
- Keep OS and software updated

---

## Quick Reference: Deployment Checklist

- [ ] VPS ordered and accessible
- [ ] Windows/Linux setup complete
- [ ] Python 3.11+ installed
- [ ] MT5 installed and logged in
- [ ] Code uploaded to VPS
- [ ] Virtual environment created and activated
- [ ] .env file created with all values
- [ ] Supabase schema created
- [ ] Backend tested locally
- [ ] Process manager installed (Supervisor/NSSM)
- [ ] Backend running as service
- [ ] Nginx configured (optional)
- [ ] Frontend deployed
- [ ] All endpoints tested
- [ ] Logs monitored
- [ ] Firewall configured

---

## Support

If you encounter issues:
1. Check logs first
2. Verify all .env variables
3. Test each component independently
4. Check internet connectivity
5. Restart all services

