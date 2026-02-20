# PowerShell test script for audit log webhook
# This sends a sample audit log event to the webhook server

$payload = @{
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

Invoke-RestMethod -Uri "http://localhost:8080" `
    -Method Post `
    -Body $payload `
    -ContentType "application/json"

Write-Host "Webhook sent successfully!" -ForegroundColor Green
