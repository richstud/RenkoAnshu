@echo off
REM Start Backend API Service

set PROJECT_DIR=C:\Renko
set LOG_DIR=%PROJECT_DIR%\logs

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

cd /d "%PROJECT_DIR%"

echo Starting Backend API on port 8000...
echo Log file: %LOG_DIR%\backend.log

python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload >> "%LOG_DIR%\backend.log" 2>&1

pause
