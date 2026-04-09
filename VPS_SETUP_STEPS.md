# 📖 VPS Setup - Step by Step (Do This First!)

## Complete Setup Process

Follow these steps **EXACTLY** in this order.

---

## ✅ Check Prerequisites

Before you start:

- [ ] MT5 is already running on VPS (you confirmed this)
- [ ] You have VPS access (SSH/RDP)
- [ ] Python 3.11+ is installed on VPS
- [ ] You have Renko code on VPS
- [ ] You have Supabase credentials

---

## 🎯 Part A: Deploy Backend to VPS

### A1: Upload Code to VPS

**Choose ONE method:**

**Method 1: Git (Easiest)**
```bash
# SSH into VPS, then:
cd C:\Users\YourUsername\Desktop
git clone https://github.com/YOUR_REPO/Renko.git
cd Renko
```

**Method 2: SFTP (WinSCP)**
1. Download WinSCP
2. Connect to VPS
3. Upload entire `Renko` folder to VPS

**Method 3: RDP**
1. RDP into VPS
2. Copy `Renko` folder via Windows Explorer

### A2: Setup Python Environment on VPS

**Open PowerShell on VPS (as Administrator):**

```powershell
# Navigate to project
cd C:\Users\YourUsername\Desktop\Renko

# Create virtual environment
python -m venv .venv

# Activate it
.venv\Scripts\activate

# Install dependencies (takes 2-3 minutes)
pip install -r requirements.txt
```

Expected output:
```
Successfully installed fastapi-0.135.3 uvicorn-0.44.0 ...
```

### A3: Verify Configuration File

**On VPS, check `.env` file exists:**

```powershell
type .env
```

**It should contain:**
```
SUPABASE_URL=https://mflakcwgbpghyzdyevsb.supabase.co
SUPABASE_KEY=eyJhbGci...
MT5_LOGIN=101510620
MT5_PASSWORD=RichAnshu@1987
MT5_SERVER=XMGlobal-MT5 5
MT5_PATH=C:\Program Files\MetaTrader 5\terminal64.exe
```

If missing, create/edit `.env` with above values.

### A4: Test Backend Startup

**Still on VPS PowerShell (with .venv activated):**

```powershell
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

**Wait for this output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
INFO:     Added default account 101510620 from environment
INFO:     Attempting to connect 1 account(s)
INFO:     Connected account 101510620
```

✅ **If you see all this, backend is working!**

❌ **If you don't:**
1. Check MT5 is running on VPS
2. Check credentials in `.env`
3. Run: `python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 2>&1`
4. Look for error messages

### A5: Firewall Configuration

**Open port 8000 on VPS firewall:**

```powershell
# Run as Administrator on VPS:
netsh advfirewall firewall add rule name="Allow Renko Port 8000" dir=in action=allow protocol=tcp localport=8000

# Verify:
netsh advfirewall firewall show rule name="Allow Renko Port 8000"
```

### A6: Get Your VPS IP Address

**On VPS PowerShell:**

```powershell
ipconfig
```

Look for **IPv4 Address** - should be something like `123.45.67.89`

**Write it down here:** `_______________________`

---

## 🖥️ Part B: Configure Frontend on Your Laptop

### B1: Update Frontend Environment

**On your laptop, edit:** `e:\Renko\frontend\.env`

**Current content (local testing):**
```
VITE_API_URL=http://localhost:8000
```

**Change to (replace with your VPS IP from A6):**
```
VITE_API_URL=http://123.45.67.89:8000
```

**Save the file!**

### B2: Clear npm Cache (if needed)

```powershell
cd e:\Renko\frontend
npm cache clean --force
```

### B3: Start Frontend

```powershell
cd e:\Renko\frontend
npm run dev
```

**You should see:**
```
  ➜  Local:   http://localhost:5173/
```

### B4: Open Browser

Navigate to:
```
http://localhost:5173
```

---

## ✅ Part C: Verification

### C1: Test from Laptop (PowerShell)

```powershell
curl http://123.45.67.89:8000/health
```

