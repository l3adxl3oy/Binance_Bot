@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1
title Binance Trading Bot - Main Menu
color 0B
mode con: cols=100 lines=40
REM ========================================
REM Main Menu - Bot Control & Documentation
REM ========================================

:MAIN_MENU
cls
echo.
echo ================================================================================
echo   BINANCE TRADING BOT - MAIN MENU
echo ================================================================================
echo.
echo   Select an option:
echo.
echo   [1] Start Trading Bot
echo   [2] View Bot Documentation
echo   [3] Setup Guides
echo   [4] View Backtest Results
echo   [5] About ^& Version
echo   [6] Exit
echo.
echo ================================================================================
echo.

set /p MENU_CHOICE="Please select (1-6): "

if "%MENU_CHOICE%"=="1" goto :BOT_MENU
if "%MENU_CHOICE%"=="2" goto :DOC_MENU
if "%MENU_CHOICE%"=="3" goto :SETUP_MENU
if "%MENU_CHOICE%"=="4" goto :BACKTEST_MENU
if "%MENU_CHOICE%"=="5" goto :ABOUT_MENU
if "%MENU_CHOICE%"=="6" goto :EXIT

echo Invalid choice. Please try again.
timeout /t 2 >nul
goto :MAIN_MENU

REM ========================================
REM   BOT SELECTION MENU
REM ========================================
:BOT_MENU
cls
cd /d "%~dp0"

REM Check for updates before launching bot
echo.
echo ========================================
echo   Checking for updates...
echo ========================================
echo.

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
    goto :MAIN_MENU
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
    goto :MAIN_MENU
)

echo.
echo ================================================================================
echo   SELECT BOT TO RUN
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
echo [3] Back to Main Menu
echo.
echo ================================================================================

set /p BOT_CHOICE="Please select (1/2/3): "

if "%BOT_CHOICE%"=="1" (
    echo.
    echo ================================================================================
    echo Starting Daily Scalping Bot...
    echo ================================================================================
    wt.exe --title "Daily Scalping Bot" -d "%CD%" cmd /k "RUN_BOT.bat"
    goto :END_SCRIPT
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
    set /p CONFIRM="Type YES to confirm and start: "
    if /i "!CONFIRM!"=="YES" (
        echo.
        echo ================================================================================
        echo Starting Aggressive Recovery Bot...
        echo ================================================================================
        wt.exe --title "Aggressive Recovery Bot" -d "%CD%" cmd /k ".venv\Scripts\python.exe bots\aggressive_recovery_bot.py"
        goto :END_SCRIPT
    ) else (
        echo.
        echo Cancelled. Returning to main menu...
        timeout /t 2 >nul
        goto :MAIN_MENU
    )
)

if "%BOT_CHOICE%"=="3" goto :MAIN_MENU

echo Invalid choice. Please try again.
timeout /t 2 >nul
goto :BOT_MENU

REM ========================================
REM   DOCUMENTATION MENU
REM ========================================
:DOC_MENU
cls
echo.
echo ================================================================================
echo   BOT DOCUMENTATION
echo ================================================================================
echo.
echo   [1] Daily Scalping Bot - Full Specifications
echo   [2] Aggressive Recovery Bot - Full Specifications
echo   [3] Bot Comparison Guide
echo   [4] Quick Bot Selection Guide
echo   [5] Strategy Analysis (Technical Details)
echo   [6] Intelligent Features Overview
echo   [7] Folder Structure Guide
echo   [8] Back to Main Menu
echo.
echo ================================================================================
echo.

set /p DOC_CHOICE="Please select (1-8): "

if "%DOC_CHOICE%"=="1" (
    start "" "docs\BOT_SPECS_DAILY_SCALPING.md"
    goto :DOC_MENU
)

if "%DOC_CHOICE%"=="2" (
    start "" "docs\BOT_SPECS_AGGRESSIVE_RECOVERY.md"
    goto :DOC_MENU
)

if "%DOC_CHOICE%"=="3" (
    start "" "docs\BOT_COMPARISON.md"
    goto :DOC_MENU
)

if "%DOC_CHOICE%"=="4" (
    start "" "docs\QUICK_BOT_SELECTION.md"
    goto :DOC_MENU
)

if "%DOC_CHOICE%"=="5" (
    start "" "docs\STRATEGY_ANALYSIS_V3.md"
    goto :DOC_MENU
)

if "%DOC_CHOICE%"=="6" (
    start "" "docs\INTELLIGENT_FEATURES.md"
    goto :DOC_MENU
)

if "%DOC_CHOICE%"=="7" (
    start "" "docs\FOLDER_STRUCTURE.md"
    goto :DOC_MENU
)

if "%DOC_CHOICE%"=="8" goto :MAIN_MENU

echo Invalid choice. Please try again.
timeout /t 2 >nul
goto :DOC_MENU

REM ========================================
REM   SETUP GUIDES MENU
REM ========================================
:SETUP_MENU
cls
echo.
echo ================================================================================
echo   SETUP GUIDES
echo ================================================================================
echo.
echo   [1] Quick Start Guide
echo   [2] Complete Setup Guide
echo   [3] Telegram Setup Guide (with Commands)
echo   [4] Auto-Update Guide
echo   [5] Backtest Guide
echo   [6] Back to Main Menu
echo.
echo ================================================================================
echo.

