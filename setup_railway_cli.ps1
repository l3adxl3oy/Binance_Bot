# ========================================================================
#   RAILWAY AUTO-SETUP SCRIPT - ONE-CLICK DEPLOYMENT
# ========================================================================
# This script will:
# 1. Check/Install Railway CLI
# 2. Login to Railway
# 3. Link your project
# 4. Set all environment variables automatically
# 5. Deploy your app
# ========================================================================

param(
    [string]$BinanceApiKey,
    [string]$BinanceApiSecret,
    [switch]$SkipBinanceKeys
)

Write-Host "`n========================================================================" -ForegroundColor Cyan
Write-Host "   RAILWAY AUTO-SETUP - FULL DEPLOYMENT AUTOMATION" -ForegroundColor Yellow
Write-Host "========================================================================`n" -ForegroundColor Cyan

# ==================== STEP 1: Check Railway CLI ====================
Write-Host "[STEP 1/6] Checking Railway CLI..." -ForegroundColor Cyan

$railwayExists = Get-Command railway -ErrorAction SilentlyContinue

if (-not $railwayExists) {
    Write-Host "  Railway CLI not found. Installing..." -ForegroundColor Yellow
    
    # Check if npm exists
    $npmExists = Get-Command npm -ErrorAction SilentlyContinue
    
    if ($npmExists) {
        Write-Host "  Installing Railway CLI via npm..." -ForegroundColor Cyan
        try {
            npm install -g @railway/cli
            Write-Host "  [SUCCESS] Railway CLI installed!" -ForegroundColor Green
        } catch {
            Write-Host "  [ERROR] Failed to install Railway CLI" -ForegroundColor Red
            Write-Host "  Please install manually: npm install -g @railway/cli" -ForegroundColor Yellow
            exit 1
        }
    } else {
        Write-Host "  [ERROR] npm not found!" -ForegroundColor Red
        Write-Host "`n  Please install Node.js first:" -ForegroundColor Yellow
        Write-Host "    https://nodejs.org/`n" -ForegroundColor White
        Write-Host "  Then run this script again." -ForegroundColor Yellow
        Write-Host "`n  OR set variables manually at:" -ForegroundColor Cyan
        Write-Host "    https://railway.app/dashboard`n" -ForegroundColor White
        exit 1
    }
} else {
    Write-Host "  [OK] Railway CLI found!" -ForegroundColor Green
}

# ==================== STEP 2: Login to Railway ====================
Write-Host "`n[STEP 2/6] Logging into Railway..." -ForegroundColor Cyan

try {
    $loginResult = railway whoami 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] Already logged in!" -ForegroundColor Green
    } else {
        Write-Host "  Please login to Railway (browser will open)..." -ForegroundColor Yellow
        railway login
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  [SUCCESS] Login successful!" -ForegroundColor Green
        } else {
            Write-Host "  [ERROR] Login failed" -ForegroundColor Red
            exit 1
        }
    }
} catch {
    Write-Host "  [ERROR] Failed to check login status" -ForegroundColor Red
    exit 1
}

# ==================== STEP 3: Link Project ====================
Write-Host "`n[STEP 3/6] Linking to Railway project..." -ForegroundColor Cyan

try {
    $linkStatus = railway status 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] Project already linked!" -ForegroundColor Green
    } else {
        Write-Host "  Please select your project..." -ForegroundColor Yellow
        railway link
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  [SUCCESS] Project linked!" -ForegroundColor Green
        } else {
            Write-Host "  [ERROR] Failed to link project" -ForegroundColor Red
            exit 1
        }
    }
} catch {
    Write-Host "  [WARNING] Could not verify project link" -ForegroundColor Yellow
}

# ==================== STEP 4: Prompt for Binance Keys ====================
Write-Host "`n[STEP 4/6] Binance API Keys..." -ForegroundColor Cyan

if (-not $SkipBinanceKeys) {
    if (-not $BinanceApiKey) {
        Write-Host "`n  Enter your Binance API Key (or press Enter to skip):" -ForegroundColor Yellow
        Write-Host "  Testnet keys: https://testnet.binance.vision/" -ForegroundColor Gray
        $BinanceApiKey = Read-Host "  API Key"
    }
    
    if (-not $BinanceApiSecret -and $BinanceApiKey) {
        Write-Host "`n  Enter your Binance API Secret:" -ForegroundColor Yellow
        $BinanceApiSecret = Read-Host "  API Secret" -AsSecureString
        $BinanceApiSecret = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($BinanceApiSecret))
    }
}

# ==================== STEP 5: Set Environment Variables ====================
Write-Host "`n[STEP 5/6] Setting environment variables..." -ForegroundColor Cyan

