# IMPLEMENTATION ACTION PLAN

## Overview

This document lists all changes needed to make your app fully functional with all required features.

---

## BACKEND: NEW ENDPOINTS TO ADD

### ✅ ALREADY EXISTS
```
POST /start-bot                 - Start bot
POST /stop-bot                  - Stop bot
POST /accounts                  - Add account
GET /accounts                   - Get accounts
GET /trades                     - Get trades
GET /logs                       - Get logs
GET /signal/{symbol}/{price}    - Get signal
POST /reset-signal/{symbol}     - Reset signal
```

### ❌ NEEDS TO BE ADDED

#### A. Ticker Management Endpoints
```
GET /tickers 
  Response: [
    { id: 1, symbol: 'XAUUSD', description: 'Gold vs USD', pip_value: 0.01, is_active: true },
    ...
  ]
  
GET /tickers/{symbol}/quote
  Response: {
    symbol: 'XAUUSD',
    bid: 2050.45,
    ask: 2050.55,
    last_update: '2024-01-15T10:30:45Z'
  }
```

#### B. Watchlist Endpoints
```
POST /watchlist
  Body: {
    account_id: 12345,
    symbol: 'XAUUSD',
    lot_size: 0.01,
    stop_loss_pips: 50,
    take_profit_pips: 100,
    trailing_stop_pips: 30,
    use_trailing_stop: false,
    brick_size: 1.0,
    algo_enabled: true,
    is_active: true
  }
  Response: { id: 1, message: 'Added to watchlist' }

GET /watchlist?account_id=12345
  Response: [
    {
      id: 1,
      account_id: 12345,
      symbol: 'XAUUSD',
      is_active: true,
      lot_size: 0.01,
      stop_loss_pips: 50,
      take_profit_pips: 100,
      trailing_stop_pips: 30,
      use_trailing_stop: false,
      brick_size: 1.0,
      algo_enabled: true
    }
  ]

GET /watchlist/{id}
  Response: { ... single watchlist entry ... }

PUT /watchlist/{id}
  Body: { stop_loss_pips: 60, take_profit_pips: 120, ... }
  Response: { id: 1, message: 'Updated' }

DELETE /watchlist/{id}
  Response: { message: 'Removed from watchlist' }
```

#### C. Algorithm Control Endpoints
```
POST /algo/toggle/{symbol}
  Body: { account_id: 12345, enabled: true|false }
  Response: { symbol: 'XAUUSD', algo_enabled: true }

GET /algo/status/{symbol}?account_id=12345
  Response: { symbol: 'XAUUSD', algo_enabled: true, last_signal: 'BUY', last_signal_time: '...' }
```

#### D. Market Data Endpoints
```
GET /market/quote/{symbol}
  Response: { symbol: 'XAUUSD', bid: 2050.45, ask: 2050.55, bid_size: 100, ask_size: 100 }

GET /market/symbols
  Response: [ 'XAUUSD', 'EURUSD', 'GBPUSD', ... ]
```

---

## FRONTEND: NEW COMPONENTS TO CREATE

### ✅ ALREADY EXISTS
```
AccountsPanel.tsx     - Show accounts
TradeDashboard.tsx    - Show trades
Controls.tsx          - Start/Stop, Brick Size
LogsViewer.tsx        - Show logs
App.tsx               - Main app
```

### ❌ NEEDS TO BE CREATED/ENHANCED

#### 1. TickersPanel Component
```tsx
// Shows all available tickers with live bid/ask
// Location: src/components/TickersPanel.tsx

Features:
- Display list of available symbols
- Show live bid/ask prices (update every 1-2 seconds)
- Show pip change (color coded green/red)
- Click to add symbol to watchlist
- Search/filter symbols
```

#### 2. WatchlistManager Component
```tsx
// Location: src/components/WatchlistManager.tsx

Features:
- Show all symbols in watchlist
- For each symbol show:
  - Symbol name
  - Lot size
  - Stop Loss (SL) value
  - Take Profit (TP) value
  - Trailing Stop value
  - Brick Size
  - Algo On/Off toggle
  - Delete button
- Add/Remove symbols
- Edit each parameter
```

#### 3. SymbolControlPanel Component
```tsx
// Location: src/components/SymbolControlPanel.tsx

Features:
- For EACH ticker in watchlist:
  - Symbol name
  - Current bid/ask price
  - Algo toggle (ON/OFF button)
  - Stop Loss slider (or input)
  - Take Profit slider (or input)
  - Trailing Stop slider (or input)
  - Brick Size input
  - Save button
```

