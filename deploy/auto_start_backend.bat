@echo off
REM Auto-start script for Renko Backend — run by Windows Task Scheduler at logon
REM Place this file at C:\Renko\deploy\auto_start_backend.bat

cd /d C:\Renko

REM Wait 30 seconds for MT5 to initialize after login
timeout /t 30 /nobreak > nul

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Start backend (no --reload in production)
start /min "RenkoBackend" cmd /c "cd /d C:\Renko && .venv\Scripts\activate.bat && uvicorn backend.main:app --host 0.0.0.0 --port 8000 >> C:\Renko\backend.log 2>&1"

echo Backend started at %date% %time% >> C:\Renko\startup.log
