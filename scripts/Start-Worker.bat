@echo off
REM Start Trading Strategy Worker Service

set PROJECT_DIR=C:\Renko
set LOG_DIR=%PROJECT_DIR%\logs

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

cd /d "%PROJECT_DIR%"

echo Starting Trading Worker...
echo Log file: %LOG_DIR%\worker.log

python backend/worker.py >> "%LOG_DIR%\worker.log" 2>&1

pause
