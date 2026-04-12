@echo off
REM Renko Trading Bot - Windows Task Scheduler Setup
REM Creates tasks that auto-start all services on Windows VPS boot
REM Requires admin privileges

setlocal enabledelayedexpansion

set PROJECT_DIR=C:\Renko
set SCRIPT_PATH=%PROJECT_DIR%\scripts\Start-All.ps1
set BACKEND_SCRIPT=%PROJECT_DIR%\scripts\Start-Backend.bat
set WORKER_SCRIPT=%PROJECT_DIR%\scripts\Start-Worker.bat
set FRONTEND_SCRIPT=%PROJECT_DIR%\scripts\Start-Frontend.bat

REM Check if running as admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ Please run this script as Administrator
    pause
    exit /b 1
)

echo.
echo ====================================
echo Setting up Windows Task Scheduler
echo ====================================
echo.

REM Create Backend task
echo Creating Backend task...
schtasks /create /tn "Renko\Backend" /tr "cmd /c start %BACKEND_SCRIPT%" /sc onstart /ru SYSTEM /f
echo ✅ Backend task created

REM Create Worker task
echo Creating Worker task...
schtasks /create /tn "Renko\Worker" /tr "cmd /c start %WORKER_SCRIPT%" /sc onstart /ru SYSTEM /f /de
echo ✅ Worker task created

REM Create Frontend task
echo Creating Frontend task...
schtasks /create /tn "Renko\Frontend" /tr "cmd /c start %FRONTEND_SCRIPT%" /sc onstart /ru SYSTEM /f /de
echo ✅ Frontend task created

echo.
echo ====================================
echo ✨ Tasks created successfully!
echo ====================================
echo.
echo Services will auto-start on system boot.
echo.
echo To view scheduled tasks:
echo   Control Panel ^> Administrative Tools ^> Task Scheduler
echo.
echo To remove tasks:
echo   schtasks /delete /tn "Renko\Backend" /f
echo   schtasks /delete /tn "Renko\Worker" /f
echo   schtasks /delete /tn "Renko\Frontend" /f
echo.

pause
