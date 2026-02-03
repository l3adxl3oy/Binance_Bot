@echo off
chcp 65001 > nul 2>&1
setlocal enabledelayedexpansion
title Binance Bot - Check Update
color 0B
cls

echo.
echo ========================================
echo    Check Update - Binance Bot
echo ========================================
echo.

REM Check Python installation
where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found
    echo.
    if exist "INSTALL.bat" (
        echo Running INSTALL.bat to setup system...
        echo.
        call INSTALL.bat
        exit /b 0
    ) else (
        echo Please install Python 3.8+ from https://www.python.org/downloads/
        echo Or run INSTALL.bat to setup system
        echo.
        pause
        exit /b 1
    )
)

REM Check Python version
echo Checking Python version...
python --version
echo.

REM Check for virtual environment
if exist ".venv\Scripts\activate.bat" (
    echo Activating Virtual Environment...
    call .venv\Scripts\activate.bat
    echo Virtual Environment activated
) else (
    echo Virtual Environment not found
    echo Using system Python...
)
echo.

REM Check and install required dependencies
echo Checking dependencies...
python -c "import requests" 2>nul
if errorlevel 1 (
    echo Installing requests...
    python -m pip install requests --quiet
)
echo.

REM Display current version
echo ========================================
echo    Current Version
echo ========================================
echo.
python -c "import version; print(f'Version: {version.__version__}'); print(f'Release Date: {version.RELEASE_DATE}'); print(f'Bot Name: {version.BOT_NAME}'); print(f'GitHub: {version.GITHUB_REPO_URL}')" 2>nul
if errorlevel 1 (
    echo [ERROR] Cannot read version information
    echo Please check version.py file
    echo.
    pause
    exit /b 1
)
echo.

REM Check for updates from GitHub
echo ========================================
echo    Checking for Updates from GitHub
echo ========================================
echo.
python -c "from utils.updater import BotUpdater; updater = BotUpdater(); update_info = updater.check_for_updates(); exit(0 if update_info else 1)"
set HAS_UPDATE=%ERRORLEVEL%

if %HAS_UPDATE% EQU 0 (
    echo.
    echo ========================================
    echo    New Version Available!
    echo ========================================
    echo.
    set /p choice="Do you want to update now? (y/n): "
    
    if /i "!choice!"=="y" goto AUTO_UPDATE
    if /i "!choice!"=="yes" goto AUTO_UPDATE
    
    echo.
    echo Skipping update
    echo You can run this file again to update anytime
    echo.
    goto EXIT
) else (
    echo.
    goto EXIT
)

:AUTO_UPDATE
echo.
echo ========================================
echo    Downloading and Updating
echo ========================================
echo.
echo System will backup data before update
echo.
python -m utils.updater --update
echo.
if errorlevel 1 (
    echo.
    echo [WARNING] Update failed
    echo.
) else (
    echo.
    echo [SUCCESS] Update completed!
    echo Please restart the program
    echo.
)
pause
goto EXIT

:EXIT
echo.
if exist ".venv\Scripts\deactivate.bat" (
    call .venv\Scripts\deactivate.bat
)
pause
exit /b 0
