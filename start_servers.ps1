# CricNex Startup Script
Write-Host "Starting CricNex Application..." -ForegroundColor Green

# Start Backend
Write-Host "`nStarting Backend Server..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location 'C:\Users\Asus\Documents\CRICNEX\src'; python backend.py"

# Wait for backend to start
Start-Sleep -Seconds 5

# Start Frontend
Write-Host "Starting Frontend Server..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location 'C:\Users\Asus\Documents\CRICNEX\frontend'; npm start"

Write-Host "`nServers are starting..." -ForegroundColor Green
Write-Host "Backend: http://localhost:5000" -ForegroundColor Yellow
Write-Host "Frontend: http://localhost:3001" -ForegroundColor Yellow
Write-Host "`nClose the individual terminal windows to stop the servers." -ForegroundColor Gray
