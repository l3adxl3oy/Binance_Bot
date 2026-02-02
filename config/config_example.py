# ========================================
# BINANCE BOT CONFIGURATION
# ========================================
# วิธีใช้: Copy ไฟล์นี้เป็น config.py แล้วแก้ไขค่าด้านล่าง

class Config:
    """การตั้งค่าสำหรับ Binance Daily Scalping Bot"""
    
    # ==================== BINANCE API ====================
    # 🔑 ใส่ API Key ของคุณที่นี่ (สำคัญมาก!)
    # Testnet (ทดสอบ): https://testnet.binance.vision/
    # Mainnet (จริง): https://www.binance.com/en/my/settings/api-management
    
    API_KEY = "YOUR_API_KEY_HERE"
    API_SECRET = "YOUR_API_SECRET_HERE"
    
    # 🌐 เลือก URL
    BASE_URL = "https://testnet.binance.vision"  # Testnet (ทดสอบ - แนะนำ)
    # BASE_URL = "https://api.binance.com"       # Mainnet (จริง - ระวัง!)
    
    # ==================== TRADING SETTINGS ====================
    SYMBOL = "BTCUSDT"           # คู่เทรด
    TIMEFRAME = "1m"             # เวลา (1m, 5m, 15m)
    DEMO_MODE = True             # True = ไม่ส่ง order จริง, False = ส่ง order จริง
    
    # ==================== RISK MANAGEMENT ====================
    MAX_LOSS_PER_TRADE = 0.6     # เสี่ยงสูงสุดต่อเทรด (%)
    MAX_CONCURRENT_POSITIONS = 3  # จำนวน position สูงสุด
    DAILY_LOSS_LIMIT = 2.5       # หยุดเทรดถ้าขาดทุนเกิน (%)
    
    # ==================== STRATEGY ====================
    RSI_PERIOD = 14
    RSI_OVERSOLD = 30
    RSI_OVERBOUGHT = 70
    
    # ==================== SYSTEM ====================
    CHECK_INTERVAL = 30          # เช็คทุกๆ N วินาที
    CANDLES_LIMIT = 100          # ดึงข้อมูล candle ย้อนหลัง
