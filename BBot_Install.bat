@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1
title Binance Bot - Complete Installation
color 0B
mode con: cols=110 lines=40

cls
echo.
echo ================================================================================
echo   BINANCE BOT - ONE-CLICK INSTALLER
echo ================================================================================
echo.
echo   This installer will automatically:
echo   [1] Check/Install Python
echo   [2] Check/Install Windows Terminal
echo   [3] Download Bot from GitHub (if needed)
echo   [4] Setup Virtual Environment
echo   [5] Install all dependencies
echo.
echo ================================================================================
echo.
echo Starting installation in 3 seconds...
timeout /t 3 >nul

REM ========================================
REM STEP 1: Check and Install Python
REM ========================================
:CHECK_PYTHON
cls
echo.
echo ================================================================================
echo   STEP 1/5: Checking Python Installation
echo ================================================================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Python not found!
    echo.
    echo Auto-opening Python download page...
    echo.
    echo IMPORTANT: During installation, CHECK "Add Python to PATH"!
    echo.
    start https://www.python.org/downloads/
    echo.
    echo Please install Python and run this installer again.
    echo.
    timeout /t 5 >nul
    exit /b 1
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo [SUCCESS] Python !PYTHON_VERSION! found!
    echo.
)

REM ========================================
REM STEP 2: Check and Install Windows Terminal
REM ========================================
:CHECK_TERMINAL
echo ================================================================================
echo   STEP 2/5: Checking Windows Terminal
echo ================================================================================
echo.

where wt.exe >nul 2>&1
if errorlevel 1 (
    echo [INFO] Windows Terminal not found. Installing automatically...
    echo.
    
    REM Check if winget is available
    where winget >nul 2>&1
    if errorlevel 1 (
        echo [INFO] winget not found. Opening Microsoft Store...
        echo Please install Windows Terminal from the store that opens...
        echo.
        start ms-windows-store://pdp/?ProductId=9N0DX20HK701
        echo.
        echo Waiting 5 seconds...
        timeout /t 5 >nul
    ) else (
        echo Installing Windows Terminal via winget...
        winget install --id Microsoft.WindowsTerminal -e --accept-package-agreements --accept-source-agreements --silent
        if errorlevel 1 (
            echo [WARNING] Auto-install failed. Opening Microsoft Store...
            start ms-windows-store://pdp/?ProductId=9N0DX20HK701
            echo.
            echo Waiting 5 seconds...
            timeout /t 5 >nul
        ) else (
            echo [SUCCESS] Windows Terminal installed!
            echo.
        )
    )
) else (
    echo [SUCCESS] Windows Terminal already installed!
    echo.
)

REM ========================================
REM STEP 3: Check and Download Bot from GitHub
REM ========================================
:CHECK_BOT_FILES
echo ================================================================================
echo   STEP 3/5: Checking Bot Files
echo ================================================================================
echo.

REM Check if we're in the bot directory
if exist "version.py" (
    echo [INFO] Bot files detected in current directory
    echo.
    goto :SETUP_VENV
)

REM Bot files not found - need to download
echo [INFO] Bot files not found. Downloading from GitHub...
echo.

REM Download latest release as ZIP (no git required)
set DOWNLOAD_URL=https://github.com/l3adxl3oy/Binance_Bot/archive/refs/heads/master.zip
set ZIP_FILE=bot_download.zip
set TEMP_DIR=bot_temp

echo [INFO] Downloading latest version...
powershell -Command "& {Invoke-WebRequest -Uri '%DOWNLOAD_URL%' -OutFile '%ZIP_FILE%'}" 2>nul
if errorlevel 1 (
    echo [ERROR] Failed to download! Trying alternative method...
    echo.
    REM Try with curl as fallback
    curl -L -o "%ZIP_FILE%" "%DOWNLOAD_URL%" 2>nul
    if errorlevel 1 (
        echo [ERROR] Download failed!
        echo.
        echo Opening GitHub releases page for manual download...
        start https://github.com/l3adxl3oy/Binance_Bot/releases/latest
        echo.
        echo Please download and extract manually, then run this installer again.
        timeout /t 5 >nul
        exit /b 1
    )
)

echo [SUCCESS] Download complete!
echo.

REM Extract ZIP
echo [INFO] Extracting files...
powershell -Command "& {Expand-Archive -Path '%ZIP_FILE%' -DestinationPath '%TEMP_DIR%' -Force}" 2>nul
if errorlevel 1 (
    echo [ERROR] Failed to extract!
    del "%ZIP_FILE%" 2>nul
    timeout /t 3 >nul
    exit /b 1
)

