# Renko Trading Bot - Windows VPS Deployment Guide

## 🎯 Overview
This guide explains how to deploy the Renko Trading Bot on a Windows VPS with automatic startup.

## ⚙️ System Requirements
- Windows Server 2019 or later (or Windows 10/11 Pro)
- Python 3.11+ (with pip)
- Node.js 18+ (with npm)
- 4GB RAM minimum
- 20GB disk space minimum
- Administrator access

## 📋 Pre-Deployment Checklist

- [ ] Windows VPS created and accessible via RDP
- [ ] Python 3.11+ installed globally
- [ ] Node.js 18+ installed globally
- [ ] Git installed (for cloning the project)
- [ ] Renko project cloned to C:\Renko
- [ ] .env file configured with Supabase credentials
- [ ] MT5 terminal installed (for live trading)

## 🚀 Deployment Options

### Option 1: PowerShell Script (Easiest)

**Best for:** Quick testing, manual startup, development

1. Open PowerShell as Administrator
2. Navigate to project: `cd C:\Renko`
3. Run startup script:
   ```powershell
   .\scripts\Start-All.ps1
   ```
4. Script will:
   - Start Backend on http://localhost:8000
   - Start Worker process
   - Build and start Frontend on http://localhost:5173
   - Open browser automatically

**Advantages:**
- Simple one-command startup
- Beautiful colored logging
- Auto-opens browser
- Easy to see logs in real-time

**To Stop:**
- Close console windows or press Ctrl+C

---

### Option 2: Windows Task Scheduler (Automatic on Boot)

**Best for:** Production VPS, auto-start on reboot

1. Open Command Prompt as Administrator
2. Navigate to: `cd C:\Renko\scripts`
3. Run setup: `Setup-TaskScheduler.bat`
4. Tasks will auto-start on system reboot

**View Tasks:**
- Open Task Scheduler (Windows Admin Tools)
- Navigate to: Task Scheduler Library > Renko

**Advantages:**
- Services restart automatically after crash
- Auto-start on server reboots
- No terminal windows visible
- Runs in background

**To Remove Tasks:**
```cmd
schtasks /delete /tn "Renko\Backend" /f
schtasks /delete /tn "Renko\Worker" /f
schtasks /delete /tn "Renko\Frontend" /f
```

---

### Option 3: NSSM Windows Services (Professional)

**Best for:** Enterprise production, service management, monitoring

1. Download NSSM: https://nssm.cc/download
2. Extract to: `C:\nssm`
3. Open Command Prompt as Administrator
4. Run: `C:\Renko\scripts\Install-WindowsServices.bat`
5. Services will install and auto-start

**Manage Services:**
```cmd
net start RenkoBackend      # Start backend
net stop RenkoBackend       # Stop backend
net start RenkoWorker       # Start worker
net stop RenkoWorker        # Stop worker
```

**View Service Status:**
- Services console: `services.msc`

**View Logs:**
- `C:\Renko\logs\backend.log`
- `C:\Renko\logs\worker.log`

**Remove Services:**
```cmd
C:\nssm\nssm-2.24\win64\nssm.exe remove RenkoBackend confirm
C:\nssm\nssm-2.24\win64\nssm.exe remove RenkoWorker confirm
```

**Advantages:**
- Professional Windows service management
- Built-in monitoring and restart
- Can set dependencies between services
- Resource limits and priorities
- Event Log integration

---

### Option 4: IIS with URL Rewrite (Advanced)

**Best for:** Web hosting multiple apps, reverse proxy, SSL termination

See: `deploy/iis-setup.md`

---

## 🌐 Networking Configuration

### For Local Network Access:
Frontend will be accessible at: `http://<VPS-IP>:5173`

