# 🚀 MT5 Connection Fix - Deployment Steps

## Summary of What's Fixed
✅ **Root Cause:** `mt5.initialize()` was being called for EVERY account in a loop, corrupting the IPC connection  
✅ **Solution:** Initialize MT5 ONCE at manager level, then login accounts sequentially  
✅ **Added:** Proper `mt5.shutdown()` cleanup on app exit  

## Files Modified
- `backend/mt5/connection.py` - Fixed initialization & connection logic
- `backend/main.py` - Added proper MT5 shutdown on exit
- `CRITICAL_MT5_FIX_FINAL.md` - Documentation

## Deployment Instructions (Windows)

### Phase 1: Local Machine (E:\Renko.worktrees\...)
```bash
cd e:\Renko.worktrees\copilot-worktree-2026-04-12T12-16-25
push_fixes.bat
```
This will:
- Commit changes from the worktree
- Push to GitHub
- Show summary

### Phase 2: Local Mirror (E:\renko)
```bash
cd e:\renko
pull_fixes.bat
```
This will:
- Pull latest changes from GitHub
- Show what changed
- Display commit history

### Phase 3: VPS (Your Linux/Windows VPS)
```bash
cd /path/to/renko  # Your VPS project directory
git pull origin main

# Kill old backend process
pkill -f "uvicorn backend.main"  # Linux/Mac
# OR
taskkill /F /IM python.exe  # Windows

# Start fresh
cd /path/to/renko
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

## Expected Output (Verify Success)

### ✅ GOOD - All accounts connected:
```
INFO:backend.main:Loaded 3 accounts from database
INFO:mt5:🔧 Initializing MT5 library (global)...
INFO:mt5:✅ MT5 library initialized successfully
INFO:mt5:🔗 Connecting 4 account(s) to initialized MT5...
INFO:mt5:📍 Processing account 101510620...
INFO:mt5:✅ Successfully connected account 101510620
INFO:mt5:📍 Processing account 336245996...
INFO:mt5:✅ Successfully connected account 336245996
INFO:mt5:📊 Connection summary: 3 succeeded, 0 failed
```

### ❌ BAD - IPC timeouts (means fix didn't apply):
```
ERROR:mt5:Failed connecting 101510620: MT5 initialize failed: (-10005, 'IPC timeout')
ERROR:mt5:Failed connecting 101510620: MT5 initialize failed: (-10005, 'IPC timeout')
```

## Troubleshooting

### If still seeing IPC timeouts:
1. **Check MT5 terminal is running** on VPS
2. **Verify the fix was pulled:**
   ```bash
   cat backend/mt5/connection.py | grep "mt5_initialized = False"
   ```
   Should show the new `self.mt5_initialized = False` flag

3. **Check if wrong version in use:**
   ```bash
   grep -n "mt5.initialize()" backend/mt5/connection.py
   # Should only see ONE initialize() call, around line 129
   # Not multiple calls in a loop
   ```

4. **Clear Python cache:**
   ```bash
   find . -type d -name __pycache__ -exec rm -rf {} +
   find . -name "*.pyc" -delete
   ```

5. **Restart backend with verbose logging:**
   ```bash
   python -u backend/main.py --log-level debug
   # OR
   uvicorn backend.main:app --log-level debug
   ```

## Testing Checklist
- [ ] Backend starts without errors
- [ ] See "Initializing MT5 library (global)" in logs (once, not per account)
- [ ] All accounts connect on startup
- [ ] No IPC timeout errors
- [ ] Auto-trading service starts
- [ ] Can trade on all accounts

## Rollback (if needed)
```bash
cd /path/to/renko
git revert HEAD  # Reverts last commit
git push origin main
```

## Contact
If issues persist, check the MT5 terminal settings and ensure it's accepting connections on your terminal's configured port.
