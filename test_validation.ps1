# PowerShell validation test script

Write-Host "Testing valid audit log event..." -ForegroundColor Cyan
$validPayload = @{
    date = "2026-02-17 14:30:45.123 -0500"
    application = "mrbeta.m3globalresearch.com"
    ipaddr = "192.168.123.234"
    userid = "userabc123"
    result = $true
    eventtype = "login"
    message = @{
        detail = "User attempted password reset"
    }
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8080" -Method Post -Body $validPayload -ContentType "application/json"
Write-Host ""

Write-Host "Testing invalid event type (should fail)..." -ForegroundColor Cyan
$invalidEventType = @{
    date = "2026-02-17 14:30:45.123 -0500"
    application = "mrbeta.m3globalresearch.com"
    ipaddr = "192.168.123.234"
    userid = "userabc123"
    result = $true
    eventtype = "invalid_event"
    message = @{
        detail = "This should fail validation"
    }
} | ConvertTo-Json

try {
    Invoke-RestMethod -Uri "http://localhost:8080" -Method Post -Body $invalidEventType -ContentType "application/json"
} catch {
    Write-Host "Error (expected): $($_.Exception.Message)" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "Testing missing required field (should fail)..." -ForegroundColor Cyan
$missingField = @{
    date = "2026-02-17 14:30:45.123 -0500"
    application = "mrbeta.m3globalresearch.com"
    ipaddr = "192.168.123.234"
    result = $true
    eventtype = "login"
    message = @{
        detail = "Missing userid field"
    }
} | ConvertTo-Json

try {
    Invoke-RestMethod -Uri "http://localhost:8080" -Method Post -Body $missingField -ContentType "application/json"
} catch {
    Write-Host "Error (expected): $($_.Exception.Message)" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "Testing invalid IP address format (should fail)..." -ForegroundColor Cyan
$invalidIP = @{
    date = "2026-02-17 14:30:45.123 -0500"
    application = "mrbeta.m3globalresearch.com"
    ipaddr = "invalid.ip.address"
    userid = "userabc123"
    result = $true
    eventtype = "login"
    message = @{
        detail = "Invalid IP format"
    }
} | ConvertTo-Json

try {
    Invoke-RestMethod -Uri "http://localhost:8080" -Method Post -Body $invalidIP -ContentType "application/json"
} catch {
    Write-Host "Error (expected): $($_.Exception.Message)" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "Validation tests completed!" -ForegroundColor Green
