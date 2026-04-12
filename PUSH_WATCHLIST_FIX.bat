@echo off
REM Push watchlist endpoint fix to GitHub

cd /d "e:\Renko.worktrees\copilot-worktree-2026-04-12T12-16-25"

echo [*] Checking git status...
git status

echo.
echo [*] Staging changes...
git add backend/main.py backend/services/auto_trader.py

echo.
echo [*] Committing changes...
git commit -m "Fix watchlist endpoint conflict and add manual lot size priority

- Removed old watchlist router from backend/main.py that was conflicting
- Now only new endpoint from endpoints.py is used
- Added lot_size to load_watchlist() config dict
- Implemented manual lot size priority in execute_trade()
  - Manual lot_size from watchlist takes priority
  - Falls back to calculated lot_size if not set
- Fixes real-time watchlist updates not working

Co-authored-by: Copilot ^<223556219+Copilot@users.noreply.github.com^>"

echo.
echo [*] Pushing to GitHub...
git push origin main

echo.
echo [✓] Done! Changes pushed to GitHub
pause
