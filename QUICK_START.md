# 🚀 Quick Start Reference

## 30-Second Setup

### Terminal 1: Backend

```bash
cd e:\Renko
.venv\Scripts\activate
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### Terminal 2: Frontend

```bash
cd e:\Renko\frontend
npm run dev
```

### Browser

Open: `http://localhost:5173`

---

## Key URLs & Endpoints

| What | URL |
|------|-----|
| Dashboard | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| Health Check | http://localhost:8000/health |
| Swagger Docs | http://localhost:8000/docs |
| Redoc Docs | http://localhost:8000/redoc |

---

## Essential API Endpoints

```bash
# Get all accounts
curl http://localhost:8000/api/accounts

# Add account
curl -X POST http://localhost:8000/api/accounts \
  -H "Content-Type: application/json" \
  -d '{
    "login": 101510620,
    "password": "RichAnshu@1987",
    "server": "XMGlobal-MT5 5"
  }'

# Get available symbols
curl http://localhost:8000/api/tickers

# Add to watchlist
curl -X POST http://localhost:8000/api/watchlist \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": 101510620,
    "symbol": "XAUUSD",
    "lot_size": 0.01,
    "brick_size": 1.0,
    "algo_enabled": true
  }'

# Get signal
curl http://localhost:8000/signal/XAUUSD/2050.45

# Start bot
curl -X POST http://localhost:8000/start-bot

# Stop bot
curl -X POST http://localhost:8000/stop-bot

# Get health status
curl http://localhost:8000/health
```

---

## Important Documents

| Document | Purpose |
|----------|---------|
| [TESTING_SETUP.md](./TESTING_SETUP.md) | Complete step-by-step testing guide |
| [CREDENTIALS_AND_TESTING.md](./CREDENTIALS_AND_TESTING.md) | Credentials checklist & troubleshooting |
| [VPS_DEPLOYMENT_GUIDE.md](./VPS_DEPLOYMENT_GUIDE.md) | Deploy to production server |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | System architecture & design |
| [DELIVERABLES.md](./DELIVERABLES.md) | Full API documentation |

---

## Prerequisites Check

```bash
# Python 3.11+
python --version

# Node.js 18+
node --version

# Dependencies installed
pip install -r requirements.txt

# Verify setup
python verify_setup.py
```

---

## Your Credentials (in `.env`)

```
MT5_LOGIN=101510620
MT5_PASSWORD=RichAnshu@1987
MT5_SERVER=XMGlobal-MT5 5
MT5_PATH=C:\Program Files\XM Global MT5\terminal64.exe

SUPABASE_URL=https://mflakcwgbpghyzdyevsb.supabase.co
SUPABASE_KEY=eyJhbGci...
```

---

## File Structure

```
Renko/
├── backend/
│   ├── api/          # REST API routes
│   ├── mt5/          # MT5 connection
│   ├── renko/        # Renko engine
│   ├── signals.py    # Signal generation
│   ├── worker.py     # Bot worker loop
│   └── main.py       # FastAPI app
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   └── services/     # API service
│   └── package.json
├── requirements.txt   # Python dependencies
├── .env              # Configuration (contains credentials)
└── TESTING_SETUP.md  # This guide
```

---

## Troubleshooting

**Backend won't start?**
```bash
# Check .env is correct
cat .env

# Check port is free
netstat -ano | findstr :8000

# Try different port
uvicorn backend.main:app --port 8001
```

**Frontend won't start?**
```bash
# Check Node is installed
node --version

# Clear npm cache
npm cache clean --force

# Reinstall
cd frontend
rm -r node_modules package-lock.json
npm install
```

**Can't connect to Supabase?**
```bash
# Test directly
python -c "from backend.supabase.client import supabase_client; print('OK')"

# Check internet
ping supbase.com
```

**MT5 connection fails?**
```bash
# Verify path
dir "C:\Program Files\XM Global MT5\terminal64.exe"

# Test MT5 login manually in the app
```

---

## Next Steps

1. ✅ Run verification: `python verify_setup.py`
2. ✅ Start backend
3. ✅ Start frontend
4. ✅ Open dashboard
5. ✅ Add MT5 account
6. ✅ Add symbols to watchlist
7. ✅ Start the bot
8. ✅ Monitor trades

Ready? Let's go! 🚀
