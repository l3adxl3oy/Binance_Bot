# Railway Environment Variables Setup Script
# PowerShell script to set all environment variables using Railway CLI

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   Railway Environment Setup" -ForegroundColor Yellow
Write-Host "========================================`n" -ForegroundColor Cyan

# Check if Railway CLI is installed
$railwayExists = Get-Command railway -ErrorAction SilentlyContinue

if (-not $railwayExists) {
    Write-Host "[ERROR] Railway CLI not found!" -ForegroundColor Red
    Write-Host "`nPlease install Railway CLI first:" -ForegroundColor Yellow
    Write-Host "  npm install -g @railway/cli" -ForegroundColor White
    Write-Host "`nOr set variables manually at:" -ForegroundColor Yellow
    Write-Host "  https://railway.app/dashboard" -ForegroundColor White
    Write-Host "`nSee RAILWAY_ENV_SETUP.txt for details`n" -ForegroundColor Cyan
    exit 1
}

Write-Host "[INFO] Railway CLI found!" -ForegroundColor Green
Write-Host "[INFO] Setting environment variables...`n" -ForegroundColor Cyan

# Environment Variables
$envVars = @{
    "JWT_SECRET_KEY" = "S9RCVkYrP0kpKmTaLFZXV9GeUG4oOKbNxM52dZJ5twwD0ZPx"
    "ENCRYPTION_KEY" = "k8LecZ7m5qZ15Ul31fZILAO8GL1fi7GK"
    "BINANCE_BASE_URL" = "https://testnet.binance.vision"
    "TELEGRAM_ENABLED" = "false"
}

# Set each variable
$success = 0
$failed = 0

foreach ($key in $envVars.Keys) {
    Write-Host "Setting $key..." -NoNewline -ForegroundColor Cyan
    try {
        railway variables set "$key=$($envVars[$key])" 2>&1 | Out-Null
        Write-Host " [OK]" -ForegroundColor Green
        $success++
    } catch {
        Write-Host " [FAILED]" -ForegroundColor Red
        $failed++
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   Setup Complete" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Variables set: $success" -ForegroundColor Green
Write-Host "Failed: $failed" -ForegroundColor $(if($failed -gt 0){"Red"}else{"Green"})

Write-Host "`n[IMPORTANT] You still need to set manually:" -ForegroundColor Yellow
Write-Host "  1. BINANCE_API_KEY=your_real_api_key" -ForegroundColor White
Write-Host "  2. BINANCE_API_SECRET=your_real_api_secret" -ForegroundColor White

Write-Host "`nSet them using:" -ForegroundColor Cyan
Write-Host "  railway variables set BINANCE_API_KEY=your_key" -ForegroundColor White
Write-Host "  railway variables set BINANCE_API_SECRET=your_secret" -ForegroundColor White

Write-Host "`nOr via Railway Dashboard:" -ForegroundColor Cyan
Write-Host "  https://railway.app/dashboard`n" -ForegroundColor White
