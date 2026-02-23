# Start Backend Server for Real Estate API
# Usage: .\start_server.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Real Estate Backend Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Navigate to backend directory
Set-Location -Path "backend"

Write-Host "[INFO] Starting uvicorn server on http://localhost:8000" -ForegroundColor Green
Write-Host "[INFO] Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start server
# Start server using local reliable venv
..\.venv_fix\Scripts\python.exe -m uvicorn api.main:app --reload --port 8000
