@echo off
REM Test connectivity to backend on VPS

echo.
echo ===============================================
echo Testing Backend Connectivity
echo ===============================================
echo.

set VPS_IP=114.29.239.50
set BACKEND_PORT=8000

echo Testing connection to http://%VPS_IP%:%BACKEND_PORT%/api/tickers...
echo.

REM Test with curl if available
where curl >nul 2>&1
if %errorLevel% equ 0 (
    echo Using curl:
    curl -v http://%VPS_IP%:%BACKEND_PORT%/api/tickers
    echo.
) else (
    REM Use PowerShell as fallback
    echo Using PowerShell:
    powershell -Command "$ErrorActionPreference = 'SilentlyContinue'; (Invoke-WebRequest 'http://%VPS_IP%:%BACKEND_PORT%/api/tickers' -UseBasicParsing).Content"
)

echo.
echo ===============================================
echo Test Complete
echo ===============================================
echo.
echo If you see JSON data above, backend is working!
echo.

pause
