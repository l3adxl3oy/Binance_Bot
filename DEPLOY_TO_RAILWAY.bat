@echo off
REM ========================================================================
REM   ONE-CLICK RAILWAY DEPLOYMENT
REM   Double-click this file to deploy automatically!
REM ========================================================================

echo.
echo ========================================================================
echo    RAILWAY AUTO-DEPLOYMENT STARTING...
echo ========================================================================
echo.

REM Check if PowerShell is available
where powershell >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] PowerShell not found!
    echo Please run setup_railway_cli.ps1 manually
    pause
    exit /b 1
)

REM Run the PowerShell script
echo [INFO] Running automated setup...
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0setup_railway_cli.ps1"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================================================
    echo    DEPLOYMENT COMPLETE!
    echo ========================================================================
    echo.
    echo Your app is deploying to Railway!
    echo Check status at: https://railway.app/dashboard
    echo.
) else (
    echo.
    echo ========================================================================
    echo    DEPLOYMENT FAILED
    echo ========================================================================
    echo.
    echo Please check the errors above
    echo Or set variables manually at: https://railway.app/dashboard
    echo.
)

pause
