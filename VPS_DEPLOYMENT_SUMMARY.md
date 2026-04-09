# 🎯 VPS Deployment Summary

## Your Setup

```
┌─────────────────────────┐
│   Your Local Laptop     │
├─────────────────────────┤
│  React Frontend         │
│  (Port 5173)            │
│  ↓ connects to          │
│  VPS_IP:8000            │
└─────────────────────────┘
          ↓
┌─────────────────────────┐
│  VPS Remote Server      │
├─────────────────────────┤
│  Backend (Port 8000)    │
│  + MT5 Terminal         │
│  + Python FastAPI       │
└─────────────────────────┘
          ↓
┌─────────────────────────┐
│  Supabase Cloud         │
├─────────────────────────┤
│  Database               │
│  (Accounts, Trades,     │
│   Logs, Watchlist)      │
└─────────────────────────┘
```

---

## ✅ Prerequisites

- [x] MT5 running on VPS (you said it's already running)
- [x] Python 3.11+ on VPS
- [x] Port 8000 accessible on VPS
- [x] Supabase account with credentials
- [ ] VPS IP address (static)

---

## 📋 Setup Steps

### Step 1: Deploy Backend to VPS

**On your VPS:**

1. Copy the `Renko` folder to VPS (via Git, SFTP, or RDP)
2. Open PowerShell on VPS
3. Run:
   ```powershell
   cd C:\path\to\Renko
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. Verify `.env` has correct credentials:
   ```
   MT5_LOGIN=101510620
   MT5_PASSWORD=RichAnshu@1987
   MT5_SERVER=XMGlobal-MT5 5
   SUPABASE_URL=https://mflakcwgbpghyzdyevsb.supabase.co
   SUPABASE_KEY=eyJhbGci...
   ```

5. Start backend:
   ```powershell
   python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
   ```

6. Verify it works:
   ```powershell
   # From VPS:
   curl http://localhost:8000/health
   # Should show: mt5_connected: true
   ```

---

### Step 2: Get VPS IP Address

**On VPS PowerShell:**
```powershell
ipconfig
```

Find your **IPv4 Address** (e.g., `123.45.67.89`)

---

### Step 3: Configure Frontend (on Your Laptop)

**Edit:** `e:\Renko\frontend\.env`

Change:
```
VITE_API_URL=http://123.45.67.89:8000
```

(Replace `123.45.67.89` with your actual VPS IP)

---

### Step 4: Test Connection from Laptop

**In PowerShell on your laptop:**
```powershell
curl http://123.45.67.89:8000/health
```

Should return:
```json
{"status":"ok","mt5_connected":true,"connected_accounts":[101510620]}
```

---

### Step 5: Run Frontend (on Your Laptop)

```powershell
cd e:\Renko\frontend
npm run dev
```

Open browser: `http://localhost:5173`

---

## 🎉 Done!

Your dashboard now:
- ✅ Runs on your laptop
- ✅ Connects to backend on VPS
- ✅ Trades execute on VPS MT5
- ✅ Data stored in Supabase cloud

---

## 📁 Files to Review

| File | Purpose |
|------|---------|
| [VPS_BACKEND_SETUP.md](./VPS_BACKEND_SETUP.md) | Detailed VPS backend setup guide |
| [CONFIGURE_FRONTEND_FOR_VPS.md](./CONFIGURE_FRONTEND_FOR_VPS.md) | How to configure frontend for remote backend |
| [deploy_vps_backend.bat](./deploy_vps_backend.bat) | Quick deployment script for VPS |
| `.env` (on VPS) | Backend configuration |
| `frontend/.env` (on laptop) | Frontend configuration |

---

## ⚙️ Configuration Checklist

### On VPS (Backend)
- [ ] `.env` file with:
  - [ ] `SUPABASE_URL`
  - [ ] `SUPABASE_KEY`
  - [ ] `MT5_PATH`
  - [ ] `MT5_LOGIN`
  - [ ] `MT5_PASSWORD`
  - [ ] `MT5_SERVER`
- [ ] Port 8000 open in firewall
- [ ] MT5 running and logged in
- [ ] Backend started: `python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000`

### On Laptop (Frontend)
- [ ] `frontend/.env` with correct VPS IP:
  ```
  VITE_API_URL=http://<VPS_IP>:8000
  ```
- [ ] Frontend running: `npm run dev`
- [ ] Browser connects to: `http://localhost:5173`

---

## 🧪 Testing

```powershell
# Test 1: Backend running
curl http://<VPS_IP>:8000/health

# Test 2: MT5 connected
curl http://<VPS_IP>:8000/diagnose

# Test 3: Get prices
curl http://<VPS_IP>:8000/api/tickers

# Test 4: Add account
curl -X POST http://<VPS_IP>:8000/api/accounts ^
  -H "Content-Type: application/json" ^
  -d "{\"login\":101510620,\"password\":\"RichAnshu@1987\",\"server\":\"XMGlobal-MT5 5\"}"
```

---

## 🚀 Quick Reference

**Start Backend on VPS:**
```powershell
cd C:\Renko
.venv\Scripts\activate
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

**Start Frontend on Laptop:**
```powershell
cd e:\Renko\frontend
npm run dev
# Open: http://localhost:5173
```

**Keep MT5 Terminal Running on VPS**

That's it! 🎉

---

## 📞 Troubleshooting

| Problem | Solution |
|---------|----------|
| Can't connect from laptop | Check VPS IP, verify port 8000 open, test `curl http://<VPS_IP>:8000/health` |
| Prices show `---` | Restart backend on VPS, verify MT5 is running and logged in |
| Trades not executing | Check account balance, verify symbols in MT5 Market Watch |
| Backend won't start | Check Python 3.11+, check `.env` has all required vars, check dependencies installed |
| Dashboard shows no accounts | Run `/diagnose` endpoint, check Supabase connection |

See detailed guides at top of this file for more info.

---

## 🔐 Production Notes

**Before going live:**
- [ ] Use HTTPS (SSL certificate)
- [ ] Restrict port 8000 to specific IPs if not needed publicly
- [ ] Move credentials to environment variables
- [ ] Setup auto-restart on VPS (NSSM or Supervisor)
- [ ] Regular backups of Supabase
- [ ] Monitor VPS resources (CPU, RAM, disk)
- [ ] Setup error alerts

See [VPS_BACKEND_SETUP.md](./VPS_BACKEND_SETUP.md#part-6-security-notes) for security details.

---

**Ready to deploy? Start with [VPS_BACKEND_SETUP.md](./VPS_BACKEND_SETUP.md)** ✅
