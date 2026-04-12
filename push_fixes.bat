@echo off
REM Push MT5 connection fixes to GitHub

cd /d e:\Renko.worktrees\copilot-worktree-2026-04-12T12-16-25

echo.
echo ========================================
echo Checking git status...
echo ========================================
git status

echo.
echo ========================================
echo Staging files...
echo ========================================
git add backend/mt5/connection.py
git add backend/main.py
git add CRITICAL_MT5_FIX_FINAL.md

echo.
echo ========================================
echo Committing...
echo ========================================
git commit -m "Fix critical MT5 initialization bug - initialize once globally per manager, not per account"

echo.
echo ========================================
echo Pushing to GitHub...
echo ========================================
git push origin main

echo.
echo ========================================
echo ✅ Push complete! Now pull in E:\renko
echo ========================================
pause
