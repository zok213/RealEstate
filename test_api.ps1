# Test Full-Site API Endpoints
# Usage: .\test_api.ps1
# Make sure server is running first (.\start_server.ps1)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Testing Full-Site API Endpoints" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if server is running
Write-Host "[1/2] Checking if server is running..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/" -Method GET -TimeoutSec 5
    Write-Host "[OK] Server is running!" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "[ERROR] Server is not running!" -ForegroundColor Red
    Write-Host "[INFO] Please start the server first:" -ForegroundColor Yellow
    Write-Host "       .\start_server.ps1" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

# Run test script
Write-Host "[2/2] Running API test script..." -ForegroundColor Yellow
Set-Location -Path "sample-data"
..\.venv_fix\Scripts\python.exe test_fullsite_api.py
