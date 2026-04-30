@echo off
cd /d C:\Renkoclone
git add backend\main.py backend\mt5\connection.py backend\api\account_manager.py backend\supabase\schema.sql NEW_SUPABASE_SETUP.sql
git commit -m "Fix MT5 IPC log spam: add 5s cooldown on switch_to failure in ws/live" -m "- main.py: only log MT5 switch failure once, retry every 5s (not every 100ms)" -m "- main.py: skip account/quotes/positions queries when MT5 is disconnected" -m "- main.py: add import time" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
git push origin main
echo Done!
pause