#### 4. LivePositions Component
```tsx
// Location: src/components/LivePositions.tsx

Features:
- Show only OPEN positions
- For each position:
  - Symbol
  - Entry price
  - Current bid/ask
  - Profit/Loss in points
  - Profit/Loss in %
  - SL price
  - TP price
  - Time in trade
  - Quick close button (optional)
```

#### 5. Enhanced App.tsx
```tsx
// Update main app layout to include new components

Layout:
├── Header (title, refresh status)
├── MarketDataPanel (live quotes for top symbols)
├── SymbolControlPanel (per-symbol controls)
├── LivePositions (currently open positions)
├── TradeDashboard (trade history)
├── AccountsPanel (account info)
├── LogsViewer (recent events)
└── Controls (global start/stop)
```

---

## BACKEND: CODE CHANGES NEEDED

### 1. Update worker.py
```python
Changes:
- Add per-symbol algo_enabled check
- Implement trailing stop monitoring
- Log trade entry details (SL, TP, Trail)
- Add position monitoring loop for SL/TP hits
```

### 2. Update execution/trade.py
```python
Changes:
- Update place_buy() to accept: sl_price, tp_price, trail_sl_pips
- Update place_sell() to accept: sl_price, tp_price, trail_sl_pips
- Implement real MT5 order with SL/TP parameters
- Add trailing stop tracking

Current signature:
  place_buy(session, symbol, price)
New signature:
  place_buy(session, symbol, price, sl_pips, tp_pips, trail_pips=0, lot_size=0.01)
```

### 3. Create new endpoints file: backend/api/endpoints.py
```python
New endpoints:
- GET /tickers
- GET /tickers/{symbol}/quote
- POST /watchlist
- GET /watchlist
- GET /watchlist/{id}
- PUT /watchlist/{id}
- DELETE /watchlist/{id}
- POST /algo/toggle/{symbol}
- GET /algo/status/{symbol}
- GET /market/quote/{symbol}
- GET /market/symbols
- PUT /settings/{setting_key} (optional)
```

### 4. Create price_manager.py
```python
New module: backend/mt5/price_manager.py

Features:
- Get current bid/ask for symbol
- Get quote history
- Update price_ticks table in Supabase
- Real-time price streaming (if supported)
```

### 5. Create watchlist_manager.py
```python
New module: backend/services/watchlist_manager.py

Features:
- CRUD operations for watchlist
- Validate parameters (SL, TP, brick size)
- Get watchlist for account
- Toggle algo per symbol
```

---

## DATABASE CHANGES

### Schema Already Created ✓
- accounts
- watchlist (with all new fields)
- trades (with SL/TP fields)
- logs
- bot_control
- settings
- available_symbols
- price_ticks

### Migration Notes
- Run `/backend/supabase/schema.sql` on your Supabase project
- Creates all necessary tables and indexes
- No changes to existing tables (backwards compatible)

---

## FRONTEND: TYPE DEFINITIONS TO ADD

```tsx
// src/types/api.ts

type Ticker = {
  id: number;
  symbol: string;
  description: string;
  pip_value: number;
  is_active: boolean;
};

type Quote = {
  symbol: string;
  bid: number;
  ask: number;
  last_update: string;
};

type WatchlistItem = {
  id: number;
  account_id: number;
  symbol: string;
  is_active: boolean;
  lot_size: number;
  stop_loss_pips: number;
  take_profit_pips: number;
  trailing_stop_pips: number;
  use_trailing_stop: boolean;
  brick_size: number;
  algo_enabled: boolean;
};

type Position = {
  id: number;
  account_id: number;
  symbol: string;
  type: 'buy' | 'sell';
  lot: number;
  entry_price: number;
  entry_time: string;
  sl_price?: number;
  tp_price?: number;
  current_profit?: number;
};
```

---

## API SERVICE UPDATES

