@echo off
REM Quick start script for Renko Trading Bot on Windows

setlocal enabledelayedexpansion

echo.
echo ============================================================
echo   Renko Trading Bot - Quick Start
echo ============================================================
echo.

REM Check if .venv exists
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment
        echo Please ensure Python 3.11+ is installed
        pause
        exit /b 1
    )
)

REM Activate virtual environment
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo Error: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Check if packages are installed
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo Installing Python packages...
    pip install -q -r requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Verify setup
echo.
echo Verifying setup...
python verify_setup.py

echo.
echo ============================================================
echo   Starting Backend Server
echo ============================================================
echo.
echo Backend will be available at: http://localhost:8000
echo Health check: http://localhost:8000/health
echo.
echo Press Ctrl+C to stop the backend
echo.
echo In another terminal/PowerShell window, run:
echo   cd frontend
echo   npm run dev
echo.
echo Then open: http://localhost:5173
echo.
echo ============================================================
echo.

REM Start backend
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

pause
