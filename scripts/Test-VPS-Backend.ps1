# Test VPS Backend Connectivity
# Run this to verify backend is accessible from your local machine

param(
    [string]$VpsIP = "114.29.239.50",
    [int]$Port = 8000
)

$BackendUrl = "http://$VpsIP:$Port"

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "🔍 VPS Backend Connectivity Test" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "VPS IP:       $VpsIP" -ForegroundColor Yellow
Write-Host "Backend Port: $Port" -ForegroundColor Yellow
Write-Host "URL:          $BackendUrl" -ForegroundColor Yellow
Write-Host ""

# Test 1: TCP Connection
Write-Host "Test 1: TCP Connection..." -ForegroundColor Cyan
try {
    $socket = New-Object System.Net.Sockets.TcpClient
    $socket.Connect($VpsIP, $Port)
    if ($socket.Connected) {
        Write-Host "✅ TCP connection successful" -ForegroundColor Green
        $socket.Close()
    }
} catch {
    Write-Host "❌ TCP connection failed: $_" -ForegroundColor Red
}

# Test 2: API Health Check
Write-Host ""
Write-Host "Test 2: API Health Check..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$BackendUrl/api/tickers" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ API responding with HTTP 200" -ForegroundColor Green
        Write-Host ""
        Write-Host "API Response:" -ForegroundColor Cyan
        $content = $response.Content | ConvertFrom-Json
        $content | ConvertTo-Json | Write-Host
    }
} catch {
    Write-Host "❌ API request failed: $_" -ForegroundColor Red
}

# Test 3: Get Accounts
Write-Host ""
Write-Host "Test 3: Get Accounts..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$BackendUrl/api/accounts" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Accounts endpoint responding" -ForegroundColor Green
        $accounts = $response.Content | ConvertFrom-Json
        Write-Host "Found $($accounts.Count) account(s)" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️ Accounts endpoint: $_" -ForegroundColor Yellow
}

# Test 4: Get Trades
Write-Host ""
Write-Host "Test 4: Get Trades..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$BackendUrl/api/trades" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Trades endpoint responding" -ForegroundColor Green
        $trades = $response.Content | ConvertFrom-Json
        Write-Host "Found $($trades.Count) trade(s)" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️ Trades endpoint: $_" -ForegroundColor Yellow
}

# Test 5: CORS Check
Write-Host ""
Write-Host "Test 5: CORS Headers..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$BackendUrl/api/tickers" -UseBasicParsing -TimeoutSec 5
    $corsHeader = $response.Headers['Access-Control-Allow-Origin']
    if ($corsHeader) {
        Write-Host "✅ CORS is enabled: $corsHeader" -ForegroundColor Green
    } else {
        Write-Host "⚠️ CORS headers not found (may still work)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Failed to check CORS: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "✨ Test Complete" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Summary
Write-Host "📝 Summary:" -ForegroundColor Cyan
Write-Host "  • If all tests pass, backend is running correctly" -ForegroundColor Gray
Write-Host "  • Frontend .env is set to: http://114.29.239.50:8000" -ForegroundColor Gray
Write-Host "  • Make sure firewall allows port 8000 from your IP" -ForegroundColor Gray
Write-Host ""
