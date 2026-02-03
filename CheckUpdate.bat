@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul
title Binance Bot - ตรวจสอบและอัพเดทอัตโนมัติ
color 0B

echo.
echo ========================================
echo   🔍 ตรวจสอบและอัพเดท Binance Bot
echo ========================================
echo.

REM ตรวจสอบว่ามี Python หรือไม่
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ ไม่พบ Python ในระบบ
    echo.
    if exist "INSTALL.bat" (
        echo 🔧 กำลังเรียกใช้ INSTALL.bat เพื่อติดตั้งระบบ...
        echo.
        call INSTALL.bat
        exit /b 0
    ) else (
        echo กรุณาติดตั้ง Python 3.8+ จาก https://www.python.org/downloads/
        echo หรือรัน INSTALL.bat เพื่อติดตั้งระบบ
        echo.
        pause
        exit /b 1
    )
)

REM ตรวจสอบเวอร์ชัน Python
echo 🐍 ตรวจสอบเวอร์ชัน Python...
python --version
echo.

REM ตรวจสอบว่ามี virtual environment หรือไม่
if exist ".venv\Scripts\activate.bat" (
    echo 🔧 เปิดใช้งาน Virtual Environment...
    call .venv\Scripts\activate.bat
    echo ✅ Virtual Environment เปิดใช้งานแล้ว
) else (
    echo ⚠️ ไม่พบ Virtual Environment
    echo กำลังใช้ Python ของระบบ...
)
echo.

REM ตรวจสอบและติดตั้ง dependencies ที่จำเป็น
echo 📦 ตรวจสอบ dependencies...
python -c "import requests" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️ กำลังติดตั้ง requests...
    python -m pip install requests --quiet
)
echo.

REM แสดงเวอร์ชันปัจจุบัน
echo ========================================
echo   📋 เวอร์ชันปัจจุบัน
echo ========================================
echo.
python -c "import version; print(f'Version: {version.__version__}'); print(f'Release Date: {version.RELEASE_DATE}'); print(f'Bot Name: {version.BOT_NAME}'); print(f'GitHub: {version.GITHUB_REPO_URL}')" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ ไม่สามารถอ่านข้อมูลเวอร์ชันได้
    echo กรุณาตรวจสอบไฟล์ version.py
    echo.
    pause
    exit /b 1
)
echo.

REM ตรวจสอบอัพเดทอัตโนมัติ
echo ========================================
echo   🔍 ตรวจสอบอัพเดทจาก GitHub
echo ========================================
echo.
python -c "from utils.updater import BotUpdater; updater = BotUpdater(); update_info = updater.check_for_updates(); exit(0 if update_info else 1)"
set HAS_UPDATE=%ERRORLEVEL%

if %HAS_UPDATE% EQU 0 (
    echo.
    echo ========================================
    echo   🆕 มีเวอร์ชันใหม่!
    echo ========================================
    echo.
    set /p choice="❓ ต้องการอัพเดทเลยไหม? (y/n): "
    
    if /i "!choice!"=="y" goto AUTO_UPDATE
    if /i "!choice!"=="yes" goto AUTO_UPDATE
    if /i "!choice!"=="ใช่" goto AUTO_UPDATE
    
    echo.
    echo ⏭️ ข้ามการอัพเดท
    echo 💡 สามารถรันไฟล์นี้อีกครั้งเพื่ออัพเดทได้ทุกเมื่อ
    echo.
    goto EXIT
) else (
    echo.
    goto EXIT
)

:AUTO_UPDATE
echo.
echo ========================================
echo   🔄 กำลังดาวน์โหลดและอัพเดท
echo ========================================
echo.
echo ⚠️ ระบบจะสำรองข้อมูลก่อนอัพเดท
echo.
python -m utils.updater --update
echo.
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ อัพเดทสำเร็จ!
    echo 🔄 กรุณาปิดและเปิดโปรแกรมใหม่
    echo.
) else (
    echo.
    echo ⚠️ การอัพเดทล้มเหลว
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
