# RENKO Reversal Gold Algo Trading System

## Overview

Production-grade algorithmic trading bot for XAUUSD (GOLD) with:
- XM / MetaTrader 5 connection
- Renko reversal strategy
- Multi-account support
- FastAPI backend
- Supabase persistence & realtime
- React + Tailwind dashboard

## Features

- Renko-based reversal logic (always 1 position active)
- Balance-based lot sizing
- Multi-account session manager
- FastAPI endpoints: /start-bot, /stop-bot, /accounts, /trades, /updates-settings, /logs
- Supabase tables: accounts, trades, logs, settings

## Setup

### 1. Backend

1. Python 3.11+
2. Create venv:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

3. Create `.env` from `.env.example` and fill in values.
4. Setup Supabase schema (via SQL script):

```bash
psql "postgres://..." -f backend/supabase/schema.sql
```

5. Run app:

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Frontend

1. Node 18+
2. Install dependencies and run:

```bash
cd frontend
npm install
npm run dev
```

3. Set `VITE_API_URL` in `frontend/.env` if needed.

## Supabase Tables

- `accounts`: account credentials + status
- `trades`: executed trades
- `logs`: events + latency
- `settings`: brick size + bot status

## Strategy

1. Green brick => close short + open buy at brick high
2. Red brick => close buy + open sell at brick low
3. Each account processes ticks and reverses positions

## Signal Generation

The system uses a unified signal generation interface via the `signals` module:

```python
from backend.signals import get_signal

# Get trading signal for a symbol at a given price
signal = get_signal('XAUUSD', 2350.50)  # Returns 'BUY', 'SELL', or None
```

Signals are generated based on Renko brick formations:
- **BUY**: Green brick formed (uptrend)
- **SELL**: Red brick formed (downtrend)
- **None**: No complete brick yet, or same direction as current position

## Lot sizing

- balance < 500 => 0.01
- 500 <= balance <= 1000 => 0.5
- balance > 1000 => 1.0

## API

- POST `/start-bot`
- POST `/stop-bot`
- GET `/signal/{symbol}/{price}` - Get trading signal for a symbol at a given price
- POST `/reset-signal/{symbol}` - Reset signal generator for a symbol
- POST `/accounts` { login, password, server }
- GET `/accounts`
- GET `/trades`
- GET `/logs`
- POST `/update-settings` { brick_size, bot_status }

## Notes

- Ensure MT5 terminal is running and connected to XM server.
- For production use, increase error handling, secure credentials and add history reconciliation.
