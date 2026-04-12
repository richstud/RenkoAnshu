# MT5 Connection Retry Logic Fix

## Problem
The backend was experiencing repeated `MT5 initialize failed: (-10005, 'IPC timeout')` errors when attempting to connect to MetaTrader5 accounts during startup. The original retry logic was minimal and didn't handle timeouts effectively.

## Root Cause
- IPC timeouts occur when MT5 terminal is not running or not responding
- Original code only retried 3 times with fixed 2-second delays
- No special handling for IPC timeout errors
- No terminal responsiveness checks before retries

## Solution

### 1. Enhanced Connection Retry Logic (`backend/mt5/connection.py`)

**AccountSession.connect()** improvements:
- **Exponential backoff**: Delays increase exponentially (1s → 2s → 4s → 8s → 10s max)
- **IPC timeout handling**: Specifically detects and handles IPC timeouts with longer waits
- **Terminal checks**: Validates MT5 terminal is responding before retry attempts
- **Max retries configurable**: Default 5 retries per account (previously 3)
- **Better logging**: Clear indication of attempt numbers and reasons for retries

```python
# Exponential backoff: 1s, 2s, 4s, 8s, 10s (capped)
delay = initial_delay * (2 ** attempt)
delay = min(delay, 10)  # Cap at 10 seconds
time.sleep(delay)
```

### 2. Improved MT5Manager Connection (`backend/mt5/connection.py`)

**MT5Manager.connect_all()** improvements:
- **Connection summary**: Reports total successful and failed connections
- **Per-account tracking**: Shows which accounts succeeded/failed and why
- **Better progress logging**: Clear status emojis and progress information
- **Graceful degradation**: Continues connecting other accounts even if some fail

```
🔗 Connecting 4 account(s)...
📍 Processing account 101510620...
✅ Account 101510620 connected successfully
📊 Connection summary: 2 succeeded, 2 failed
```

### 3. Auto-Trader Connection Handling (`backend/services/auto_trader.py`)

**evaluate_symbol()** improvements:
- **Connection status check**: Validates account is truly connected before evaluating
- **Warning instead of error**: Logs warnings for transient connection issues
- **Graceful degradation**: Skips evaluation if connection fails, retries next cycle

## Changes Summary

### File: `backend/mt5/connection.py`
- ✅ AccountSession.connect() - Exponential backoff, IPC timeout handling
- ✅ AccountSession.disconnect() - Better error handling
- ✅ AccountSession.get_balance() - Retry logic on connection
- ✅ MT5Manager.connect_all() - Connection summary and per-account tracking
- ✅ MT5Manager.connect_account() - Configurable max_retries parameter

### File: `backend/services/auto_trader.py`
- ✅ evaluate_symbol() - Better connection status validation

## Testing

To verify the fix works:

1. **Start without MT5 running**:
   ```bash
   uvicorn backend.main:app --host 0.0.0.0 --port 8000
   ```
   Expected: Logs show retries with increasing delays, connection attempts per account

2. **Start MT5 terminal during retries**:
   ```
   IPC timeout detected. Waiting 1.0s before retry...
   Attempting to initialize MT5 (attempt 2/5)...
   ✅ Successfully connected account 101510620
   ```

3. **Check connection status**:
   ```bash
   curl http://localhost:8000/health
   ```
   Should show connected accounts once MT5 is running

## Behavior

### Before Fix
- 3 fixed retries with 2-second delays
- ~6 seconds to give up per account
- No IPC timeout handling
- All-or-nothing connection approach

### After Fix
- Exponential backoff with up to 5 retries
- ~15 seconds to give up per account (with increasing delays)
- Special handling for IPC timeouts with diagnostic checks
- Graceful handling of partial failures
- Better visibility into connection status

## Configuration

Retry behavior can be customized by calling:
```python
# Custom retry attempts
mt5_manager.connect_all(max_retries=10)

# Or per account
mt5_manager.connect_account(account_id, max_retries=7)
```

## Error Diagnosis

Use the `/diagnose` endpoint to check connection status:
```bash
curl http://localhost:8000/diagnose
```

This shows:
- MT5 initialization status
- Connected accounts
- Any connection issues
- Diagnostic recommendations
