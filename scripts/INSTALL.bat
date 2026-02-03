@echo off
chcp 65001 >nul 2>&1
title Binance Bot - Installation
color 0B
mode con: cols=100 lines=35
REM ========================================
REM ติดตั้ง Python Packages สำหรับ Bot
REM ========================================
cls
echo.
echo ======================================
echo   Installing Bot Dependencies...
echo ======================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed!
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [INFO] Python found. Starting installation...
echo.

REM Check if Windows Terminal is installed
echo [STEP 1/4] Checking Windows Terminal...
where wt.exe >nul 2>&1
if errorlevel 1 (
    echo [INFO] Windows Terminal not found. Installing...
    echo.
    winget install --id Microsoft.WindowsTerminal -e --accept-package-agreements --accept-source-agreements
    if errorlevel 1 (
        echo [WARNING] ไม่สามารถติดตั้ง Windows Terminal อัตโนมัติได้
        echo กรุณาติดตั้งเองจาก Microsoft Store: ms-windows-store://pdp/?ProductId=9N0DX20HK701
        echo หรือใช้ CMD ธรรมดาก็ได้ (แต่ภาษาไทยอาจเพี้ยน)
        echo.
        timeout /t 3 >nul
    ) else (
        echo [SUCCESS] Windows Terminal ติดตั้งเรียบร้อย!
        echo.
    )
) else (
    echo [SUCCESS] Windows Terminal ติดตั้งอยู่แล้ว!
    echo.
)

REM Create virtual environment
echo [STEP 2/4] Creating virtual environment...
if exist .venv (
    echo [INFO] Virtual environment already exists. Skipping creation...
    echo.
) else (
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment!
        echo กรุณาตรวจสอบว่า Python ติดตั้งถูกต้อง
        pause
        exit /b 1
    )
    echo [SUCCESS] Virtual environment created!
    echo.
)

REM Activate virtual environment and upgrade pip
echo [STEP 3/4] Upgrading pip...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment!
    pause
    exit /b 1
)

python -m pip install --upgrade pip >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Failed to upgrade pip, continuing anyway...
) else (
    echo [SUCCESS] Pip upgraded!
)
echo.

REM Install Python packages
echo [STEP 4/4] Installing Python packages...
echo.
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to install some packages!
    echo กรุณาตรวจสอบ requirements.txt และเชื่อมต่ออินเทอร์เน็ต
    echo.
    pause
    exit /b 1
)

echo.
echo ======================================
echo   Installation Complete!
echo ======================================
echo.
echo [SUCCESS] ทุกอย่างติดตั้งสำเร็จแล้ว!
echo.
echo ขั้นตอนถัดไป:
echo 1. แก้ไขไฟล์ config\config.py ใส่ Binance API keys
echo 2. รัน Bot:
echo    - RUN_BOT.bat (CMD ธรรมดา)
echo    - RUN_IN_TERMINAL.bat (Windows Terminal - แนะนำ)
echo.
echo เคล็ดลับ:
echo - ใช้ Windows Terminal เพื่อแสดงภาษาไทยชัดเจน
echo - ใช้ CMD ธรรมดาถ้า Terminal มีปัญหา
echo - Virtual environment จะถูก activate อัตโนมัติเมื่อรัน Bot
echo.

pause
