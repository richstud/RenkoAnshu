@echo off
REM Frontend startup script for Renko Trading Bot

setlocal

echo.
echo ============================================================
echo   Renko Trading Bot - Frontend Setup
echo ============================================================
echo.

REM Check if we're in the right directory
if not exist "package.json" (
    echo Error: package.json not found in current directory
    echo Please run this from the frontend directory:
    echo   cd frontend
    echo   .\start_frontend.bat
    pause
    exit /b 1
)

REM Check if node_modules exists
if not exist "node_modules" (
    echo Installing npm dependencies...
    call npm install --legacy-peer-deps
    if errorlevel 1 (
        echo Error: Failed to install npm dependencies
        echo Make sure Node.js 18+ is installed
        pause
        exit /b 1
    )
)

echo.
echo ============================================================
echo   Starting Frontend Development Server
echo ============================================================
echo.
echo Frontend will be available at: http://localhost:5173
echo API URL: http://localhost:8000
echo.
echo Make sure the backend is running:
echo   - In another terminal: run start_backend.bat from project root
echo   - Or: uvicorn backend.main:app --host 0.0.0.0 --port 8000
echo.
echo Press Ctrl+C to stop the frontend
echo.
echo ============================================================
echo.

REM Start frontend dev server
call npm run dev

pause
