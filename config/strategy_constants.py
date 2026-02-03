"""
📊 Strategy Constants - Advanced Settings
❌ ค่าเหล่านี้เป็น logic/สูตร ไม่ควรให้ลูกค้าแก้
"""


class StrategyConstants:
    """
    Strategy Parameters - Internal Configuration
    
    ⚠️ WARNING: อย่าแก้ไขค่าเหล่านี้ถ้าไม่เข้าใจกลยุทธ์
    การแก้ไขอาจทำให้บอททำงานผิดพลาด
    """
    
    # ==================== SYMBOL ROTATION ====================
    SYMBOL_ROTATION_INTERVAL: int = 900  # Rotate every 15 minutes
    
    # ==================== INDICATOR SETTINGS ====================
    # RSI Settings
    RSI_PERIOD: int = 14
    RSI_OVERSOLD: int = 30
    RSI_OVERBOUGHT: int = 70
    RSI_EXTREME_THRESHOLD: int = 25
    
    # Bollinger Bands
    BB_PERIOD: int = 20
    BB_STD_DEV: int = 2
    
    # MACD
    MACD_FAST: int = 12
    MACD_SLOW: int = 26
    MACD_SIGNAL: int = 9
    
    # Volume
    VOLUME_PERIOD: int = 20
    VOLUME_MULTIPLIER: float = 1.5  # ลดจาก 2.0 → 1.5 (รับสัญญาณได้บ่อยขึ้น)
    
    # ATR
    ATR_PERIOD: int = 14
    
    # Trend Filter
    EMA_FAST: int = 20
    EMA_SLOW: int = 50
    TRADE_WITH_TREND_ONLY: bool = True
    
    # Signal Weighting
    USE_WEIGHTED_SIGNALS: bool = True
    USE_TREND_WEIGHTING: bool = True
    
    # ==================== MULTI-TIMEFRAME ====================
    PRIMARY_TIMEFRAME: str = "1m"
    CONFIRM_TIMEFRAME: str = "3m"
    USE_HIGHER_TF_CONFIRM: bool = True
    MIN_TF_ALIGNMENT_SCORE: int = 2
    
    # ==================== ENTRY/EXIT RULES ====================
    MIN_CONFLUENCE_SIGNALS: int = 3
    MIN_SIGNAL_STRENGTH: float = 3.5  # ลดจาก 4.5 → 3.5 (เพิ่มความถี่ออเดอร์)
    USE_DYNAMIC_RR: bool = True
    USE_ATR_BASED_STOPS: bool = True  # เปิดใช้ ATR-based SL/TP
    ATR_SL_MULTIPLIER: float = 1.2    # ลดจาก 1.5 → 1.2 (SL แคบลง 20% = ลด noise)
    ATR_TP_MULTIPLIER: float = 4.5    # เพิ่มจาก 3.5 → 4.5 (TP กว้างขึ้น 29%, RR = 1:3.75)
    
    # Partial Take Profit (3-tier system - OPTIMIZED)
    PARTIAL_TP_ENABLED: bool = True
    PARTIAL_TP_1_PERCENT: float = 0.35  # เพิ่มจาก 0.25% → 0.35% (ล็อคเร็วขึ้น)
    PARTIAL_TP_1_SIZE: float = 0.40     # เพิ่มจาก 0.25 → 0.40 (ล็อค 40% แทน 25%)
    PARTIAL_TP_2_PERCENT: float = 0.75  # เพิ่มจาก 0.5% → 0.75% (ล็อคกำไรดีๆ)
    PARTIAL_TP_2_SIZE: float = 0.30     # เพิ่มจาก 0.25 → 0.30 (ล็อคอีก 30%)
    PARTIAL_TP_3_PERCENT: float = 2.0   # เพิ่มจาก 1.0% → 2.0% (ปล่อย runner 30% ไปไกล)
    # เมื่อ hit partial TP แรก → ขยับ SL เป็น breakeven
    MOVE_SL_TO_BREAKEVEN_AFTER_PARTIAL: bool = True
    
    # Time Stop
    TIME_STOP_BASE: int = 150  # ลดจาก 180 → หมุนเวียนเร็วขึ้น
    TIME_STOP_STRONG_SIGNAL: int = 240  # ลดจาก 300 → เร็วขึ้น
    TIME_STOP_HIGH_VOL_MULT: float = 1.3
    TIME_STOP_SECONDS: int = 240  # ลดจาก 300 → หมุนเวียนเร็วขึ้น
    
    # ==================== POSITION MANAGEMENT ====================
    MAX_POSITIONS_PER_SYMBOL: int = 2
    
    # ==================== ADAPTIVE FREQUENCY CONTROL ====================
    USE_ADAPTIVE_FREQUENCY: bool = True
    ADAPTIVE_GOOD_PERFORMANCE_WR: float = 58  # ปรับเป็น 58% (realistic)
    ADAPTIVE_GOOD_PERFORMANCE_PNL: float = 1.0  # ต้องมีกำไร +1%
    ADAPTIVE_BAD_PERFORMANCE_WR: float = 50  # ต่ำกว่า 50% = defensive
    ADAPTIVE_BAD_PERFORMANCE_PNL: float = -1.0  # หรือขาดทุนเกิน -1%
    ADAPTIVE_MAX_POSITIONS_GOOD: int = 6  # ลดจาก 12 → 6 (รักษา risk)
    ADAPTIVE_MAX_POSITIONS_BAD: int = 3  # ลดจาก 6 → 3 (ระมัดระวังมากขึ้น)
    ADAPTIVE_MIN_STRENGTH_GOOD: float = 3.8  # ผ่อนปรนเล็กน้อยเมื่อดี
    ADAPTIVE_MIN_STRENGTH_BAD: float = 4.5  # เข้มงวดเมื่อแย่
    
    # ==================== PROFIT LOCKING ====================
    PROFIT_LOCK_ENABLED: bool = False
    PROFIT_LOCK_THRESHOLD: float = 7.0
    PROFIT_LOCK_MODE: str = "normal"
    
    # ==================== PROGRESSIVE RECOVERY ====================
    USE_PROGRESSIVE_RECOVERY: bool = False  # ปิดเพื่อหลีกเลี่ยง martingale effect
    RECOVERY_MODE_TRIGGER: float = -2.5  # เข้มงวดขึ้น: trigger ที่ -2.5% แทน -1.2%
    RECOVERY_CONFLUENCE_REQUIRED: int = 4  # ต้องการ signal ที่แข็งแกร่งกว่า
    RECOVERY_SIZE_LOSS_1: float = 0.8  # ลดขนาดแทนที่จะเพิ่ม (anti-martingale)
    RECOVERY_SIZE_LOSS_2: float = 0.7  # ลดต่อเนื่อง
    RECOVERY_SIZE_LOSS_3: float = 0.6  # ลดอีก
    RECOVERY_TP_MULTIPLIER: float = 1.0  # ไม่เพิ่ม TP ในโหมด recovery
    MAX_RECOVERY_TRADES: int = 2  # ลดจาก 3 → 2
    
    # ==================== HARD STOP RISK MANAGEMENT (CRITICAL!) ====================
    # 🛡️ Protection against catastrophic losses
    ENABLE_HARD_STOPS: bool = True
    MAX_DAILY_LOSS: float = -2.5           # หยุดเทรดถ้าขาดทุน -2.5% ในวันเดียว
    MAX_WEEKLY_LOSS: float = -10.0         # หยุด 1 สัปดาห์ถ้าขาดทุน -10%
    MAX_MONTHLY_LOSS: float = -25.0        # Review strategy ถ้าขาดทุน -25%/เดือน
    MAX_LOSS_PER_POSITION: float = 5.0     # ตัดขาดทุนบังคับถ้า position เดียวเกิน -5%
    MAX_CONSECUTIVE_LOSSES: int = 5        # หยุดเทรดวันนั้นหลังขาดทุนติด 5 ครั้ง
    PAUSE_AFTER_DAILY_LIMIT: bool = True   # หยุดเทรดอัตโนมัติเมื่อถึง daily limit
    
    # ==================== COST SIMULATION ====================
    SIMULATE_REAL_COSTS: bool = True
    MAKER_FEE: float = 0.001  # 0.1%
    TAKER_FEE: float = 0.001  # 0.1%
    EXPECTED_SLIPPAGE: float = 0.03  # 0.03%
    MIN_NET_PROFIT_REQUIRED: float = 0.4  # 0.4%
    
    # ==================== TIME FILTER ====================
    TRADING_START_HOUR: int = 8   # UTC 08:00 (Asian market open)
    TRADING_END_HOUR: int = 15    # UTC 15:00 (London mid-session)
    # เทรดเฉพาะช่วง high volume: Asian + London overlap
    
    # ==================== MARKET FILTER ====================
    SIDEWAYS_THRESHOLD: float = 0.4
    USE_VOLUME_QUALITY_FILTER: bool = True
    MIN_VOLUME_RATIO: float = 0.8
    
    # ==================== SYSTEM ====================
    CANDLES_LIMIT: int = 100
    API_REQUEST_DELAY: float = 0.1
    
    # API Resilience
    API_RETRY_ATTEMPTS: int = 3
    API_RETRY_DELAY: int = 5
    API_TIMEOUT: int = 10
    USE_CACHED_DATA_ON_FAILURE: bool = True
    
    # ==================== STATE PERSISTENCE ====================
    STATE_FILE: str = "bot_state.json"
