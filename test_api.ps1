# PowerShell script to test CricNex API endpoints

Write-Host "🧪 Testing CricNex Backend API" -ForegroundColor Cyan
Write-Host "================================`n" -ForegroundColor Cyan

# Test 1: Health Check
Write-Host "1️⃣ Testing Health Check..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:5000/api/health" -Method GET
    Write-Host "✅ Status: $($health.status)" -ForegroundColor Green
    Write-Host $($health | ConvertTo-Json) -ForegroundColor Gray
} catch {
    Write-Host "❌ Failed: $_" -ForegroundColor Red
}

Write-Host "`n"

# Test 2: Predict Player Performance
Write-Host "2️⃣ Testing Prediction..." -ForegroundColor Yellow
try {
    $body = @{
        player = "V Kohli"
        team = "Royal Challengers Bangalore"
        opponent = "Mumbai Indians"
        venue = "M Chinnaswamy Stadium"
    } | ConvertTo-Json
    
    $prediction = Invoke-RestMethod -Uri "http://localhost:5000/api/predict" -Method POST -Body $body -ContentType "application/json"
    Write-Host "✅ Predicted Runs: $($prediction.predicted_runs)" -ForegroundColor Green
    Write-Host $($prediction | ConvertTo-Json -Depth 3) -ForegroundColor Gray
} catch {
    Write-Host "❌ Failed: $_" -ForegroundColor Red
}

Write-Host "`n"

# Test 3: Get Players List
Write-Host "3️⃣ Testing Get Players..." -ForegroundColor Yellow
try {
    $players = Invoke-RestMethod -Uri "http://localhost:5000/api/players?limit=5" -Method GET
    Write-Host "✅ Total Players: $($players.total)" -ForegroundColor Green
    Write-Host "Top 5 Players:" -ForegroundColor Gray
    $players.players | Format-Table -Property player, total_runs, avg_runs, matches
} catch {
    Write-Host "❌ Failed: $_" -ForegroundColor Red
}

Write-Host "`n"

# Test 4: Leaderboard
Write-Host "4️⃣ Testing Leaderboard..." -ForegroundColor Yellow
try {
    $leaderboard = Invoke-RestMethod -Uri "http://localhost:5000/api/leaderboard/runs?limit=5" -Method GET
    Write-Host "✅ Top Run Scorers:" -ForegroundColor Green
    $leaderboard.leaderboard | Format-Table -Property rank, player, total_runs, matches
} catch {
    Write-Host "❌ Failed: $_" -ForegroundColor Red
}

Write-Host "`n================================" -ForegroundColor Cyan
Write-Host "✨ Testing Complete!" -ForegroundColor Cyan
