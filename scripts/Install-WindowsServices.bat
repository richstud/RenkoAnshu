@echo off
REM Renko Trading Bot - Windows Service Setup with NSSM
REM This script installs services that auto-start on Windows VPS boot
REM Requires admin privileges and NSSM installed

setlocal enabledelayedexpansion

set PROJECT_DIR=C:\Renko
set NSSM_PATH=C:\nssm\nssm-2.24\win64\nssm.exe
set PYTHON_PATH=%PROJECT_DIR%\.venv\Scripts\python.exe

REM Check if running as admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ Please run this script as Administrator
    pause
    exit /b 1
)

echo.
echo ====================================
echo Setting up Renko as Windows Services
echo ====================================
echo.

REM Check if NSSM exists
if not exist "%NSSM_PATH%" (
    echo ❌ NSSM not found at %NSSM_PATH%
    echo Please download NSSM from: https://nssm.cc/download
    echo Extract to: C:\nssm
    pause
    exit /b 1
)

REM Check if project dir exists
if not exist "%PROJECT_DIR%" (
    echo ❌ Project directory not found: %PROJECT_DIR%
    pause
    exit /b 1
)

echo Setting up Backend API service...
%NSSM_PATH% install RenkoBackend "%PYTHON_PATH%" "-m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 2"
%NSSM_PATH% set RenkoBackend AppDirectory "%PROJECT_DIR%"
%NSSM_PATH% set RenkoBackend AppStdout "%PROJECT_DIR%\logs\backend.log"
%NSSM_PATH% set RenkoBackend AppStderr "%PROJECT_DIR%\logs\backend-error.log"
%NSSM_PATH% set RenkoBackend Start SERVICE_AUTO_START
echo ✅ Backend service installed

echo Setting up Trading Worker service...
%NSSM_PATH% install RenkoWorker "%PYTHON_PATH%" "backend/worker.py"
%NSSM_PATH% set RenkoWorker AppDirectory "%PROJECT_DIR%"
%NSSM_PATH% set RenkoWorker AppStdout "%PROJECT_DIR%\logs\worker.log"
%NSSM_PATH% set RenkoWorker AppStderr "%PROJECT_DIR%\logs\worker-error.log"
%NSSM_PATH% set RenkoWorker Start SERVICE_AUTO_START
%NSSM_PATH% set RenkoWorker DependOnService RenkoBackend
echo ✅ Worker service installed

echo Starting services...
net start RenkoBackend
timeout /t 2 /nobreak
net start RenkoWorker

echo.
echo ====================================
echo ✨ Services installed and started!
echo ====================================
echo.
echo Commands:
echo   net start RenkoBackend   - Start backend
echo   net stop RenkoBackend    - Stop backend
echo   net start RenkoWorker    - Start worker
echo   net stop RenkoWorker     - Stop worker
echo.
echo To remove services later:
echo   %NSSM_PATH% remove RenkoBackend confirm
echo   %NSSM_PATH% remove RenkoWorker confirm
echo.

pause