### For Internet Access (Recommended):
1. Buy a domain name
2. Point DNS to your VPS IP
3. Install SSL certificate (Let's Encrypt)
4. Set up reverse proxy with IIS or Nginx

**IIS Setup (Windows):**
1. Install IIS with URL Rewrite module
2. Create website pointing to: `C:\Renko\frontend\dist`
3. Configure reverse proxy rules for `/api/*` to `http://localhost:8000`

---

## 📝 Configuration Files

### .env (Windows VPS)
```
SUPABASE_URL=https://mflakcwgbpghyzdyevsb.supabase.co
SUPABASE_KEY=your_anon_key_here
MT5_LOGIN=101510620
MT5_PASSWORD=your_password
MT5_SERVER=XMGlobal-MT5 5
MT5_PATH=C:\Program Files\XM Global MT5\terminal64.exe
```

### Port Configuration:
- Backend: `8000` (internal only, change in main.py if needed)
- Frontend: `5173` (internal, expose via IIS/firewall)
- Logs: `C:\Renko\logs\`

---

## 🔧 Troubleshooting

### Backend won't start
1. Check Python installation: `python --version`
2. Verify .env file exists in project root
3. Check port 8000 isn't already in use: `netstat -ano | findstr :8000`
4. View logs: `C:\Renko\logs\backend.log`

### Frontend won't start
1. Check Node.js: `npm --version`
2. Install dependencies: `cd frontend && npm install`
3. Check port 5173: `netstat -ano | findstr :5173`
4. View build errors: `C:\Renko\logs\build.log`

### Worker won't connect to backend
1. Ensure backend is running first
2. Check firewall: `netsh advfirewall show allprofiles`
3. Verify Supabase credentials in .env

### MT5 Terminal issues
1. Ensure MT5 is installed at configured path
2. Update MT5 to latest version
3. Check account credentials
4. Verify internet connection

---

## 📊 Monitoring

### Check Service Status (PowerShell):
```powershell
Get-Process python | Where-Object { $_.Path -like "*uvicorn*" }
Get-Process node
```

### Monitor Logs:
```powershell
Get-Content -Path "C:\Renko\logs\backend.log" -Tail 20 -Wait
```

### Database Status:
Frontend shows real-time:
- Connected accounts
- Active trades
- Strategy status
- Error logs

---

## 🔐 Security Recommendations

1. **Firewall Rules:**
   - Open port 80/443 (HTTP/HTTPS) for internet traffic
   - Keep port 8000 (Backend) internal only
   - Restrict port 5173 (Frontend) to needed IPs

2. **VPS Hardening:**
   - Enable Windows Defender
   - Keep Windows updated
   - Disable RDP if not needed
   - Use strong passwords

3. **Application Security:**
   - Use HTTPS only for production
   - Rotate API keys monthly
   - Enable database backups
   - Monitor error logs for attacks

4. **Example Windows Firewall Rules:**
```powershell
# Allow HTTP/HTTPS
New-NetFirewallRule -DisplayName "Allow HTTP" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 80
New-NetFirewallRule -DisplayName "Allow HTTPS" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 443

# Block Backend to internet (internal only)
New-NetFirewallRule -DisplayName "Block Backend" -Direction Inbound -Action Block -Protocol TCP -LocalPort 8000
```

---

## 🚀 Startup Comparison

| Method | Setup | Auto-Reboot | Monitoring | Best For |
|--------|-------|-------------|-----------|----------|
| PowerShell | 1 min | ❌ Manual | ✅ Console | Development |
| Task Scheduler | 2 min | ✅ Auto | ⚠️ Limited | Testing |
| NSSM Services | 5 min | ✅ Auto | ✅ Full | Production |
| IIS Hosting | 10 min | ✅ Auto | ✅ Full | Enterprise |

---

## ✅ Post-Deployment Testing

1. **Backend Health:**
   ```
   curl http://localhost:8000/api/tickers
   ```

2. **Frontend Access:**
   - Open browser to http://localhost:5173
   - Should load with accounts panel

3. **Database Connection:**
   - View AccountsPanel - should show account info
   - Check Supabase dashboard

4. **Trading Integration:**
   - Add symbol to watchlist
   - Verify prices update each 2 seconds
   - Try placing a test trade

---

## 📞 Support

If services won't start:
1. Check logs in `C:\Renko\logs\`
2. Verify .env configuration
3. Run `python -m pip install -r requirements.txt` (update dependencies)
4. Restart Windows
5. Try PowerShell script first before services

---

**Last Updated:** April 12, 2026
**Platform:** Windows Server/VPS
**Environment:** Production Ready
