@echo off
echo ============================================================
echo  Pushing Renko Bot to GitHub (main branch)
echo ============================================================

REM Work from the worktree
cd /d "E:\Renko.worktrees\copilot-worktree-2026-04-26T13-58-47"

echo.
echo [1/4] Staging all changes...
git add -A

echo.
echo [2/4] Committing...
git commit -m "feat: full codebase update - frontend and backend ready for deployment

- Add .gitignore to protect credentials
- Update frontend/.env.example with all required variables
- Backend: FastAPI + MT5 integration + Supabase
- Frontend: React + Vite + Tailwind + Supabase realtime
- Auto-trading, Renko charts, watchlist, account management

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

echo.
echo [3/4] Pushing worktree branch...
git push origin copilot/worktree-2026-04-26T13-58-47

echo.
echo [4/4] Merging to main and pushing...
cd /d "E:\Renko"
git checkout main
git merge copilot/worktree-2026-04-26T13-58-47 --no-edit
git push origin main

echo.
echo ============================================================
echo  DONE! Repo updated at: https://github.com/richstud/renko
echo  Clone with: git clone https://github.com/richstud/renko.git
echo ============================================================
pause
