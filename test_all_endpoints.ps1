# Comprehensive API Endpoint Testing Script
$baseUrl = "http://localhost:5000"
$results = @()

Write-Host "`n" -NoNewline
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "  CRICNEX API ENDPOINT TESTING" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "`n"

# Test function
function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Method,
        [string]$Url,
        [hashtable]$Body = $null
    )
    
    Write-Host "Testing: $Name" -ForegroundColor Yellow -NoNewline
    
    try {
        if ($Method -eq "GET") {
            $response = Invoke-RestMethod -Uri $Url -Method $Method -TimeoutSec 5
        } else {
            $jsonBody = $Body | ConvertTo-Json -Depth 3
            $response = Invoke-RestMethod -Uri $Url -Method $Method -Body $jsonBody -ContentType "application/json" -TimeoutSec 5
        }
        
        Write-Host " [OK]" -ForegroundColor Green
        return @{
            Name = $Name
            Status = "PASSED"
            Method = $Method
            Url = $Url
            Response = $response
        }
    } catch {
        Write-Host " [FAIL]" -ForegroundColor Red
        Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
        return @{
            Name = $Name
            Status = "FAILED"
            Method = $Method
            Url = $Url
            Error = $_.Exception.Message
        }
    }
}

Write-Host "`n[SYSTEM ENDPOINTS]" -ForegroundColor Magenta
Write-Host "-" * 80 -ForegroundColor Gray

# 1. Health Check
$results += Test-Endpoint -Name "Health Check" -Method "GET" -Url "$baseUrl/api/health"

# 2. Model Info
$results += Test-Endpoint -Name "Model Info" -Method "GET" -Url "$baseUrl/api/model/info"

# 3. Stats Summary
$results += Test-Endpoint -Name "Stats Summary" -Method "GET" -Url "$baseUrl/api/stats/summary"

Write-Host "`n[PREDICTION ENDPOINTS]" -ForegroundColor Magenta
Write-Host "-" * 80 -ForegroundColor Gray

# 4. Single Prediction
$predictBody = @{
    player = "V Kohli"
    team = "Royal Challengers Bangalore"
    opponent = "Mumbai Indians"
    venue = "M Chinnaswamy Stadium"
}
$results += Test-Endpoint -Name "Single Prediction" -Method "POST" -Url "$baseUrl/api/predict" -Body $predictBody

# 5. Batch Prediction
$batchBody = @{
    predictions = @(
        @{
            player = "V Kohli"
            team = "Royal Challengers Bangalore"
            opponent = "Mumbai Indians"
            venue = "M Chinnaswamy Stadium"
        },
        @{
            player = "RG Sharma"
            team = "Mumbai Indians"
            opponent = "Chennai Super Kings"
            venue = "Wankhede Stadium"
        }
    )
}
$results += Test-Endpoint -Name "Batch Prediction" -Method "POST" -Url "$baseUrl/api/predict/batch" -Body $batchBody

Write-Host "`n[PLAYER ENDPOINTS]" -ForegroundColor Magenta
Write-Host "-" * 80 -ForegroundColor Gray

# 6. Get All Players
$results += Test-Endpoint -Name "Get All Players" -Method "GET" -Url "$baseUrl/api/players?limit=10"

# 7. Search Players
$results += Test-Endpoint -Name "Search Players" -Method "GET" -Url "$baseUrl/api/players/search?q=Kohli"

# 8. Get Player Details
$results += Test-Endpoint -Name "Get Player Details" -Method "GET" -Url "$baseUrl/api/players/V Kohli"

Write-Host "`n[TEAM ENDPOINTS]" -ForegroundColor Magenta
Write-Host "-" * 80 -ForegroundColor Gray

# 9. Get All Teams
$results += Test-Endpoint -Name "Get All Teams" -Method "GET" -Url "$baseUrl/api/teams"

# 10. Get Team Players
$results += Test-Endpoint -Name "Get Team Players" -Method "GET" -Url "$baseUrl/api/teams/Royal Challengers Bangalore/players"

Write-Host "`n[VENUE ENDPOINTS]" -ForegroundColor Magenta
Write-Host "-" * 80 -ForegroundColor Gray

# 11. Get All Venues
$results += Test-Endpoint -Name "Get All Venues" -Method "GET" -Url "$baseUrl/api/venues"

# 12. Get Venue Stats
$results += Test-Endpoint -Name "Get Venue Stats" -Method "GET" -Url "$baseUrl/api/venues/M Chinnaswamy Stadium/stats"

Write-Host "`n[LEADERBOARD ENDPOINTS]" -ForegroundColor Magenta
Write-Host "-" * 80 -ForegroundColor Gray

# 13. Top Run Scorers
$results += Test-Endpoint -Name "Top Run Scorers" -Method "GET" -Url "$baseUrl/api/leaderboard/runs?limit=10"

# 14. Top Strike Rates
$results += Test-Endpoint -Name "Top Strike Rates" -Method "GET" -Url "$baseUrl/api/leaderboard/strike-rate?limit=10"

# 15. Top Averages
$results += Test-Endpoint -Name "Top Averages" -Method "GET" -Url "$baseUrl/api/leaderboard/average?limit=10&min_matches=20"

Write-Host "`n[COMPARISON ENDPOINTS]" -ForegroundColor Magenta
Write-Host "-" * 80 -ForegroundColor Gray

# 16. Compare Players
$compareBody = @{
    players = @("V Kohli", "RG Sharma", "S Dhawan")
}
$results += Test-Endpoint -Name "Compare Players" -Method "POST" -Url "$baseUrl/api/compare/players" -Body $compareBody

Write-Host "`n[ANALYTICS ENDPOINTS]" -ForegroundColor Magenta
Write-Host "-" * 80 -ForegroundColor Gray

# 17. Recent Form
$results += Test-Endpoint -Name "Recent Form Analytics" -Method "GET" -Url "$baseUrl/api/analytics/form?days=30&limit=10"

# 18. Player Matchups (player vs team)
$results += Test-Endpoint -Name "Player Matchups" -Method "GET" -Url "$baseUrl/api/analytics/matchups?player=V Kohli&opponent=Mumbai Indians"

Write-Host "`n"
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "  TEST SUMMARY" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan

$passed = ($results | Where-Object { $_.Status -eq "PASSED" }).Count
$failed = ($results | Where-Object { $_.Status -eq "FAILED" }).Count
$total = $results.Count

Write-Host "`nTotal Tests: $total" -ForegroundColor White
Write-Host "Passed: $passed" -ForegroundColor Green
Write-Host "Failed: $failed" -ForegroundColor Red
Write-Host "Success Rate: $([math]::Round(($passed/$total)*100, 2))%" -ForegroundColor Cyan

if ($failed -gt 0) {
    Write-Host "`n[X] FAILED ENDPOINTS:" -ForegroundColor Red
    $results | Where-Object { $_.Status -eq "FAILED" } | ForEach-Object {
        Write-Host "  • $($_.Name) [$($_.Method) $($_.Url)]" -ForegroundColor Red
        Write-Host "    Error: $($_.Error)" -ForegroundColor Gray
    }
}

Write-Host "`n[OK] PASSED ENDPOINTS:" -ForegroundColor Green
$results | Where-Object { $_.Status -eq "PASSED" } | ForEach-Object {
    Write-Host "  • $($_.Name)" -ForegroundColor Green
}

Write-Host "`n" -NoNewline
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "`n"

# Export results to JSON
$results | ConvertTo-Json -Depth 5 | Out-File "test_results.json"
Write-Host "[FILE] Detailed results saved to: test_results.json" -ForegroundColor Yellow
