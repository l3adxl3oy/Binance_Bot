@echo off
chcp 65001 >nul 2>&1
REM ========================================
REM Force run in Windows Terminal
REM ========================================

where wt.exe >nul 2>&1
if errorlevel 1 (
    echo ไม่พบ Windows Terminal!
    echo กรุณาติดตั้งจาก Microsoft Store
    echo หรือรัน INSTALL.bat
    echo.
    pause
    exit /b 1
)

echo เปิด Bot ใน Windows Terminal...
wt.exe --title "Binance Bot" -d "%CD%" cmd /k RUN_BOT.bat
