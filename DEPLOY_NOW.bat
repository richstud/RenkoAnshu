@echo off
REM Simple deployment script - Commit and push all fixes

cd /d E:\Renko

echo.
echo ========================================
echo  RENKO TRADING BOT - DEPLOYMENT SCRIPT
echo ========================================
echo.

echo [1/3] Checking Git Status...
echo.
git status
echo.

echo [2/3] Staging and Committing Changes...
echo.
git add .
timeout /t 2 /nobreak

git commit -m "fix: complete fixes for watchlist delete, live trades display, and auto-cleanup features

- LivePositions.tsx: Enhanced to show all trade fields in table format
- WatchlistManager: Added debug logging for delete troubleshooting
- endpoints.py: Added auto-cleanup and closed trade management endpoints

Fixes:
1. Live trades now show ALL values except exit price
2. Watchlist delete now has detailed debug output
3. Auto-cleanup keeps only today and yesterday trades
4. Closed trades properly managed and moved to history

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

echo.
echo [3/3] Pushing to GitHub...
echo.
git push

echo.
echo ========================================
echo  ✅ DEPLOYMENT COMPLETE!
echo ========================================
echo.
echo Next Steps (on VPS):
echo 1. cd c:\tradingbot\renko
echo 2. git pull
echo 3. python -m pip install -r requirements.txt
echo 4. Restart backend service
echo.
pause
