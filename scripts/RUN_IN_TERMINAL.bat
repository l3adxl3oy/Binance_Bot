@echo off
chcp 65001 >nul 2>&1
REM ========================================
REM Force run in Windows Terminal with Auto-Update
REM ========================================

REM Check for updates before launching bot
echo.
echo ========================================
echo   Checking for updates...
echo ========================================
echo.

cd /d "%~dp0"

REM Activate virtual environment for update check
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat >nul 2>&1
)

REM Run update checker
if exist .venv\Scripts\python.exe (
    .venv\Scripts\python.exe -m utils.updater
    if errorlevel 1 (
        echo.
        echo WARNING: Unable to check for updates
        echo.
    )
) else (
    echo WARNING: Python environment not found
    echo Please run INSTALL.bat first
    pause
    exit /b 1
)

echo.
echo ========================================

REM Check if Windows Terminal is available
where wt.exe >nul 2>&1
if errorlevel 1 (
    echo Windows Terminal not found!
    echo Please install from Microsoft Store
    echo or run INSTALL.bat
    echo.
    pause
    exit /b 1
)

REM ========================================
REM   BOT SELECTION MENU
REM ========================================
echo.
echo ================================================================================
echo   Select Bot to Run
echo ================================================================================
echo.
echo [1] Daily Scalping Bot (Recommended for Beginners)
echo     - Strategy: Balanced between safety and profit
echo     - TP: 1.2-2.0%% (Moderate)
echo     - SL: 1.0%% (Standard)
echo     - Target: +2-5%% per day
echo     - Best for: Beginners, stable trading
echo.
echo [2] Aggressive Recovery Bot (High Risk - Experienced Traders)
echo     - Strategy: Fast profit + Smart loss recovery
echo     - TP: 1.2-2.5%% (Better RR)
echo     - SL: 0.6-1.0%% (Safe)
echo     - Recovery: Smart Martingale 1.3x (Max 2 levels)
echo     - Target: +5%% then stop immediately
echo     - Best for: Experienced traders, accept high risk
echo.
echo [3] Cancel
echo.
echo ================================================================================

set /p BOT_CHOICE="Please select (1/2/3): "

if "%BOT_CHOICE%"=="1" (
    echo.
    echo ================================================================================
    echo Starting Daily Scalping Bot...
    echo ================================================================================
    wt.exe --title "Daily Scalping Bot" -d "%CD%" cmd /k "RUN_BOT.bat"
    goto :end
)

if "%BOT_CHOICE%"=="2" (
    echo.
    echo ================================================================================
    echo WARNING: You selected Aggressive Recovery Bot (High Risk)
    echo ================================================================================
    echo.
    echo Important Warning:
    echo    * This bot uses Smart Martingale 1.3x (Max 2 levels)
    echo    * May increase position size to recover losses
    echo    * Higher risk than Daily Bot
    echo    * Target: 5%% profit then stop immediately
    echo    * Recommended: Test in DEMO MODE first before using real money
    echo.
    echo ================================================================================
    set /p CONFIRM="Confirm to use this bot? (Y/N): "
    
    if /i "%CONFIRM%"=="Y" (
        echo.
        echo ================================================================================
        echo Starting Aggressive Recovery Bot...
        echo ================================================================================
        wt.exe --title "Aggressive Recovery Bot" -d "%CD%" cmd /k ".venv\Scripts\python.exe bots\aggressive_recovery_bot.py"
        goto :end
    ) else (
        echo.
        echo ================================================================================
        echo Cancelled
        echo ================================================================================
        pause
        goto :end
    )
)

if "%BOT_CHOICE%"=="3" (
    echo.
    echo ================================================================================
    echo Cancelled
    echo ================================================================================
    goto :end
)

echo.
echo ================================================================================
echo Invalid choice. Please select 1, 2, or 3
echo ================================================================================
pause
goto :end

:end