set /p SETUP_CHOICE="Please select (1-6): "

if "%SETUP_CHOICE%"=="1" (
    start "" "docs\QUICK_START_V2.md"
    goto :SETUP_MENU
)

if "%SETUP_CHOICE%"=="2" (
    start "" "docs\SETUP_GUIDE.md"
    goto :SETUP_MENU
)

if "%SETUP_CHOICE%"=="3" (
    start "" "docs\TELEGRAM_SETUP.md"
    goto :SETUP_MENU
)

if "%SETUP_CHOICE%"=="4" (
    start "" "docs\AUTO_UPDATE_GUIDE.md"
    goto :SETUP_MENU
)

if "%SETUP_CHOICE%"=="5" (
    start "" "docs\BACKTEST_GUIDE.md"
    goto :SETUP_MENU
)

if "%SETUP_CHOICE%"=="6" goto :MAIN_MENU

echo Invalid choice. Please try again.
timeout /t 2 >nul
goto :SETUP_MENU

REM ========================================
REM   BACKTEST RESULTS MENU
REM ========================================
:BACKTEST_MENU
cls
echo.
echo ================================================================================
echo   BACKTEST RESULTS
echo ================================================================================
echo.
echo   [1] Open Backtest Reports Folder
echo   [2] Run New Backtest (Daily Scalping Bot)
echo   [3] Run New Backtest (Aggressive Recovery Bot)
echo   [4] View Backtest Results
echo   [5] Back to Main Menu
echo.
echo ================================================================================
echo.

set /p BACK_CHOICE="Please select (1-5): "

if "%BACK_CHOICE%"=="1" (
    start "" "backtest\reports"
    goto :BACKTEST_MENU
)

if "%BACK_CHOICE%"=="2" (
    echo.
    echo Running backtest for Daily Scalping Bot...
    call .venv\Scripts\activate.bat
    .venv\Scripts\python.exe scripts\run_backtest.py
    pause
    goto :BACKTEST_MENU
)

if "%BACK_CHOICE%"=="3" (
    echo.
    echo Running backtest for Aggressive Recovery Bot...
    call .venv\Scripts\activate.bat
    .venv\Scripts\python.exe scripts\run_backtest_aggressive.py
    pause
    goto :BACKTEST_MENU
)

if "%BACK_CHOICE%"=="4" (
    start "" "backtest\results"
    goto :BACKTEST_MENU
)

if "%BACK_CHOICE%"=="5" goto :MAIN_MENU

echo Invalid choice. Please try again.
timeout /t 2 >nul
goto :BACKTEST_MENU

REM ========================================
REM   ABOUT MENU
REM ========================================
:ABOUT_MENU
cls
echo.
echo ================================================================================
echo   ABOUT BINANCE TRADING BOT
echo ================================================================================
echo.

if exist .venv\Scripts\python.exe (
    call .venv\Scripts\activate.bat >nul 2>&1
    .venv\Scripts\python.exe -c "from version import __version__, BOT_NAME; print(f'  Bot Name: {BOT_NAME}'); print(f'  Version: {__version__}')"
) else (
    echo   Bot Name: Binance Trading Bot
    echo   Version: 3.0+
)

echo.
echo   Description: Advanced AI-powered trading bot for Binance
echo   Features:
echo     - Multi-symbol trading (20+ pairs)
echo     - AI adaptive strategy
echo     - Smart risk management
echo     - Telegram notifications
echo     - Backtesting support
echo.
echo   Documentation: docs\
echo   License: See LICENSE.txt
echo   Terms: See TERMS_OF_USE.md
echo.
echo ================================================================================
echo.
echo   [1] View README
echo   [2] View License
echo   [3] View Terms of Use
echo   [4] View Changelog
echo   [5] Back to Main Menu
echo.
echo ================================================================================
echo.

set /p ABOUT_CHOICE="Please select (1-5): "

if "%ABOUT_CHOICE%"=="1" (
    start "" "README.md"
    goto :ABOUT_MENU
)

if "%ABOUT_CHOICE%"=="2" (
    start "" "LICENSE.txt"
    goto :ABOUT_MENU
)

if "%ABOUT_CHOICE%"=="3" (
    start "" "docs\TERMS_OF_USE.md"
    goto :ABOUT_MENU
)

if "%ABOUT_CHOICE%"=="4" (
    start "" "docs\CHANGELOG_v3.0.md"
    goto :ABOUT_MENU
)

if "%ABOUT_CHOICE%"=="5" goto :MAIN_MENU

echo Invalid choice. Please try again.
timeout /t 2 >nul
goto :ABOUT_MENU

REM ========================================
REM   EXIT
REM ========================================
:EXIT
cls
echo.
echo ================================================================================
echo   Thank you for using Binance Trading Bot!
echo ================================================================================
echo.
timeout /t 2 >nul
exit /b 0

:END_SCRIPT
echo.
echo Bot launched in Windows Terminal.
echo You can close this window now.
echo.
pause
exit /b 0
