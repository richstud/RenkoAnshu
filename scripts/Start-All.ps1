# Renko Trading Bot - Windows PowerShell Startup Script
# Run as Administrator
# This script auto-starts all services when you open the frontend

param(
    [string]$ProjectPath = "C:\Renko",
    [int]$BackendPort = 8000,
    [int]$FrontendPort = 5173
)

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "🤖 Renko Trading Bot - Windows Startup" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Create logs directory
$LogPath = Join-Path $ProjectPath "logs"
if (-not (Test-Path $LogPath)) {
    New-Item -ItemType Directory -Path $LogPath | Out-Null
}

# Function to log
function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp - $Message" | Tee-Object -FilePath (Join-Path $LogPath "startup.log") -Append | Write-Host
}

# Check if Python is installed
Write-Log "Checking Python installation..."
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "❌ Python not found! Please install Python 3.11+" -ForegroundColor Red
    exit 1
}
Write-Log "✅ Python found: $(python --version)"

# Check if Node.js is installed
Write-Log "Checking Node.js installation..."
$node = Get-Command npm -ErrorAction SilentlyContinue
if (-not $node) {
    Write-Host "❌ Node.js not found! Please install Node.js 18+" -ForegroundColor Red
    exit 1
}
Write-Log "✅ Node.js found: $(npm --version)"

# Change to project directory
Set-Location $ProjectPath
Write-Log "Working directory: $ProjectPath"

# Kill existing processes (cleanup)
Write-Log "Cleaning up existing processes..."
Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*uvicorn*" } | Stop-Process -Force -ErrorAction SilentlyContinue
Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

# Start Backend API
Write-Log "Starting Backend API on port $BackendPort..."
$BackendProcess = Start-Process python -ArgumentList "-m uvicorn backend.main:app --host 0.0.0.0 --port $BackendPort --reload" `
    -RedirectStandardOutput (Join-Path $LogPath "backend.log") `
    -RedirectStandardError (Join-Path $LogPath "backend-error.log") `
    -PassThru `
    -WindowStyle Normal
Write-Log "✅ Backend API started (PID: $($BackendProcess.Id))"

# Wait for backend to be ready
Write-Log "Waiting for backend to start..."
Start-Sleep -Seconds 3

# Check if backend is responding
$BackendReady = $false
for ($i = 1; $i -le 10; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$BackendPort/api/tickers" -UseBasicParsing -TimeoutSec 2
        if ($response.StatusCode -eq 200) {
            $BackendReady = $true
            break
        }
    } catch {
        Start-Sleep -Seconds 1
    }
}

if ($BackendReady) {
    Write-Log "✅ Backend API is responding"
} else {
    Write-Host "❌ Backend failed to start. Check $LogPath\backend-error.log" -ForegroundColor Red
    exit 1
}

# Start Trading Worker
Write-Log "Starting Trading Strategy Worker..."
$WorkerProcess = Start-Process python -ArgumentList "backend/worker.py" `
    -RedirectStandardOutput (Join-Path $LogPath "worker.log") `
    -RedirectStandardError (Join-Path $LogPath "worker-error.log") `
    -PassThru `
    -WindowStyle Normal
Write-Log "✅ Trading Worker started (PID: $($WorkerProcess.Id))"

# Build Frontend
Write-Log "Building Frontend for production..."
Set-Location (Join-Path $ProjectPath "frontend")
& npm run build 2>&1 | Tee-Object -FilePath (Join-Path $LogPath "build.log") -Append | Out-Null
Write-Log "✅ Frontend built successfully"

# Start Frontend
Write-Log "Starting Frontend on port $FrontendPort..."
$FrontendProcess = Start-Process npm -ArgumentList "run preview -- --host 0.0.0.0 --port $FrontendPort" `
    -RedirectStandardOutput (Join-Path $LogPath "frontend.log") `
    -RedirectStandardError (Join-Path $LogPath "frontend-error.log") `
    -PassThru `
    -WindowStyle Normal
Write-Log "✅ Frontend started (PID: $($FrontendProcess.Id))"

# Write PID file for shutdown
@{
    Backend = $BackendProcess.Id
    Worker = $WorkerProcess.Id
    Frontend = $FrontendProcess.Id
} | ConvertTo-Json | Out-File (Join-Path $LogPath "pids.json")

Write-Log "======================================="
Write-Log "✨ All services started successfully!"
Write-Log "Backend:  http://localhost:$BackendPort"
Write-Log "Frontend: http://localhost:$FrontendPort"
Write-Log "======================================="

# Open browser
Start-Process "http://localhost:$FrontendPort"

# Wait for all processes
Write-Log "Monitoring services..."
$BackendProcess.WaitForExit()
