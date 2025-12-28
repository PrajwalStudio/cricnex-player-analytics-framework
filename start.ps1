# CricNex Full Stack Launcher
# This script starts both backend and frontend servers

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  CRICNEX FULL STACK LAUNCHER" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check if Node.js is installed
Write-Host "[1/5] Checking Node.js installation..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    Write-Host "  Node.js version: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Node.js is not installed!" -ForegroundColor Red
    Write-Host "  Please install Node.js from https://nodejs.org/" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Python is available
Write-Host "`n[2/5] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version
    Write-Host "  $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Python is not installed!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if frontend dependencies are installed
Write-Host "`n[3/5] Checking frontend dependencies..." -ForegroundColor Yellow
if (!(Test-Path "frontend\node_modules")) {
    Write-Host "  Installing frontend dependencies (this may take a few minutes)..." -ForegroundColor Yellow
    Set-Location frontend
    npm install
    Set-Location ..
    Write-Host "  Dependencies installed successfully!" -ForegroundColor Green
} else {
    Write-Host "  Frontend dependencies already installed" -ForegroundColor Green
}

# Start Backend Server
Write-Host "`n[4/5] Starting Backend Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; python src/backend.py"
Write-Host "  Backend server starting on http://localhost:5000" -ForegroundColor Green
Start-Sleep -Seconds 3

# Start Frontend Server
Write-Host "`n[5/5] Starting Frontend Server..." -ForegroundColor Yellow
Set-Location frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; npm start"
Set-Location ..
Write-Host "  Frontend server starting on http://localhost:3000" -ForegroundColor Green

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  CRICNEX IS STARTING!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "`nBackend:  http://localhost:5000" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "`nThe frontend will open automatically in your browser." -ForegroundColor White
Write-Host "`nTwo new PowerShell windows have been opened:" -ForegroundColor White
Write-Host "  1. Backend Server (Python)" -ForegroundColor Gray
Write-Host "  2. Frontend Server (React)" -ForegroundColor Gray
Write-Host "`nTo stop the servers, close those PowerShell windows." -ForegroundColor White
Write-Host "`n========================================`n" -ForegroundColor Green

Read-Host "Press Enter to close this window"
