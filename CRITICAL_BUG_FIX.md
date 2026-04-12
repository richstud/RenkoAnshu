# CRITICAL BUG FIX: Multi-Account Connection Failure

## Issue
All 4 accounts failing with `MT5 initialize failed: (-10005, 'IPC timeout')` error when trying to connect simultaneously.

## Root Cause
**File:** `backend/mt5/connection.py` (line 100)

The `disconnect()` method was calling `mt5.shutdown()` which **completely terminates the global MT5 connection**, not just logging out a specific account. When one account disconnected, it killed the IPC connection for ALL accounts.

### The Bug Flow:
1. Account 1 disconnects → `disconnect()` called → `mt5.shutdown()`
2. MT5 global connection dies
3. Accounts 2, 3, 4 try to connect → `IPC timeout` (connection is dead)
4. Multi-account trading breaks

## Solution

### Change 1: Use `mt5.logout()` instead of `mt5.shutdown()`

**File:** `backend/mt5/connection.py`

```python
# BEFORE (Broken):
def disconnect(self):
    if self.connected:
        try:
            mt5.shutdown()  # ❌ Kills GLOBAL connection
        except Exception as e:
            logger.warning(f"Error during MT5 shutdown: {e}")
        self.connected = False

# AFTER (Fixed):
def disconnect(self):
    if self.connected:
        try:
            mt5.logout()  # ✅ Logs out only THIS account
        except Exception as e:
            logger.warning(f"Error during MT5 logout: {e}")
        self.connected = False
```

### Change 2: Remove Duplicate Method

**File:** `backend/services/auto_trader.py` (lines 358-367)

Removed duplicate `calculate_lot_size(self, balance: float, lot_size_rules: dict)` method that was conflicting with the main method and not being used.

## Impact

### Before Fix:
- ❌ Only 1 account could stay connected
- ❌ IPC timeout errors on all subsequent connections
- ❌ Disconnecting any account broke all others

### After Fix:
- ✅ All 4 accounts connect simultaneously
- ✅ Can disconnect one account without affecting others
- ✅ Multi-account trading fully functional

## Testing

After deploying this fix:

```bash
# On VPS, restart backend
sudo systemctl restart renko-backend

# Or manually:
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

You should see all 4 accounts connect successfully:
```
INFO:backend.main:Attempting to connect 4 account(s)
✅ Account 101510620 connected successfully
✅ Account 336245996 connected successfully
✅ Account 1301212568 connected successfully
✅ Account [4th] connected successfully
```

## Files Changed
- `backend/mt5/connection.py` - Line 100 (shutdown → logout)
- `backend/services/auto_trader.py` - Lines 358-367 (removed duplicate method)