**Expected response:**
```json
{
  "status": "ok",
  "active": false,
  "mt5_connected": true,
  "total_accounts": 1,
  "connected_accounts": [101510620]
}
```

✅ If you see `mt5_connected: true` - SUCCESS!

### C2: Test Dashboard

**In browser at:** `http://localhost:5173`

You should see:
- [ ] **Accounts Panel** showing your MT5 account
- [ ] **Available Tickers** with symbols (XAUUSD, EURUSD, etc.)
- [ ] **Bid/Ask prices** showing actual numbers (not `---`)
- [ ] **Watchlist** section

### C3: Add Symbol to Watchlist

1. Find **XAUUSD** in "Available Tickers"
2. Click **"Add"** button
3. It should appear in **"Watchlist"** section

✅ If this works, system is connected!

### C4: Start Bot Test

1. Click **"Start Bot"** button
2. Check logs at bottom show activity
3. Check VPS backend logs (should show messages)

---

## 🎉 You're Done!

If all checks passed, you now have:

| Component | Location | Status |
|-----------|----------|--------|
| Backend | VPS (running) | ✅ |
| MT5 | VPS (connected) | ✅ |
| Frontend | Laptop (running) | ✅ |
| Database | Supabase (cloud) | ✅ |
| Network | Connected | ✅ |

---

## 🔧 Keeping It Running

### Daily Operation

1. **Start VPS Backend** (every time you use it):
   ```powershell
   # On VPS:
   cd Renko
   .venv\Scripts\activate
   python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
   ```

2. **Start Frontend** (on your laptop):
   ```powershell
   cd e:\Renko\frontend
   npm run dev
   ```

3. **Keep MT5 running** on VPS

4. **Open dashboard**: `http://localhost:5173`

### Auto-Start on VPS (Optional)

To run backend automatically on VPS restart, see [VPS_BACKEND_SETUP.md](./VPS_BACKEND_SETUP.md#step-5-setup-auto-start-with-supervisor-windows)

---

## 🆘 Troubleshooting

### "Cannot reach backend from laptop"

```powershell
# Test:
ping 123.45.67.89
curl http://123.45.67.89:8000/health
```

If ping works but curl fails:
- Check port 8000 is open on VPS firewall
- Restart backend on VPS

### "Dashboard shows no data"

1. Refresh browser (Ctrl+F5)
2. Check browser console (F12)
3. Look for error messages
4. Verify backend is running: `curl http://123.45.67.89:8000/health`

### "Prices show ---"

1. Verify MT5 is running on VPS
2. Check symbols in MT5 Market Watch
3. Restart backend
4. Refresh browser

### "Can't place trades"

Check MT5 on VPS:
1. Is account logged in?
2. Any error messages?
3. Try adding a symbol to Market Watch
4. Try checking account balance

---

## 📋 Final Checklist

Before declaring success:

- [ ] VPS IP noted: `___________________`
- [ ] Backend running on VPS with "Connected account"
- [ ] Port 8000 firewall rule created
- [ ] Frontend `.env` updated with VPS IP
- [ ] Frontend running at `http://localhost:5173`
- [ ] Health check returns `mt5_connected: true`
- [ ] Dashboard shows accounts and symbols
- [ ] Can see bid/ask prices
- [ ] Can add symbols to watchlist

---

## 📚 Additional Docs

- [VPS_BACKEND_SETUP.md](./VPS_BACKEND_SETUP.md) - Detailed VPS guide
- [CONFIGURE_FRONTEND_FOR_VPS.md](./CONFIGURE_FRONTEND_FOR_VPS.md) - Frontend config details
- [TROUBLESHOOT_BID_ASK.md](./TROUBLESHOOT_BID_ASK.md) - Troubleshooting guide
- [QUICK_VPS_REFERENCE.md](./QUICK_VPS_REFERENCE.md) - Quick reference card

---

**You've got this! Follow the steps and you'll have it running.** ✅

**Next step: Start with Part A - Upload code to VPS!**
