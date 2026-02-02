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

echo [INFO] Python found. Installing packages...
echo.

REM Check if Windows Terminal is installed
echo [STEP 1/3] Checking Windows Terminal...
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

REM Install Python packages
echo [STEP 2/3] Installing Python packages...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo ======================================
echo   Installation Complete!
echo ======================================
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
echo.

pause
