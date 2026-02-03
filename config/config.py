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
