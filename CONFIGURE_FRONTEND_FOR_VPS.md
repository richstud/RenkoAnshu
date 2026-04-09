# 🔗 Configure Frontend to Connect to VPS Backend

## Quick Setup (3 Steps)

### Step 1: Get Your VPS IP Address

**On VPS (Windows PowerShell):**
```powershell
ipconfig
```

Look for **IPv4 Address** in the public network adapter. Example: `123.45.67.89`

Or check your hosting provider's console for the public IP.

---

### Step 2: Update Frontend Configuration

**On your local laptop**, edit: `e:\Renko\frontend\.env`

**Current (for local testing):**
```
VITE_API_URL=http://localhost:8000
```

**Change to (for VPS):**
```
VITE_API_URL=http://<YOUR_VPS_IP>:8000
```

**Example with real VPS IP:**
```
VITE_API_URL=http://123.45.67.89:8000
```

---

### Step 3: Restart Frontend

**On laptop:**
```powershell
cd e:\Renko\frontend

# Ctrl+C to stop if running

# Restart
npm run dev
```

**Open browser:**
```
http://localhost:5173
```

---

## ✅ Verify Connection Works

### Test 1: Health Check

In PowerShell on your **laptop**:
```powershell
curl http://<YOUR_VPS_IP>:8000/health
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

---

### Test 2: Get Tickers

```powershell
curl http://<YOUR_VPS_IP>:8000/api/tickers
```

**Expected:** List of available symbols

---

### Test 3: Dashboard Check

**In browser at:** `http://localhost:5173`

You should see:
- ✅ Accounts loaded from VPS
- ✅ Bid/Ask prices (from VPS MT5)
- ✅ Available symbols
- ✅ Can add to watchlist
- ✅ Can start/stop bot on VPS

---

## 🔧 Troubleshooting

### Issue: "Cannot reach VPS backend"

**Check VPS IP is accessible:**
```powershell
ping <YOUR_VPS_IP>
```

If that works, check backend is running:
```powershell
curl http://<YOUR_VPS_IP>:8000/health
```

If that fails:
1. SSH into VPS and restart backend
2. Check port 8000 is open in firewall:
   ```powershell
   # On VPS:
   netstat -ano | findstr 8000
   ```
3. If not visible, open firewall:
   ```powershell
   # On VPS (Administrator):
   netsh advfirewall firewall add rule name="Allow port 8000" dir=in action=allow protocol=tcp localport=8000
   ```

---

### Issue: "Dashboard loads but shows empty"

**Check browser console (F12):**

1. Open DevTools: Press **F12**
2. Go to **Network** tab
3. Refresh page
4. Look for API calls to `/api/accounts`, `/api/tickers`
5. Check response status (should be 200, not 404 or CORS error)

**If you see CORS errors:**

The backend needs to allow your frontend domain. Currently it allows all (`*`).

**Check backend logs (on VPS):**
```
curl http://<VPS_IP>:8000/diagnose
```

---

### Issue: "Prices showing --- instead of numbers"

**Check MT5 on VPS:**
1. SSH into VPS
2. Verify MT5 terminal is running
3. Check symbols are in Market Watch
4. Restart backend once

---

## 📝 Configuration Files

### Frontend Config: `.env`

**Location:** `e:\Renko\frontend\.env`

```
# Backend URL (remotely on VPS)
VITE_API_URL=http://123.45.67.89:8000

# Other settings (optional)
NODE_ENV=development
```

### Backend Config: `.env` (on VPS)

**Location:** `C:\Users\YourUser\Desktop\Renko\.env` (or wherever on VPS)

```
# Supabase (same for both local and VPS)
SUPABASE_URL=https://mflakcwgbpghyzdyevsb.supabase.co
SUPABASE_KEY=eyJhbGci...

# MT5 (runs on VPS)
MT5_PATH=C:\Program Files\MetaTrader 5\terminal64.exe
MT5_LOGIN=101510620
MT5_PASSWORD=RichAnshu@1987
MT5_SERVER=XMGlobal-MT5 5

# Server
API_HOST=0.0.0.0
API_PORT=8000
```

---

## 🌐 Network Communication Flow

```
Your Laptop Browser
    ↓ (http://localhost:5173)
React Frontend
    ↓ (http://<VPS_IP>:8000)
VPS Backend
    ↓ (Local MT5 connection)
VPS MT5 Terminal
    ↓ (WebSocket)
Supabase Cloud Database
```

Each layer is independent:
- Frontend can run anywhere (laptop, server, etc.)
- Backend must run where MT5 is (your VPS)
- Database is always in cloud (Supabase)

---

## ✅ Deployment Checklist

- [ ] VPS IP address determined
- [ ] Backend running on VPS: `python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000`
- [ ] Port 8000 open in VPS firewall
- [ ] MT5 running and logged in on VPS
- [ ] `frontend/.env` updated with VPS IP
- [ ] Frontend restarted: `npm run dev`
- [ ] Health check works: `curl http://<VPS_IP>:8000/health`
- [ ] Dashboard loads at `http://localhost:5173`
- [ ] Prices display (not `---`)
- [ ] Can add to watchlist
- [ ] Can start/stop bot

---

## 📞 Common Questions

### Q: Can I run both backend and frontend on VPS?
**A:** Yes, but not recommended. Frontend on VPS needs Node.js and npm. Better to keep frontend on your laptop or separate web server.

### Q: Will trades execute on VPS MT5?
**A:** Yes! The backend connects to local MT5 on VPS and executes trades there.

### Q: Is my data secure?
**A:** Supabase handles data security. Communication to VPS is standard HTTP (add HTTPS for production).

### Q: What if VPS restarts?
**A:** Backend needs to be restarted. Use NSSM or Supervisor for auto-restart (see VPS_BACKEND_SETUP.md).

### Q: Can I trade from multiple laptops?
**A:** Yes! Any browser can connect to VPS backend as long as port 8000 is accessible.

---

## 🚀 Next Steps

1. **Note your VPS IP address**
2. **Update `frontend/.env` with VPS IP**
3. **Restart frontend**: `npm run dev`
4. **Test dashboard**: http://localhost:5173
5. **Start trading!**

Questions? Check [VPS_BACKEND_SETUP.md](./VPS_BACKEND_SETUP.md) for detailed setup instructions.
