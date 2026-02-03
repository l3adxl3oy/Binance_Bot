"""
⚙️ ไฟล์ Config สำหรับ Daily Scalping Bot
🔐 ใช้ .env file สำหรับเก็บ API Keys และข้อมูลสำคัญ
"""

from decouple import config, Csv
from typing import List


class Config:
    """
    การตั้งค่าบอท - อ่านค่าจาก .env file
    
    🔧 วิธีใช้งาน:
    1. คัดลอก .env.example เป็น .env
    2. แก้ไขค่าต่างๆ ใน .env ตามต้องการ
    3. ห้าม commit .env เข้า git (มี .gitignore ป้องกันแล้ว)
    """
    
    # ==================== BINANCE API ====================
    # 🔑 วิธีสร้าง API Key:
    # 1. Testnet (ฝึกใช้ฟรี): https://testnet.binance.vision/
    # 2. Mainnet (เงินจริง): https://www.binance.com/en/my/settings/api-management
    
    API_KEY: str = config("BINANCE_API_KEY", default="YOUR_BINANCE_API_KEY")
    API_SECRET: str = config("BINANCE_API_SECRET", default="YOUR_BINANCE_API_SECRET")
    BASE_URL: str = config("BINANCE_BASE_URL", default="https://testnet.binance.vision")
    
    # ==================== TELEGRAM (Optional) ====================
    TELEGRAM_ENABLED: bool = config("TELEGRAM_ENABLED", default=False, cast=bool)
    TELEGRAM_BOT_TOKEN: str = config("TELEGRAM_BOT_TOKEN", default="")
    TELEGRAM_CHAT_ID: str = config("TELEGRAM_CHAT_ID", default="")
    
    # ==================== เงินทุนและความเสี่ยง ====================
    DEMO_MODE: bool = config("DEMO_MODE", default=True, cast=bool)
    STARTING_BALANCE: float = config("STARTING_BALANCE", default=100.0, cast=float)
    
    MAX_LOSS_PER_TRADE: float = config("MAX_LOSS_PER_TRADE", default=0.25, cast=float)  # ลดจาก 0.6 → 0.25%
    DAILY_LOSS_LIMIT: float = config("DAILY_LOSS_LIMIT", default=2.5, cast=float)  # หยุดเทรดที่ -2.5%
    DAILY_PROFIT_TARGET: float = config("DAILY_PROFIT_TARGET", default=2.0, cast=float)  # เป้ากำไร 2%/วัน (realistic)
    DAILY_MAX_TARGET: float = config("DAILY_MAX_TARGET", default=5.0, cast=float)  # หยุดเทรดที่ +5% (lock profits)
    
    # ==================== การจัดการ Position ====================
    MAX_TOTAL_POSITIONS: int = config("MAX_TOTAL_POSITIONS", default=4, cast=int)  # ปรับตาม symbols ที่ผ่าน backtest
    MAX_ACTIVE_SYMBOLS: int = config("MAX_ACTIVE_SYMBOLS", default=4, cast=int)  # ใช้เฉพาะเหรียญที่ผ่าน backtest
    
    # คู่เงินที่จะเทรด (✅ Backtest Verified Only - Top 4 Performers)
    SYMBOL_POOL: List[str] = [
        "BTCUSDT",   # ✅ Best performer: 68.75% WR, avg +$0.30
        "BNBUSDT",   # ✅ Explosive: +$10.25 total
        "ADAUSDT",   # ✅ Stable: 68.42% WR
        "SOLUSDT",   # ✅ Good: 63.16% WR
        # เหรียญอื่นๆ รอผล backtest ก่อนเปิดใช้
        # "ETHUSDT",  # ❌ REMOVED: -$18.65 total (destroying performance)
        # "XRPUSDT", "DOGEUSDT", "TRXUSDT", "DOTUSDT", "AVAXUSDT",
        # "LINKUSDT", "ATOMUSDT", "LTCUSDT", "ETCUSDT", "XLMUSDT",
        # "FILUSDT", "ICPUSDT", "APTUSDT"
    ]
    
    # ==================== Take Profit / Stop Loss ====================
    TAKE_PROFIT_3_SIGNALS: float = config("TAKE_PROFIT_3_SIGNALS", default=0.85, cast=float)
    TAKE_PROFIT_4_SIGNALS: float = config("TAKE_PROFIT_4_SIGNALS", default=1.15, cast=float)
    STOP_LOSS_PERCENT: float = config("STOP_LOSS_PERCENT", default=0.35, cast=float)
    
    # ==================== INTELLIGENT FEATURES ====================
    # Event Management
    ENABLE_EVENT_MANAGER: bool = config("ENABLE_EVENT_MANAGER", default=True, cast=bool)
    ENABLE_SENTIMENT_TRACKING: bool = config("ENABLE_SENTIMENT_TRACKING", default=True, cast=bool)
    ENABLE_CASCADE_DETECTION: bool = config("ENABLE_CASCADE_DETECTION", default=True, cast=bool)
    
    # Risk Management
    ENABLE_ADVANCED_RISK: bool = config("ENABLE_ADVANCED_RISK", default=True, cast=bool)
    ENABLE_CORRELATION_FILTER: bool = config("ENABLE_CORRELATION_FILTER", default=True, cast=bool)
    ENABLE_KELLY_SIZING: bool = config("ENABLE_KELLY_SIZING", default=True, cast=bool)
    MAX_CORRELATION_ALLOWED: float = config("MAX_CORRELATION_ALLOWED", default=0.5, cast=float)  # ลดจาก 0.65 → 0.5 (เข้มงวดขึ้น)
    
    # Adaptive Strategy
    ENABLE_ADAPTIVE_STRATEGY: bool = config("ENABLE_ADAPTIVE_STRATEGY", default=True, cast=bool)
    ENABLE_REGIME_DETECTION: bool = config("ENABLE_REGIME_DETECTION", default=True, cast=bool)
    ENABLE_PARAMETER_LEARNING: bool = config("ENABLE_PARAMETER_LEARNING", default=True, cast=bool)
    
    # Enhanced Alerts
    ENABLE_ENHANCED_ALERTS: bool = config("ENABLE_ENHANCED_ALERTS", default=True, cast=bool)
    ALERT_HOURLY_STATUS: bool = config("ALERT_HOURLY_STATUS", default=False, cast=bool)
    ALERT_DAILY_SUMMARY: bool = config("ALERT_DAILY_SUMMARY", default=True, cast=bool)
    
    # Trailing Stop
    TRAILING_STOP_ENABLED: bool = config("TRAILING_STOP_ENABLED", default=True, cast=bool)
    TRAILING_STOP_PERCENT: float = config("TRAILING_STOP_PERCENT", default=0.2, cast=float)
    TRAILING_ACTIVATION_PROFIT: float = config("TRAILING_ACTIVATION_PROFIT", default=0.5, cast=float)
    
    # ==================== AUTO-UPDATE ====================
    # Auto-update configuration
    AUTO_UPDATE_CHECK_ENABLED: bool = config("AUTO_UPDATE_CHECK_ENABLED", default=True, cast=bool)
    AUTO_UPDATE_ON_STARTUP: bool = config("AUTO_UPDATE_ON_STARTUP", default=False, cast=bool)  # Manual approval by default
    AUTO_UPDATE_CHECK_FREQUENCY: int = config("AUTO_UPDATE_CHECK_FREQUENCY", default=86400, cast=int)  # Check once per day (seconds)
    AUTO_UPDATE_BACKUP_RETENTION: int = config("AUTO_UPDATE_BACKUP_RETENTION", default=5, cast=int)  # Keep last 5 backups
    
    # ==================== ระบบ ====================
    CHECK_INTERVAL: int = config("CHECK_INTERVAL", default=30, cast=int)
    TIMEFRAME: str = config("TIMEFRAME", default="1m")
    
    # ==================== AGGRESSIVE BOT SETTINGS ====================
    # TP/SL Levels
    AGGRESSIVE_QUICK_TP: float = config("AGGRESSIVE_QUICK_TP", default=1.2, cast=float)
    AGGRESSIVE_MEDIUM_TP: float = config("AGGRESSIVE_MEDIUM_TP", default=1.8, cast=float)
    AGGRESSIVE_STRONG_TP: float = config("AGGRESSIVE_STRONG_TP", default=2.5, cast=float)
    AGGRESSIVE_TIGHT_SL: float = config("AGGRESSIVE_TIGHT_SL", default=0.6, cast=float)
    AGGRESSIVE_MEDIUM_SL: float = config("AGGRESSIVE_MEDIUM_SL", default=0.8, cast=float)
    AGGRESSIVE_WIDE_SL: float = config("AGGRESSIVE_WIDE_SL", default=1.0, cast=float)
    
    # Recovery System
    AGGRESSIVE_MARTINGALE_MULTIPLIER: float = config("AGGRESSIVE_MARTINGALE_MULTIPLIER", default=1.3, cast=float)
    AGGRESSIVE_MAX_MARTINGALE_LEVEL: int = config("AGGRESSIVE_MAX_MARTINGALE_LEVEL", default=2, cast=int)
    AGGRESSIVE_ENABLE_AVERAGING: bool = config("AGGRESSIVE_ENABLE_AVERAGING", default=False, cast=bool)
    AGGRESSIVE_AVERAGING_DISTANCE: float = config("AGGRESSIVE_AVERAGING_DISTANCE", default=0.3, cast=float)
    AGGRESSIVE_MAX_AVERAGING_TIMES: int = config("AGGRESSIVE_MAX_AVERAGING_TIMES", default=0, cast=int)
    
    # Signal Quality
    AGGRESSIVE_MIN_SIGNAL_STRENGTH: float = config("AGGRESSIVE_MIN_SIGNAL_STRENGTH", default=4.0, cast=float)
    AGGRESSIVE_MIN_CONFLUENCE_SIGNALS: int = config("AGGRESSIVE_MIN_CONFLUENCE_SIGNALS", default=4, cast=int)
    
    # Targets & Limits
    AGGRESSIVE_DAILY_TARGET: float = config("AGGRESSIVE_DAILY_TARGET", default=5.0, cast=float)
    AGGRESSIVE_DAILY_MAX: float = config("AGGRESSIVE_DAILY_MAX", default=5.0, cast=float)
    AGGRESSIVE_MAX_DAILY_LOSS: float = config("AGGRESSIVE_MAX_DAILY_LOSS", default=-5.0, cast=float)
    AGGRESSIVE_MAX_INTRADAY_DRAWDOWN: float = config("AGGRESSIVE_MAX_INTRADAY_DRAWDOWN", default=-15.0, cast=float)
    AGGRESSIVE_QUICK_PROFIT_LOCK: float = config("AGGRESSIVE_QUICK_PROFIT_LOCK", default=3.0, cast=float)
    
    # Timing
    AGGRESSIVE_TIME_STOP_FAST: int = config("AGGRESSIVE_TIME_STOP_FAST", default=600, cast=int)
    AGGRESSIVE_TIME_STOP_RECOVERY: int = config("AGGRESSIVE_TIME_STOP_RECOVERY", default=900, cast=int)
    AGGRESSIVE_WIN_STREAK_BONUS: float = config("AGGRESSIVE_WIN_STREAK_BONUS", default=1.3, cast=float)
    AGGRESSIVE_LOSS_REDUCTION: float = config("AGGRESSIVE_LOSS_REDUCTION", default=0.7, cast=float)
    
    # ==================== DAILY SCALPING BOT SETTINGS ====================
    # 📊 ตัวชี้วัดทางเทคนิค (Technical Indicators)
    RSI_PERIOD: int = config("RSI_PERIOD", default=14, cast=int)  # ช่วงเวลาคำนวณ RSI
    RSI_OVERSOLD: int = config("RSI_OVERSOLD", default=30, cast=int)  # ขาย Oversold (ถูกเกินไป)
    RSI_OVERBOUGHT: int = config("RSI_OVERBOUGHT", default=70, cast=int)  # ขอบ Overbought (แพงเกินไป)
    BB_PERIOD: int = config("BB_PERIOD", default=20, cast=int)  # ช่วง Bollinger Bands
    BB_STD_DEV: int = config("BB_STD_DEV", default=2, cast=int)  # ค่าเบี่ยงเบนมาตรฐาน BB
    MACD_FAST: int = config("MACD_FAST", default=12, cast=int)  # MACD เส้นเร็ว
    MACD_SLOW: int = config("MACD_SLOW", default=26, cast=int)  # MACD เส้นช้า
    MACD_SIGNAL: int = config("MACD_SIGNAL", default=9, cast=int)  # MACD Signal
    EMA_FAST: int = config("EMA_FAST", default=20, cast=int)  # EMA เร็ว (เทรนด์สั้น)
    EMA_SLOW: int = config("EMA_SLOW", default=50, cast=int)  # EMA ช้า (เทรนด์ยาว)
    ATR_PERIOD: int = config("ATR_PERIOD", default=14, cast=int)  # ช่วงคำนวณ ATR
    
    # 🎯 กฎการเข้า-ออกออเดอร์ (Entry/Exit Rules)
    MIN_CONFLUENCE_SIGNALS: int = config("MIN_CONFLUENCE_SIGNALS", default=3, cast=int)  # จำนวนสัญญาณขั้นต่ำ
    MIN_SIGNAL_STRENGTH: float = config("MIN_SIGNAL_STRENGTH", default=4.5, cast=float)  # ความแข็งแรงสัญญาณขั้นต่ำ
    ATR_SL_MULTIPLIER: float = config("ATR_SL_MULTIPLIER", default=1.2, cast=float)  # ตัวคูณ ATR สำหรับ Stop Loss
    ATR_TP_MULTIPLIER: float = config("ATR_TP_MULTIPLIER", default=4.5, cast=float)  # ตัวคูณ ATR สำหรับ Take Profit
    
    # 💰 ปิดกำไรทีละส่วน (Partial Take Profit)
    PARTIAL_TP_ENABLED: bool = config("PARTIAL_TP_ENABLED", default=True, cast=bool)  # เปิด/ปิด Partial TP
    PARTIAL_TP_1_PERCENT: float = config("PARTIAL_TP_1_PERCENT", default=0.35, cast=float)  # TP ครั้งที่ 1 (0.35%)
    PARTIAL_TP_1_SIZE: float = config("PARTIAL_TP_1_SIZE", default=0.40, cast=float)  # ปิด 40% ของ position
    PARTIAL_TP_2_PERCENT: float = config("PARTIAL_TP_2_PERCENT", default=0.75, cast=float)  # TP ครั้งที่ 2 (0.75%)
    PARTIAL_TP_2_SIZE: float = config("PARTIAL_TP_2_SIZE", default=0.30, cast=float)  # ปิด 30% ของ position
    PARTIAL_TP_3_PERCENT: float = config("PARTIAL_TP_3_PERCENT", default=2.0, cast=float)  # TP ครั้งที่ 3 (2.0%)
    MOVE_SL_TO_BREAKEVEN_AFTER_PARTIAL: bool = config("MOVE_SL_TO_BREAKEVEN_AFTER_PARTIAL", default=True, cast=bool)  # ขยับ SL เป็น BE หลัง Partial TP
    
    # 📍 จัดการออเดอร์ (Position Management)
    MAX_POSITIONS_PER_SYMBOL: int = config("MAX_POSITIONS_PER_SYMBOL", default=2, cast=int)  # ออเดอร์สูงสุดต่อเหรียญ
    TIME_STOP_BASE: int = config("TIME_STOP_BASE", default=150, cast=int)  # เวลาปิดพื้นฐาน (วินาที)
    TIME_STOP_STRONG_SIGNAL: int = config("TIME_STOP_STRONG_SIGNAL", default=240, cast=int)  # เวลาปิดสัญญาณแรง (วินาที)
    TIME_STOP_SECONDS: int = config("TIME_STOP_SECONDS", default=240, cast=int)  # เวลา Time Stop (วินาที)
    
    # 📊 กรองตลาดและปริมาณ (Volume & Market Filter)
    MIN_VOLUME_RATIO: float = config("MIN_VOLUME_RATIO", default=0.8, cast=float)  # อัตราปริมาณขั้นต่ำ
    SIDEWAYS_THRESHOLD: float = config("SIDEWAYS_THRESHOLD", default=0.4, cast=float)  # เกณฑ์ตลาดนิ่ง
    USE_VOLUME_QUALITY_FILTER: bool = config("USE_VOLUME_QUALITY_FILTER", default=True, cast=bool)  # กรองคุณภาพปริมาณ
