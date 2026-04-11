@echo off
REM Push the auto_trader fix to GitHub

cd /d "E:\Renko"

echo Staging changes...
git add backend/services/auto_trader.py

echo Committing...
git commit -m "Fix: Use lot_size directly instead of lot_size_rules

- Changed from config['lot_size_rules'] to config.get('lot_size', 0.01)
- Watchlist table has direct lot_size field, not lot_size_rules
- This fixes 'lot_size_rules' KeyError in trade execution

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

echo Pushing to GitHub...
git push origin main

echo Done! Now pull on VPS with: git pull origin main
pause
