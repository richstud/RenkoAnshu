@echo off
REM Renko Trading Bot - Windows Startup Script
REM This script starts all services: Backend API, Frontend, and Trading Strategy

setlocal enabledelayedexpansion

set PROJECT_DIR=e:\Renko
set PYTHON_ENV=%PROJECT_DIR%\.venv
set LOG_DIR=%PROJECT_DIR%\logs

REM Create logs directory
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

echo.
echo ====================================
echo 🤖 Starting Renko Trading Bot
echo ====================================
echo.

REM Check Python environment
if not exist "%PYTHON_ENV%\Scripts\activate.bat" (
    echo ❌ Python environment not found at %PYTHON_ENV%
    exit /b 1
)

REM Activate Python environment
call "%PYTHON_ENV%\Scripts\activate.bat"
echo ✅ Python environment activated

REM Change to project directory
cd /d "%PROJECT_DIR%"

REM Start Backend API (in new window)
echo Starting Backend API on port 8000...
start "Backend API" cmd /k "python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 2"
echo ✅ Backend API window opened

REM Wait for backend to start
timeout /t 3 /nobreak

REM Start Trading Strategy Worker (in new window)
echo Starting Trading Strategy Worker...
start "Trading Worker" cmd /k "python backend/worker.py"
echo ✅ Trading Worker window opened

REM Build frontend for production
echo Building Frontend...
cd /d "%PROJECT_DIR%\frontend"
call npm run build

REM Start Frontend (in new window)
echo Starting Frontend on port 5173...
start "Renko Frontend" cmd /k "npm run preview -- --host 0.0.0.0 --port 5173"
echo ✅ Frontend window opened

echo.
echo ====================================
echo ✨ All services starting!
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo ====================================
echo.

REM Open browser to frontend
start http://localhost:5173

pause
