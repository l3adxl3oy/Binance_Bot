@echo off
chcp 65001 >nul 2>&1
title Binance Daily Scalping Bot
color 0A
mode con: cols=120 lines=40
REM ========================================
REM Run Daily Scalping Bot (Multi-symbol)
REM ========================================
cls
echo.
echo ========================================
echo   BINANCE DAILY SCALPING BOT
echo ========================================
echo.
echo Bot Type: Multi-Symbol Trading
echo Timeframe: 1 minute (Ultra-Fast)
echo Strategy: Multi-Indicator Confluence
echo Target: 2-5%% daily profit
echo.
echo ========================================
echo   🛡️ วิธีปิด Bot อย่างปลอดภัย:
echo   ✅ กด Ctrl+C (Bot จะปิด positions ทั้งหมดอัตโนมัติ)
echo   ❌ ห้ามกดปุ่ม X หรือปิดหน้าต่าง (Positions จะค้าง!)
echo ========================================
echo.
echo กด Ctrl+C เพื่อหยุด Bot
echo Press Ctrl+C to stop the bot
echo.
echo ========================================
echo.

cd /d "%~dp0"

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Run bot with virtual environment Python
.venv\Scripts\python.exe bots\daily_scalping_bot.py

echo.
echo ========================================
echo   Bot หยุดทำงานแล้ว / Bot Stopped
echo ========================================
pause
