@echo off
REM Auto-deployment script for VPS Backend Setup
REM Run this on your VPS

echo.
echo ============================================================
echo   Renko Backend - VPS Deployment Script
echo ============================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found. Install Python 3.11+ first.
    pause
    exit /b 1
)

REM Create venv
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate venv
call .venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -q fastapi uvicorn pydantic pydantic-settings MetaTrader5 supabase python-dotenv gunicorn

REM Check .env exists
if not exist ".env" (
    echo.
    echo ERROR: .env file not found!
    echo Create .env with:
    echo   SUPABASE_URL=...
    echo   SUPABASE_KEY=...
    echo   MT5_LOGIN=101510620
    echo   MT5_PASSWORD=...
    echo   MT5_SERVER=XMGlobal-MT5 5
    pause
    exit /b 1
)

REM Start backend
echo.
echo ============================================================
echo   Starting Renko Backend
echo ============================================================
echo.
echo Backend running on: http://0.0.0.0:8000
echo Health check: http://<YOUR_VPS_IP>:8000/health
echo Diagnose: http://<YOUR_VPS_IP>:8000/diagnose
echo.
echo Important:
echo   1. Make sure MT5 Terminal is running on this VPS
echo   2. Keep this window open
echo   3. Make sure port 8000 is open in firewall
echo.

python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

pause
