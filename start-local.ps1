$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$frontendDir = Join-Path $projectRoot "frontend"

Write-Host "Starting ClearSpace locally..." -ForegroundColor Cyan

if (-not (Test-Path (Join-Path $frontendDir "node_modules"))) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    Push-Location $frontendDir
    npm install
    Pop-Location
}

Write-Host "Installing backend dependencies..." -ForegroundColor Yellow
Push-Location $projectRoot
python -m pip install -r "backend/requirements.txt"
Pop-Location

Write-Host "Launching backend on http://127.0.0.1:8000" -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectRoot'; python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000"

Write-Host "Launching frontend on http://localhost:3000" -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendDir'; npm run dev"

Write-Host "Done. Two new terminal windows should be running." -ForegroundColor Cyan
