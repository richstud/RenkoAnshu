@echo off
cd /d E:\Renko

echo.
echo ===== GIT STATUS =====
git status

echo.
echo ===== STAGING CHANGES =====
git add .

echo.
echo ===== COMMITTING CHANGES =====
git commit -m "fix: complete fixes for watchlist delete, live trades display, and auto-cleanup features

- LivePositions.tsx: Enhanced to show all trade fields (Symbol, Type, Lot, Entry Price, SL, TP, Brick Size, Time) in table format
- WatchlistManager: Added detailed debug logging for delete operations to troubleshoot GBPCHF deletion errors  
- endpoints.py: Added two new endpoints for trade auto-cleanup and closed trade management

These changes address:
1. Live trades now display ALL values except exit price (as requested)
2. Watchlist delete now has enhanced debugging output
3. Automatic trade cleanup ensures database stays clean with only recent trades
4. Closed trades are properly managed and moved to history

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

echo.
echo ===== PUSHING TO GITHUB =====
git push

echo.
echo ===== COMPLETE =====
echo All changes pushed to GitHub!
echo.
pause
