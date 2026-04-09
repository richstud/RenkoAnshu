# 🚀 VPS Deployment - Quick Reference Card

## In 5 Minutes

### What You Need
- [ ] VPS IP address (e.g., `123.45.67.89`)
- [ ] Renko folder on VPS
- [ ] MT5 running on VPS
- [ ] `.env` file on VPS with credentials

---

## On VPS (3 Commands)

**Open PowerShell on VPS, then:**

```powershell
# 1. Navigate to project
cd C:\path\to\Renko

# 2. Install everything (one time)
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# 3. Start backend
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

✅ Backend is now running on VPS!

---

## On Your Laptop (3 Steps)

### Step 1: Update Frontend Config

**Edit:** `e:\Renko\frontend\.env`

```
VITE_API_URL=http://123.45.67.89:8000
```
(Replace IP with your VPS IP)

### Step 2: Start Frontend

```powershell
cd e:\Renko\frontend
npm run dev
```

### Step 3: Open Browser

```
http://localhost:5173
```

✅ Dashboard now connects to VPS backend!

---

## Verify It Works

**In PowerShell on laptop:**

```powershell
# Should show:
# {"status":"ok","mt5_connected":true,"connected_accounts":[101510620]}

curl http://123.45.67.89:8000/health
```

---

## Diagram

```
LAPTOP (Local)           VPS (Remote)         CLOUD
┌──────────────┐        ┌──────────────┐     ┌──────────────┐
│  Frontend    │───────→│  Backend     │────→│ Supabase     │
│ localhost:   │        │ 0.0.0.0:     │     │ (Database)   │
│ 5173         │        │ 8000         │     │              │
│              │        │              │     │              │
│              │        │  + MT5       │     │              │
└──────────────┘        └──────────────┘     └──────────────┘
Your Computer           Your Server         Your Database
```

---

## Common Commands

| What | Command |
|------|---------|
| Get VPS IP | `ipconfig` (on VPS) |
| Test backend | `curl http://<IP>:8000/health` |
| View prices | `curl http://<IP>:8000/api/tickers` |
| Check issues | `curl http://<IP>:8000/diagnose` |
| View logs | Check PowerShell window where backend is running |

---

## If Something's Wrong

| Issue | Check |
|-------|-------|
| Can't reach VPS | `ping <VPS_IP>` |
| Backend won't start | Check Python: `python --version` |
| Prices show `---` | Restart backend, verify MT5 is running |
| Dashboard empty | Check browser console (F12) |
| Trades not executing | Check MT5 balance, verify symbols in Market Watch |

---

## Files Reference

```
Renko/
├── .env                              ← Backend config (ON VPS)
├── backend/main.py                   ← Backend app
├── requirements.txt                  ← Dependencies
│
├── frontend/
│   ├── .env                          ← Frontend config (ON LAPTOP)
│   └── src/
│       └── services/api.ts           ← Connects to backend
│
└── VPS_BACKEND_SETUP.md              ← Detailed guide
```

---

## One-Liner Deploy (for VPS)

Copy entire project to VPS, then run:

```powershell
cd Renko && python -m venv .venv && .venv\Scripts\activate.bat && pip install -r requirements.txt && python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

---

## Keep This Handy

| Step | Action | Done |
|------|--------|------|
| 1 | Get VPS IP address | [ ] |
| 2 | Start backend on VPS | [ ] |
| 3 | Update `frontend/.env` | [ ] |
| 4 | Start frontend on laptop | [ ] |
| 5 | Open `http://localhost:5173` | [ ] |
| 6 | Test: `curl http://<IP>:8000/health` | [ ] |
| 7 | Dashboard shows data ✅ | [ ] |

---

## Need Help?

1. **Backend issues** → See [VPS_BACKEND_SETUP.md](./VPS_BACKEND_SETUP.md)
2. **Frontend connection** → See [CONFIGURE_FRONTEND_FOR_VPS.md](./CONFIGURE_FRONTEND_FOR_VPS.md)
3. **Troubleshooting** → See [TROUBLESHOOT_BID_ASK.md](./TROUBLESHOOT_BID_ASK.md)

---

**That's it! You now have:**
- ✅ Backend on VPS (connected to MT5)
- ✅ Frontend on laptop (easy to use)
- ✅ Database in cloud (always accessible)
- ✅ Trades execute on VPS MT5
- ✅ Works from anywhere 🌍