# All environment variables
$envVars = @{
    "JWT_SECRET_KEY" = "S9RCVkYrP0kpKmTaLFZXV9GeUG4oOKbNxM52dZJ5twwD0ZPx"
    "ENCRYPTION_KEY" = "k8LecZ7m5qZ15Ul31fZILAO8GL1fi7GK"
    "BINANCE_BASE_URL" = "https://testnet.binance.vision"
    "TELEGRAM_ENABLED" = "false"
}

# Add Binance keys if provided
if ($BinanceApiKey) {
    $envVars["BINANCE_API_KEY"] = $BinanceApiKey
}
if ($BinanceApiSecret) {
    $envVars["BINANCE_API_SECRET"] = $BinanceApiSecret
}

# Set each variable
$success = 0
$failed = 0
$total = $envVars.Count

foreach ($key in $envVars.Keys) {
    $displayKey = $key
    if ($key -match "SECRET|KEY" -and $key -ne "JWT_SECRET_KEY" -and $key -ne "ENCRYPTION_KEY") {
        $displayValue = "***hidden***"
    } else {
        $displayValue = $envVars[$key].Substring(0, [Math]::Min(30, $envVars[$key].Length)) + "..."
    }
    
    Write-Host "  Setting $displayKey..." -NoNewline -ForegroundColor Cyan
    try {
        $result = railway variables set "$key=$($envVars[$key])" 2>&1
        if ($LASTEXITCODE -eq 0 -or $result -like "*success*") {
            Write-Host " [OK]" -ForegroundColor Green
            $success++
        } else {
            Write-Host " [FAILED]" -ForegroundColor Red
            $failed++
        }
    } catch {
        Write-Host " [FAILED]" -ForegroundColor Red
        $failed++
    }
    
    Start-Sleep -Milliseconds 500
}

# ==================== STEP 6: Deploy ====================
Write-Host "`n[STEP 6/6] Triggering deployment..." -ForegroundColor Cyan

try {
    Write-Host "  Pushing to trigger Railway deployment..." -ForegroundColor Cyan
    $deployResult = railway up 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [SUCCESS] Deployment triggered!" -ForegroundColor Green
    } else {
        Write-Host "  [INFO] Using git push instead..." -ForegroundColor Yellow
        git push origin master
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  [SUCCESS] Git push successful - Railway will deploy automatically!" -ForegroundColor Green
        }
    }
} catch {
    Write-Host "  [WARNING] Could not trigger deployment automatically" -ForegroundColor Yellow
    Write-Host "  Railway will deploy automatically from git push" -ForegroundColor Cyan
}

# ==================== SUMMARY ====================
Write-Host "`n========================================================================" -ForegroundColor Cyan
Write-Host "   SETUP COMPLETE!" -ForegroundColor Green
Write-Host "========================================================================" -ForegroundColor Cyan

Write-Host "`n[ENVIRONMENT VARIABLES]" -ForegroundColor Yellow
Write-Host "  Variables set: $success/$total" -ForegroundColor $(if($success -eq $total){"Green"}else{"Yellow"})
if ($failed -gt 0) {
    Write-Host "  Failed: $failed" -ForegroundColor Red
}

if ($BinanceApiKey) {
    Write-Host "`n  [OK] Binance API keys configured" -ForegroundColor Green
} else {
    Write-Host "`n  [WARNING] Binance API keys not set!" -ForegroundColor Yellow
    Write-Host "  Set them with:" -ForegroundColor Cyan
    Write-Host "    railway variables set BINANCE_API_KEY=your_key" -ForegroundColor White
    Write-Host "    railway variables set BINANCE_API_SECRET=your_secret" -ForegroundColor White
}

Write-Host "`n[NEXT STEPS]" -ForegroundColor Yellow
Write-Host "  1. Wait for Railway deployment (2-3 minutes)" -ForegroundColor White
Write-Host "  2. Check logs: railway logs" -ForegroundColor White
Write-Host "  3. Visit: https://web-production-05f5f.up.railway.app" -ForegroundColor White
Write-Host "  4. Create account and start trading!" -ForegroundColor White

Write-Host "`n[USEFUL COMMANDS]" -ForegroundColor Cyan
Write-Host "  railway logs              - View deployment logs" -ForegroundColor White
Write-Host "  railway variables         - List all variables" -ForegroundColor White
Write-Host "  railway open              - Open app in browser" -ForegroundColor White
Write-Host "  railway status            - Check deployment status" -ForegroundColor White

Write-Host "`n========================================================================" -ForegroundColor Cyan
Write-Host "   Your Trading Bot is being deployed! " -NoNewline -ForegroundColor Yellow
Write-Host "" -ForegroundColor Yellow
Write-Host "========================================================================`n" -ForegroundColor Cyan