```tsx
// src/services/api.ts - Add new functions

export const getAvailableTickers = () => request('/tickers');
export const getQuote = (symbol: string) => request(`/tickers/${symbol}/quote`);
export const addToWatchlist = (data: Watchlist) => request('/watchlist', { method: 'POST', body: JSON.stringify(data) });
export const getWatchlist = (accountId: number) => request(`/watchlist?account_id=${accountId}`);
export const updateWatchlistItem = (id: number, data: Partial<Watchlist>) => request(`/watchlist/${id}`, { method: 'PUT', body: JSON.stringify(data) });
export const removeFromWatchlist = (id: number) => request(`/watchlist/${id}`, { method: 'DELETE' });
export const toggleAlgo = (symbol: string, accountId: number, enabled: boolean) => request(`/algo/toggle/${symbol}`, { method: 'POST', body: JSON.stringify({ account_id: accountId, enabled }) });
export const getAlgoStatus = (symbol: string, accountId: number) => request(`/algo/status/${symbol}?account_id=${accountId}`);
```

---

## PRIORITY ORDER (Phase-based Implementation)

### Phase 0: Foundation (DONE ✓)
- ✓ Database schema created
- ✓ .env.example created
- ✓ Code review completed

### Phase 1: Backend Endpoints (NEXT)
- [ ] Update execution/trade.py with SL/TP/Trail
- [ ] Create watchlist_manager.py
- [ ] Create endpoints.py with all new endpoints
- [ ] Create price_manager.py for live quotes
- [ ] Update worker.py for per-symbol algo control
- [ ] Add trailing stop monitoring

Estimated time: 4-6 hours

### Phase 2: Frontend Components (THEN)
- [ ] Create TickersPanel.tsx
- [ ] Create WatchlistManager.tsx  
- [ ] Create SymbolControlPanel.tsx
- [ ] Create LivePositions.tsx
- [ ] Update App.tsx layout
- [ ] Add type definitions
- [ ] Update API services

Estimated time: 6-8 hours

### Phase 3: Testing & Deployment (FINALLY)
- [ ] Test all endpoints
- [ ] Test frontend components
- [ ] VPS deployment
- [ ] Live trading test
- [ ] Monitoring setup

Estimated time: 3-4 hours

### Total Estimate: 13-18 hours of development

---

## Implementation Notes

### Backend Priority
1. **Critical**: Trade execution (SL/TP/Trail) - affects real trades
2. **Critical**: Watchlist management - needed for UI
3. **Important**: Price manager - for bid/ask display
4. **Nice-to-have**: Algorithm toggle - can default to on

### Frontend Priority
1. **Critical**: WatchlistManager - to manage symbols
2. **Critical**: TickersPanel - to add symbols
3. **Important**: SymbolControlPanel - to set parameters
4. **Important**: LivePositions - to see current trades
5. **Nice-to-have**: Enhanced Controls - better UX

### Testing Strategy
1. Test each backend endpoint individually with Postman
2. Test frontend components in isolation
3. Integration test: UI → API → MT5
4. Test on VPS before live trading

---

## Files to Modify

```
backend/
├── main.py                          (add CORS, import endpoints)
├── worker.py                        (per-symbol algo control)
├── execution/
│   └── trade.py                     (SL/TP/Trail support)
├── mt5/
│   └── price_manager.py             (NEW - get quotes)
├── services/
│   └── watchlist_manager.py         (NEW - watchlist CRUD)
└── api/
    └── endpoints.py                 (NEW - all endpoints)

frontend/
├── src/
│   ├── App.tsx                      (update layout)
│   ├── types/
│   │   └── api.ts                   (NEW - type definitions)
│   ├── services/
│   │   └── api.ts                   (add new functions)
│   └── components/
│       ├── TickersPanel.tsx         (NEW)
│       ├── WatchlistManager.tsx     (NEW)
│       ├── SymbolControlPanel.tsx   (NEW)
│       ├── LivePositions.tsx        (NEW)
│       └── Controls.tsx             (update)

root/
├── CODE_REVIEW_AND_REQUIREMENTS.md  (DONE ✓)
├── INFORMATION_CHECKLIST.md         (DONE ✓)
├── VPS_DEPLOYMENT_GUIDE.md          (DONE ✓)
├── IMPLEMENTATION_ACTION_PLAN.md    (this file)
├── .env.example                     (DONE ✓)
└── backend/supabase/schema.sql      (DONE ✓)
```

---

## Next Action

1. **You**: Fill out INFORMATION_CHECKLIST.md with your specific values
2. **You**: Create Supabase account (if needed) and run schema.sql
3. **Me**: Create all backend endpoints
4. **Me**: Create all frontend components
5. **You**: Deploy to VPS following VPS_DEPLOYMENT_GUIDE.md
6. **You**: Test and go live!

