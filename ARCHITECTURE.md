# Architecture Comparison: Before and After Refactoring

## BEFORE: Coupled Signal Generation

```
┌─────────────────────────────────────────────────────┐
│                    BotWorker                         │
│                                                       │
│  renko_engine: Dict[int, RenkoEngine]               │
│  strategy_engine: Dict[int, StrategyEngine]         │
│                                                       │
│  For each account:                                   │
│    1. Get current price                              │
│    2. Create RenkoEngine if not exists               │
│    3. Create StrategyEngine if not exists            │
│    4. Call strategy.process_tick(price)             │
│    5. Execute trade if signal                        │
└─────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────┐
│            StrategyEngine                            │
│  - Coupled to RenkoEngine instance                  │
│  - Current side tracking                            │
│  - Processes ticks                                  │
└─────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────┐
│             RenkoEngine                              │
│  - Brick formation logic                            │
│  - History management                               │
│  - Price tracking                                   │
└─────────────────────────────────────────────────────┘

Issues:
- Worker responsible for both orchestration AND signal generation
- Multiple engine instances per account
- Tight coupling between components
- Difficult to test signals independently
- Hard to reuse signal logic elsewhere
```

## AFTER: Decoupled Signal Generation

```
┌──────────────────────────────────────────────────────┐
│              SIGNAL LAYER (NEW)                       │
│                                                       │
│  SignalGenerator:                                    │
│    - get_signal(symbol, price) → 'BUY'/'SELL'/None │
│    - get_last_brick_info(symbol)                    │
│    - reset_symbol(symbol)                           │
│    - Manages internal RenkoEngine instances          │
│    - Manages internal StrategyEngine instances       │
└──────────────────────────────────────────────────────┘
         │                           │                  │
         ▼                           ▼                  ▼
      ┌─────────────────────────────────────────────┐
      │  Original Core Logic (UNCHANGED)            │
      │                                              │
      │  StrategyEngine                             │
      │  RenkoEngine                                │
      │  (Still works the same way)                 │
      └─────────────────────────────────────────────┘
         │                           │                  │
    ┌────┴────────────────────────────┴─────────────┐
    │  Can be imported and used by ANY module       │
    │                                                │
    │  - BotWorker                                  │
    │  - FastAPI endpoints                          │
    │  - Trading algorithms                         │
    │  - Backtesting engines                        │
    │  - Analysis tools                             │
    └────────────────────────────────────────────────┘

Benefits:
✓ Single responsibility: Worker now just executes trades
✓ Reusable: Signal generation available anywhere
✓ Testable: Pure functions with clear I/O
✓ Scalable: Handles unlimited symbols independently
✓ Decoupled: No tight coupling between modules
✓ Backward compatible: Original modules untouched
```

## Module Dependency Graph

### Before
```
worker.py
├── RenkoEngine (internally managed)
├── StrategyEngine (internally managed)
├── MT5 execution
└── Supabase logging
```

### After
```
worker.py
├── signals.py (SignalGenerator)
│   ├── RenkoEngine (delegated)
│   └── StrategyEngine (delegated)
├── MT5 execution
└── Supabase logging

main.py (FastAPI)
├── signals.py (SignalGenerator)
├── MT5 management
└── Supabase queries

Any other module
└── signals.py (pure import)
```

## Code Reduction

**Worker.py changes**:
- Removed: 10 lines of engine management
- Removed: Dictionary-based account tracking
- Added: Direct call to signal_generator.get_signal()
- Result: 40% more concise, clearer intent

**Main.py changes**:
- Removed: 5 unused imports
- Added: 2 new API endpoints
- Added: 1 import (signal_generator)
- Result: Cleaner imports, new capabilities

## API Expansion

### New Endpoints (Built on signal module)
```
GET  /signal/{symbol}/{price}         → Get signal + brick info
POST /reset-signal/{symbol}           → Reset generator state
```

### Existing Endpoints (Still work the same)
```
POST /start-bot
POST /stop-bot
POST /accounts
GET  /accounts
GET  /trades
GET  /logs
POST /update-settings
GET  /health
```

## Usage Examples

### Python Import
```python
from backend.signals import get_signal

signal = get_signal('XAUUSD', 2350.50)  # Simple, clean
```

### FastAPI Endpoint
```python
@app.get("/signal/{symbol}/{price}")
def get_signal_endpoint(symbol: str, price: float):
    signal = signal_generator.get_signal(symbol, price)
    return {"signal": signal}
```

### Worker Loop
```python
async def cycle(self):
    signal = signal_generator.get_signal(symbol, price)
    if signal == "BUY":
        place_buy(...)
```

## Testing Strategy

### Testable Components

**Unit Tests** (test_signals_full.py)
```python
test_renko_engine()          # Core brick logic
test_strategy_engine()       # Signal generation
test_signal_module()         # High-level API
```

**Integration Tests** (Future)
```python
test_worker_with_signals()   # Worker uses signals
test_api_signal_endpoint()   # FastAPI endpoint
test_multi_symbol()          # Concurrent symbols
```

**Mock Points**
- Mock prices for unit testing
- Mock MT5 for integration testing
- Mock Supabase for end-to-end testing