REM Move files from extracted folder to current directory or subfolder
for /d %%D in (%TEMP_DIR%\*) do (
    echo [INFO] Moving files...
    
    REM Check if current dir has only installer
    set FILE_COUNT=0
    for %%F in (*) do (
        if not "%%F"=="%ZIP_FILE%" if not "%%F"=="BBot_Install.bat" set /a FILE_COUNT+=1
    )
    
    if !FILE_COUNT! EQU 0 (
        REM Current dir is clean, move here
        xcopy "%%D\*" "." /E /I /Y >nul
        echo [SUCCESS] Bot installed in current directory!
    ) else (
        REM Current dir not clean, create subfolder
        set INSTALL_DIR=Binance_Bot
        if exist "!INSTALL_DIR!" (
            echo [WARNING] Folder !INSTALL_DIR! exists, updating...
            xcopy "%%D\*" "!INSTALL_DIR!" /E /I /Y >nul
        ) else (
            mkdir "!INSTALL_DIR!"
            xcopy "%%D\*" "!INSTALL_DIR!" /E /I /Y >nul
        )
        cd /d "!INSTALL_DIR!"
        echo [SUCCESS] Bot installed in !INSTALL_DIR!
    )
)

REM Cleanup
rmdir /s /q "%TEMP_DIR%" 2>nul
del "%ZIP_FILE%" 2>nul

echo.

REM ========================================
REM STEP 4: Setup Virtual Environment
REM ========================================
:SETUP_VENV
echo ================================================================================
echo   STEP 4/5: Setting up Virtual Environment
echo ================================================================================
echo.

if exist ".venv" (
    echo [INFO] Virtual environment already exists
    echo.
) else (
    echo [INFO] Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment!
        echo.
        pause
        exit /b 1
    )
    echo [SUCCESS] Virtual environment created!
    echo.
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment!
    pause
    exit /b 1
)
echo [SUCCESS] Virtual environment activated!
echo.

REM Upgrade pip
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip --quiet
if errorlevel 1 (
    echo [WARNING] Failed to upgrade pip, continuing anyway...
) else (
    echo [SUCCESS] Pip upgraded!
)
echo.

REM ========================================
REM STEP 5: Install Dependencies
REM ========================================
:INSTALL_DEPS
echo ================================================================================
echo   STEP 5/5: Installing Python Dependencies
echo ================================================================================
echo.

if not exist "requirements.txt" (
    echo [ERROR] requirements.txt not found!
    echo Please make sure you're in the bot directory.
    timeout /t 3 >nul
    exit /b 1
)

echo [INFO] Installing packages from requirements.txt...
echo This may take a few minutes...
echo.
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to install some packages!
    echo Please check your internet connection and try again.
    echo.
    timeout /t 5 >nul
    exit /b 1
)

echo.
echo [SUCCESS] All packages installed successfully!
echo.

REM ========================================
REM Installation Complete
REM ========================================
:COMPLETE
cls
echo.
echo ================================================================================
echo   INSTALLATION COMPLETE!
echo ================================================================================
echo.
echo [SUCCESS] Binance Bot ติดตั้งเรียบร้อยแล้ว!
echo.
echo ================================================================================
echo   ขั้นตอนถัดไป:
echo ================================================================================
echo.
echo   1. ตั้งค่า API Keys:
echo      - เปิดไฟล์: config\config.py
echo      - ใส่ Binance API Key และ Secret Key
echo      - บันทึกไฟล์
echo.
echo   2. รันบอท:
echo      - RUN_IN_TERMINAL.bat (แนะนำ - รองรับภาษาไทย)
echo      - RUN_BOT.bat (สำหรับ CMD ธรรมดา)
echo.
echo   3. ตรวจสอบอัพเดท:
echo      - CheckUpdate.bat (เช็คและอัพเดทเวอร์ชันใหม่)
echo.
echo ================================================================================
echo   เคล็ดลับ:
echo ================================================================================
echo.
echo   - ใช้ Windows Terminal เพื่อแสดงผลภาษาไทยได้ชัดเจน
echo   - อัพเดทบอทผ่าน CheckUpdate.bat เป็นประจำ
echo   - ดูคู่มือใน docs\ สำหรับข้อมูลเพิ่มเติม
echo.
echo ================================================================================
echo.

REM Check if config.py exists
if exist "config\config.py" (
    echo [INFO] Opening config.py for you to set up API keys...
    echo.
    timeout /t 2 >nul
    start notepad config\config.py
)

echo.
echo Installation complete! Window will close in 10 seconds...
echo Or press any key to close now...
timeout /t 10 >nul

REM Deactivate virtual environment
if exist ".venv\Scripts\deactivate.bat" (
    call .venv\Scripts\deactivate.bat
)

exit /b 0
