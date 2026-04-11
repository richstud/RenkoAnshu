# Multi-Account Auto-Trading Setup

## Overview
The auto-trader now supports trading on **multiple accounts simultaneously** with dynamic lot sizing based on account balance.

## How It Works

### 1. **Multiple Account Support**
The auto-trader now:
- Reads ALL symbols from the watchlist table where `algo_enabled=true`
- Monitors each symbol **per account** (using format: `{account_id}_{symbol}`)
- Executes trades on the **correct account** for each symbol

### 2. **Dynamic Lot Sizing by Account Balance**
Lot size is automatically calculated based on the account's current balance:

```
Balance ≤ $1,000    →  Lot Size: 0.01
Balance $1,001-$10,000   →  Lot Size: 0.1
Balance $10,001-$25,000  →  Lot Size: 1.0
Balance > $25,000   →  Lot Size: 1.0 (maximum)
```

### 3. **Setup Instructions**

#### Step 1: Add All Accounts to Backend
Make sure your backend is connected to all 3 MT5 accounts. They should be in Supabase `accounts` table:

```sql
SELECT login, server, status FROM accounts;
```

Expected output:
```
login       | server  | status
101510620   | ICMarkets | active
[account2]  | ICMarkets | active
[account3]  | ICMarkets | active
```

#### Step 2: Add Watchlist Entries for Each Account

For **Account 1** (101510620) - Add BTCUSD:
- Account ID: 101510620
- Symbol: BTCUSD
- Brick Size: 1
- algo_enabled: true

For **Account 2** - Add BTCUSD:
- Account ID: [account2_id]
- Symbol: BTCUSD
- Brick Size: 1
- algo_enabled: true

For **Account 3** - Add BTCUSD:
- Account ID: [account3_id]
- Symbol: BTCUSD
- Brick Size: 1
- algo_enabled: true

**Example Supabase Query:**
```sql
INSERT INTO watchlist (account_id, symbol, brick_size, algo_enabled, stop_loss_pips, take_profit_pips) 
VALUES 
  (101510620, 'BTCUSD', 1.0, true, 50, 100),
  (account2_id, 'BTCUSD', 1.0, true, 50, 100),
  (account3_id, 'BTCUSD', 1.0, true, 50, 100);
```

#### Step 3: Restart Backend

```bash
pkill -f "python -m backend.main"
python -m backend.main &
tail -50 backend.log
```

### 4. **Verification**

Check the logs to see all accounts and symbols being loaded:

```
📋 Loaded 3 symbol/account pairs from watchlist
   Account 101510620: BTCUSD
   Account 123456789: BTCUSD
   Account 987654321: BTCUSD
```

When a signal is detected, you'll see:

```
📊 Signal detected for BTCUSD: green → red
🎯 Executing SELL for BTCUSD on account 101510620...
💰 Account 101510620 balance: $9991.98, Calculated lot size: 0.1

🎯 Executing SELL for BTCUSD on account 123456789...
💰 Account 123456789 balance: $5500.00, Calculated lot size: 0.1

🎯 Executing SELL for BTCUSD on account 987654321...
💰 Account 987654321 balance: $20000.00, Calculated lot size: 1.0
```

### 5. **Code Changes Made**

**File: `backend/services/auto_trader.py`**

#### New Function: `calculate_lot_size(balance)`
```python
def calculate_lot_size(self, balance: float) -> float:
    """Calculate lot size based on account balance"""
    if balance <= 1000:
        return 0.01
    elif balance <= 10000:
        return 0.1
    else:
        return 1.0
```

#### Updated: `load_watchlist()`
- Changed to load ALL symbols from ALL accounts
- Uses key format: `{account_id}_{symbol}` for unique tracking
- Groups symbols by account for logging

#### Updated: `execute_trade()`
- Now uses `calculate_lot_size(balance)` instead of static lot size
- Logs which account is being traded

### 6. **Example Scenario**

3 accounts, all with BTCUSD enabled:

```
Account 1 (Balance: $9,000)   → Lot size: 0.1
Account 2 (Balance: $500)     → Lot size: 0.01
Account 3 (Balance: $18,000)  → Lot size: 1.0
```

When BTCUSD goes from green to red (SELL signal):
- **Account 1** sells 0.1 lot
- **Account 2** sells 0.01 lot
- **Account 3** sells 1.0 lot

All at the same time, automatically! ✅

### 7. **Monitoring**

Check which accounts have active symbols:

```bash
curl http://your-vps:8000/api/auto-trading/status
```

Should show all accounts and their enabled symbols:
```json
{
  "service": {
    "running": true,
    "enabled_symbols": ["BTCUSD"],
    "symbol_count": 3,
    "accounts": [101510620, 123456789, 987654321]
  }
}
```

---

## Troubleshooting

### Q: Trades only executing on one account?
**A:** Check that all 3 accounts are added to the `accounts` table in Supabase and are connected.

### Q: Different lot sizes than expected?
**A:** Verify the account balances. Lot size is calculated dynamically from current balance, not from watchlist entry.

### Q: Symbol not trading on Account 2?
**A:** Make sure the watchlist entry exists for Account 2 with `algo_enabled=true`.

---

## What's Next?

1. Push changes to GitHub
2. Pull on VPS
3. Restart backend
4. Monitor logs for all 3 accounts executing trades
5. Verify trades on all accounts in MT5 terminal
