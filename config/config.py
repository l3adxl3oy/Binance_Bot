"""
⚙️ ไฟล์ Config สำหรับ Binance Trading Bots
📌 Bot Configuration จัดการที่นี่ทั้งหมด
🔐 API Credentials เก็บใน .env file
"""

from decouple import config, Csv
from typing import List


class Config:
    """
    การตั้งค่าบอททั้งหมด
    
    🔧 วิธีใช้งาน:
    1. แก้ไข config.py สำหรับการตั้งค่ากลยุทธ์
    2. แก้ไข .env เฉพาะ API Keys และ Telegram
    3. ห้าม commit .env เข้า git (มี .gitignore ป้องกันแล้ว)
    """
    
    # ==================== BINANCE API (จาก .env) ====================
    API_KEY: str = config("BINANCE_API_KEY", default="YOUR_BINANCE_API_KEY")
    API_SECRET: str = config("BINANCE_API_SECRET", default="YOUR_BINANCE_API_SECRET")
    BASE_URL: str = config("BINANCE_BASE_URL", default="https://testnet.binance.vision")
    
    # ==================== TELEGRAM (จาก .env) ====================
    TELEGRAM_ENABLED: bool = config("TELEGRAM_ENABLED", default=False, cast=bool)
    TELEGRAM_BOT_TOKEN: str = config("TELEGRAM_BOT_TOKEN", default="")
    TELEGRAM_CHAT_ID: str = config("TELEGRAM_CHAT_ID", default="")
    
    # ==================== GENERAL TRADING SETTINGS ====================
    # 💼 โหมดการเทรด
    DEMO_MODE: bool = False  # เปลี่ยนเป็น True เพื่อใช้โหมดทดสอบ (ไม่เชื่อม Binance)
    
    # 📊 ระบบและเวลา
    CHECK_INTERVAL: int = 30  # ตรวจสอบทุก 30 วินาที
    TIMEFRAME: str = "1m"  # ใช้กราฟ 1 นาที
    
    # 📈 คู่เงินที่เทรด (Verified from Backtest)
    SYMBOL_POOL: List[str] = [
        "BTCUSDT",   # ✅ Best: 68.75% WR
        "BNBUSDT",   # ✅ Explosive: +$10.25
        "ADAUSDT",   # ✅ Stable: 68.42% WR
        "SOLUSDT",   # ✅ Good: 63.16% WR
    ]
    
    # 🎯 การจัดการ Position
    MAX_TOTAL_POSITIONS: int = 4  # ออเดอร์สูงสุดพร้อมกัน
    MAX_ACTIVE_SYMBOLS: int = 4  # เหรียญสูงสุดพร้อมกัน
    
    # ==================== INTELLIGENT SYSTEMS (เปิด/ปิดระบบอัจฉริยะ) ====================
    ENABLE_EVENT_MANAGER: bool = True  # ระบบติดตามข่าวและเหตุการณ์
    ENABLE_SENTIMENT_TRACKING: bool = True  # ติดตามความเชื่อมั่นตลาด
    ENABLE_CASCADE_DETECTION: bool = True  # ตรวจจับการลดราคาพร้อมกัน
    
    ENABLE_ADVANCED_RISK: bool = True  # ระบบบริหารความเสี่ยงขั้นสูง
    ENABLE_CORRELATION_FILTER: bool = True  # กรองคู่เงินที่มี correlation สูง
    ENABLE_KELLY_SIZING: bool = True  # คำนวณขนาด position ด้วย Kelly Criterion
    MAX_CORRELATION_ALLOWED: float = 0.5  # ห้ามเทรดคู่เงินที่ correlation > 0.5
    
    ENABLE_ADAPTIVE_STRATEGY: bool = True  # ปรับกลยุทธ์ตามสภาพตลาด
    ENABLE_REGIME_DETECTION: bool = True  # ตรวจจับแนวโน้มตลาด
    ENABLE_PARAMETER_LEARNING: bool = True  # เรียนรู้ parameter ที่เหมาะสม
    
    ENABLE_ENHANCED_ALERTS: bool = True  # การแจ้งเตือนขั้นสูง
    ALERT_HOURLY_STATUS: bool = False  # แจ้งเตือนทุกชั่วโมง
    ALERT_DAILY_SUMMARY: bool = True  # สรุปผลรายวัน
    
    # ==================== AUTO-UPDATE ====================
    AUTO_UPDATE_CHECK_ENABLED: bool = True  # เช็คอัพเดทอัตโนมัติ
    AUTO_UPDATE_ON_STARTUP: bool = False  # อัพเดทอัตโนมัติเมื่อเปิดบอท
    AUTO_UPDATE_CHECK_FREQUENCY: int = 86400  # เช็คทุก 24 ชม (วินาที)
    AUTO_UPDATE_BACKUP_RETENTION: int = 5  # เก็บ backup ล่าสุด 5 ไฟล์
    
    # ==================== 🔥 AGGRESSIVE RECOVERY BOT SETTINGS ====================
    # กลยุทธ์: เทรดรวดเร็ว + กู้คืนขาดทุนอัจฉริยะ (v2.2 Original - Verified +13.19%)
    
    # 💰 TP/SL Levels (Proven Profitable)
    AGGRESSIVE_QUICK_TP: float = 1.2  # TP เร็ว 1.2%
    AGGRESSIVE_MEDIUM_TP: float = 1.8  # TP กลาง 1.8%
    AGGRESSIVE_STRONG_TP: float = 2.5  # TP แรง 2.5%
    AGGRESSIVE_TIGHT_SL: float = 0.6  # SL แคบ 0.6%
    AGGRESSIVE_MEDIUM_SL: float = 0.8  # SL กลาง 0.8%
    AGGRESSIVE_WIDE_SL: float = 1.0  # SL กว้าง 1.0%
    
    # � Risk Management
    MAX_LOSS_PER_TRADE: float = 0.15  # เสี่ยงสูงสุด 0.15% ต่อเทรด
    
    # 🔄 Recovery System (Martingale)
    AGGRESSIVE_ENABLE_SMART_MARTINGALE: bool = True  # เปิด Martingale
    AGGRESSIVE_MARTINGALE_MULTIPLIER: float = 1.3  # คูณขนาด position 1.3x
    AGGRESSIVE_MAX_MARTINGALE_LEVEL: int = 2  # สูงสุด 2 level
    AGGRESSIVE_ENABLE_AVERAGING: bool = False  # ปิด Averaging (ป้องกันการทบทุน)
    AGGRESSIVE_AVERAGING_DISTANCE: float = 0.3  # ระยะห่างเฉลี่ย 0.3%
    AGGRESSIVE_MAX_AVERAGING_TIMES: int = 0  # ไม่ทำ Averaging
    
    # 🎯 Signal Quality (v2.2 Original - Very Selective)
    AGGRESSIVE_MIN_SIGNAL_STRENGTH: float = 4.0  # คะแนนขั้นต่ำ 4.0/5.0
    AGGRESSIVE_MIN_CONFLUENCE_SIGNALS: int = 4  # สัญญาณขั้นต่ำ 4 อัน
    
    # 💎 Targets & Limits
    AGGRESSIVE_DAILY_TARGET: float = 5.0  # เป้ากำไร 5%/วัน
    AGGRESSIVE_DAILY_MAX: float = 5.0  # หยุดที่ 5% (Lock Profit)
    AGGRESSIVE_MAX_DAILY_LOSS: float = -5.0  # หยุดขาดทุน -5%
    AGGRESSIVE_MAX_INTRADAY_DRAWDOWN: float = -15.0  # Drawdown สูงสุด -15%
    AGGRESSIVE_QUICK_PROFIT_LOCK: float = 3.0  # ล็อคกำไรที่ 3%
    
    # ⏰ Timing (v2.2 Original)
    AGGRESSIVE_TIME_STOP_FAST: int = 600  # หมดเวลา 10 นาที (600 วินาที)
    AGGRESSIVE_TIME_STOP_RECOVERY: int = 900  # หมดเวลา Recovery 15 นาที
    AGGRESSIVE_WIN_STREAK_BONUS: float = 1.3  # โบนัสชนะติด 1.3x
    AGGRESSIVE_LOSS_REDUCTION: float = 0.7  # ลดขนาดหลังแพ้ 0.7x
    
    # 🛡️ Trailing Stop (Aggressive Mode)
    AGGRESSIVE_TRAILING_ENABLED: bool = True  # เปิด Trailing Stop
    AGGRESSIVE_TRAILING_PERCENT: float = 0.3  # ห่าง 0.3%
    AGGRESSIVE_TRAILING_ACTIVATION: float = 0.5  # เริ่มที่กำไร 0.5%
    
    # ==================== 📊 DAILY SCALPING BOT SETTINGS ====================
    # กลยุทธ์: Confluence Scalping บนกราฟ 1 นาที
    
    # 🎯 Daily Targets
    DAILY_PROFIT_TARGET: float = 2.0  # เป้ากำไร 2%/วัน
    DAILY_MAX_TARGET: float = 5.0  # หยุดเทรดที่ 5%
    DAILY_LOSS_LIMIT: float = -2.5  # หยุดขาดทุน -2.5%
    
    # 📈 Technical Indicators (ตัวชี้วัดทางเทคนิค)
    RSI_PERIOD: int = 14  # ช่วง RSI
    RSI_OVERSOLD: int = 30  # RSI Oversold
    RSI_OVERBOUGHT: int = 70  # RSI Overbought
    BB_PERIOD: int = 20  # ช่วง Bollinger Bands
    BB_STD_DEV: int = 2  # ค่าเบี่ยงเบนมาตรฐาน
    MACD_FAST: int = 12  # MACD Fast
    MACD_SLOW: int = 26  # MACD Slow
    MACD_SIGNAL: int = 9  # MACD Signal
    EMA_FAST: int = 20  # EMA เร็ว
    EMA_SLOW: int = 50  # EMA ช้า
    ATR_PERIOD: int = 14  # ช่วง ATR
    
    # 🎯 Entry/Exit Rules
    MIN_CONFLUENCE_SIGNALS: int = 3  # สัญญาณขั้นต่ำ 3 อัน
    MIN_SIGNAL_STRENGTH: float = 4.5  # คะแนนขั้นต่ำ 4.5/5.0
    ATR_SL_MULTIPLIER: float = 1.2  # Stop Loss = ATR × 1.2
    ATR_TP_MULTIPLIER: float = 4.5  # Take Profit = ATR × 4.5
    
    # 💰 Partial Take Profit (ปิดกำไรทีละส่วน)
    PARTIAL_TP_ENABLED: bool = True  # เปิดใช้งาน Partial TP
    PARTIAL_TP_1_PERCENT: float = 0.35  # TP 1: 0.35%
    PARTIAL_TP_1_SIZE: float = 0.40  # ปิด 40% ของ position
    PARTIAL_TP_2_PERCENT: float = 0.75  # TP 2: 0.75%
    PARTIAL_TP_2_SIZE: float = 0.30  # ปิด 30% ของ position
    PARTIAL_TP_3_PERCENT: float = 2.0  # TP 3: 2.0%
    MOVE_SL_TO_BREAKEVEN_AFTER_PARTIAL: bool = True  # ขยับ SL → BE หลัง Partial
    
    # 📍 Position Management
    MAX_POSITIONS_PER_SYMBOL: int = 2  # ออเดอร์สูงสุดต่อเหรียญ
    TIME_STOP_SECONDS: int = 240  # หมดเวลา 4 นาที (240 วินาที)
    
    # 📊 Volume & Market Filter
    MIN_VOLUME_RATIO: float = 0.8  # Volume ขั้นต่ำ 80%
    SIDEWAYS_THRESHOLD: float = 0.4  # กรองตลาดนิ่ง
    USE_VOLUME_QUALITY_FILTER: bool = True  # เปิดกรอง Volume
    
    # 🛡️ Trailing Stop (Daily Scalping Mode)
    DAILY_TRAILING_ENABLED: bool = True  # เปิด Trailing Stop
    DAILY_TRAILING_PERCENT: float = 0.2  # ห่าง 0.2%
    DAILY_TRAILING_ACTIVATION: float = 0.5  # เริ่มที่กำไร 0.5%
