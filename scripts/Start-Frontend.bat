@echo off
REM Start Frontend React Application

set PROJECT_DIR=C:\Renko
set FRONTEND_DIR=%PROJECT_DIR%\frontend
set LOG_DIR=%PROJECT_DIR%\logs

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

cd /d "%FRONTEND_DIR%"

echo Building frontend...
call npm run build >> "%LOG_DIR%\build.log" 2>&1

echo Starting Frontend on port 5173...
echo Log file: %LOG_DIR%\frontend.log

call npm run preview -- --host 0.0.0.0 --port 5173 >> "%LOG_DIR%\frontend.log" 2>&1

pause
