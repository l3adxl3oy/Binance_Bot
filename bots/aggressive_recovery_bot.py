"""
Aggressive Recovery Bot - เน้นทำกำไรรวดเร็วและกู้คืนขาดทุนอัจฉริยะ
Target: 3-8% daily profit with smart loss recovery
Strategy: Fast scalping + Intelligent martingale recovery + Adaptive position sizing

กลยุทธ์พิเศษ:
- 🚀 เทรดรวดเร็ว: TP แคบ (0.8-1.5%) แต่บ่อยขึ้น
- 🎯 ทำกำไรเล็กๆ ซ้ำๆ: ออเดอร์บ่อย win rate สูง
- 🧠 กู้คืนฉลาด: ใช้ Smart Martingale + Averaging เมื่อขาดทุน
- ⚡ ตัดขาดทุนเร็ว: SL แคบ (0.5%) แต่เพิ่ม position ถัดไปเพื่อกู้คืน
- 📊 ปรับขนาดอัตโนมัติ: Position size เพิ่มตามความมั่นใจและผลงาน
"""

import time
import logging
from datetime import datetime, timedelta, UTC
from typing import Dict, List, Optional
from collections import deque
import json
import os

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pandas as pd
from binance.spot import Spot

# Import modular components
from core.indicators import Indicators
from core.models import Position, TradeHistory
from managers.symbol_manager import SymbolManager
from managers.position_manager import PositionManager
from modules.trailing_stop import TrailingStopManager

# Import intelligent systems
from core.event_manager import EventManager
from core.risk_manager import RiskManager
from core.alert_manager import AlertManager
from core.adaptive_strategy import AdaptiveStrategyEngine

# Import configuration
from config.config import Config
from config.strategy_constants import StrategyConstants

# Import version information
try:
    from version import __version__, BOT_NAME
except ImportError:
    __version__ = "3.0.1"
    BOT_NAME = "AGGRESSIVE RECOVERY BOT 🔥"


# ===================== LOGGING SETUP =====================
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


# ===================== MAIN BOT ====================
class AggressiveRecoveryBot:
    """Aggressive Recovery Bot - Fast Profit + Smart Loss Recovery"""
    
    def __init__(self):
        logger.info("="*80)
        logger.info(f"🔥 {BOT_NAME} v{__version__} - OPTIMIZED v2.1".center(80))
        logger.info("="*80)
        logger.info("🎯 กลยุทธ์: เลือกเฉพาะสัญญาณดีที่สุด → ทำกำไร 5% → หยุดทันที".center(80))
        logger.info("="*80)
        
        # Track bot runtime
        self.start_time = datetime.now()
        
        # Binance client
        self.client = Spot(
            api_key=Config.API_KEY,
            api_secret=Config.API_SECRET,
            base_url=Config.BASE_URL
        )
        
        # 💰 ดึงยอดเงินจาก Binance (ไม่ใช้ .env อีกต่อไป)
        actual_balance = 0.0
        if Config.DEMO_MODE:
            # DEMO MODE: ใช้ยอดจำลอง
            actual_balance = 100.0
            logger.info(f"💼 DEMO MODE: ใช้ยอดเงินจำลอง ${actual_balance:.2f}")
        else:
            # LIVE MODE: ดึงจาก Binance
            try:
                account = self.client.account()
                for asset in account['balances']:
                    if asset['asset'] == 'USDT':
                        actual_balance = float(asset['free'])
                        logger.info(f"💰 ดึงยอดเงินจาก Binance: ${actual_balance:,.2f} USDT")
                        break
                if actual_balance == 0:
                    logger.error("❌ ไม่พบยอด USDT ใน account!")
                    raise ValueError("No USDT balance found")
            except Exception as e:
                logger.error(f"❌ ไม่สามารถดึงยอดเงินจาก Binance: {e}")
                raise
        
        logger.info(f"💼 โหมด: {'DEMO (ทดสอบปลอดภัย)' if Config.DEMO_MODE else 'LIVE ⚠️ เงินจริง!'}")
        logger.info(f"💰 ทุนเริ่มต้น: ${actual_balance:,.2f}")
        logger.info(f"📊 Symbols: {len(Config.SYMBOL_POOL)} pool, {Config.MAX_ACTIVE_SYMBOLS} active")
        logger.info(f"⏱️  Timeframe: {Config.TIMEFRAME} (Fast Scalping)")
        logger.info(f"🎯 เป้าหมาย STRICT: +{Config.AGGRESSIVE_DAILY_TARGET}% แล้วหยุดทันที!")
        logger.info("-"*80)
        logger.info("⚡ กลยุทธ์ที่ปรับปรุง v2.1 (Ultra-Selective)".center(80))
        logger.info("-"*80)
        logger.info(f"  ✅ TP เพิ่มขึ้น: {Config.AGGRESSIVE_QUICK_TP}%-{Config.AGGRESSIVE_STRONG_TP}% (RR ดีขึ้น)")
        logger.info(f"  🛡️  SL ปลอดภัย: {Config.AGGRESSIVE_TIGHT_SL}%-{Config.AGGRESSIVE_WIDE_SL}% (ป้องกันดี)")
        logger.info(f"  🔄 Martingale ปลอดภัย: {Config.AGGRESSIVE_MARTINGALE_MULTIPLIER}x Max {Config.AGGRESSIVE_MAX_MARTINGALE_LEVEL} level")
        logger.info(f"  🚫 Averaging: {'Disabled' if not Config.AGGRESSIVE_ENABLE_AVERAGING else 'Enabled'} (ป้องกันการทบทุน)")
        logger.info(f"  📊 Signal Quality: {Config.AGGRESSIVE_MIN_SIGNAL_STRENGTH}/5, {Config.AGGRESSIVE_MIN_CONFLUENCE_SIGNALS}/4 (เข้มงวดสูงสุด!)")
        logger.info(f"  ⏰ Check: {Config.CHECK_INTERVAL}s (ลดสัญญาณรบกวน)")
        logger.info(f"  🛡️  Drawdown Protection: {Config.AGGRESSIVE_MAX_INTRADAY_DRAWDOWN}% from peak")
        logger.info("="*80)
        
        # Show which intelligent features are enabled
        logger.info("🤖 ระบบอัจฉริยะที่เปิดใช้งาน".center(80))
        logger.info("-"*80)
        feature_status = []
        if Config.ENABLE_EVENT_MANAGER:
            feature_status.append("✅ Event Manager (ปฏิทินเศรษฐกิจ + ความเชื่อมั่น)")
        if Config.ENABLE_ADVANCED_RISK:
            feature_status.append("✅ Risk Manager (Kelly + Correlation + Drawdown)")
        if Config.ENABLE_ADAPTIVE_STRATEGY:
            feature_status.append("✅ Adaptive Strategy (ตรวจจับแนวโน้ม + เรียนรู้)")
        if Config.ENABLE_ENHANCED_ALERTS:
            feature_status.append("✅ Enhanced Alerts (การแจ้งเตือนอัจฉริยะ)")
        
        if feature_status:
            for status in feature_status:
                logger.info(f"  {status}")
        else:
            logger.info("  ⚠️  ไม่มีระบบอัจฉริยะเปิดใช้งาน (โหมดพื้นฐาน)")
        logger.info("="*80)
        
        # Core managers
        self.symbol_manager = SymbolManager(
            symbol_pool=Config.SYMBOL_POOL,
            max_active=Config.MAX_ACTIVE_SYMBOLS,
            rotation_interval=StrategyConstants.SYMBOL_ROTATION_INTERVAL
        )
        
        self.position_manager = PositionManager(
            max_total_positions=Config.MAX_TOTAL_POSITIONS + 5,  # เพิ่มพื้นที่สำหรับ recovery
            max_per_symbol=5  # อนุญาตหลาย position ต่อ symbol (averaging)
        )
        
        self.trade_history = TradeHistory(starting_balance=actual_balance)
        
        self.trailing_stop_manager = TrailingStopManager(
            trail_percent=Config.AGGRESSIVE_TRAILING_PERCENT,
            activation_profit=Config.AGGRESSIVE_TRAILING_ACTIVATION
        )
        
        # Intelligent systems (optional)
        self.event_manager = None
        if Config.ENABLE_EVENT_MANAGER:
            try:
                self.event_manager = EventManager()
            except Exception as e:
                logger.warning(f"⚠️ Event Manager ล้มเหลว: {e}")
        
        self.risk_manager = None
        if Config.ENABLE_ADVANCED_RISK:
            try:
                self.risk_manager = RiskManager(initial_capital=actual_balance)
            except Exception as e:
                logger.warning(f"⚠️ Risk Manager ล้มเหลว: {e}")
        
        self.alert_manager = None
        if Config.ENABLE_ENHANCED_ALERTS:
            try:
                self.alert_manager = AlertManager()
            except Exception as e:
                logger.warning(f"⚠️ Alert Manager ล้มเหลว: {e}")
        
        self.adaptive_strategy = None
        if Config.ENABLE_ADAPTIVE_STRATEGY:
            try:
                self.adaptive_strategy = AdaptiveStrategyEngine()
            except Exception as e:
                logger.warning(f"⚠️ Adaptive Strategy ล้มเหลว: {e}")
        
        # Log successful initialization
        systems_count = sum([self.event_manager is not None, self.risk_manager is not None, 
                            self.alert_manager is not None, self.adaptive_strategy is not None])
        logger.info(f"✅ ระบบอัจฉริยะพร้อม: {systems_count}/4 ระบบ")
        
        # Recovery tracking
        self.recovery_positions: Dict[str, List[Position]] = {}  # Track multiple positions per symbol
        self.martingale_level: Dict[str, int] = {}  # Track martingale level per symbol
        self.last_loss_symbol: Optional[str] = None
        self.consecutive_wins = 0
        self.consecutive_losses = 0
        
        # State tracking per symbol
        self.symbol_states: Dict[str, Dict] = {}
        for symbol in Config.SYMBOL_POOL:
            self.symbol_states[symbol] = {
                "last_macd_histogram": 0.0,
                "last_check_time": 0,
                "last_price": 0.0,
                "averaging_count": 0,
                "last_entry_price": 0.0
            }
        
        # Bot state
        self.running = False
        self.trading_paused = False
        self.profit_locked = False
        self.cycle_count = 0
        self.daily_peak_balance = actual_balance  # Track peak for drawdown protection
        
        # Telegram
        if Config.TELEGRAM_ENABLED:
            self.setup_telegram()
        
        # Load saved state
        self.load_state()
        
        logger.info("✅ Aggressive Bot initialized successfully")
    
    def setup_telegram(self):
        """Setup Telegram notifications and command handler"""
        try:
            from utils.telegram_commands import TelegramCommandHandler
            import threading
            
            # Create command handler
            self.telegram_handler = TelegramCommandHandler(
                bot_instance=self,
                bot_token=Config.TELEGRAM_BOT_TOKEN,
                chat_id=Config.TELEGRAM_CHAT_ID
            )
            
            # Start polling in background thread
            telegram_thread = threading.Thread(target=self.telegram_handler.start_polling, daemon=True)
            telegram_thread.start()
            
            logger.info("✅ Telegram integration enabled")
        except ImportError:
            logger.warning("⚠️ Telegram module not found")
            Config.TELEGRAM_ENABLED = False
        except Exception as e:
            logger.warning(f"⚠️ Telegram setup failed: {e}")
            Config.TELEGRAM_ENABLED = False
    
    def send_telegram(self, message: str):
        """Send Telegram notification"""
        if not Config.TELEGRAM_ENABLED:
            return
        
        try:
            import requests
            url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"
            data = {"chat_id": Config.TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
            requests.post(url, data=data, timeout=5)
        except Exception as e:
            logger.warning(f"Telegram send failed: {e}")
    
    def load_state(self):
        """Load bot state from file"""
        state_file = "bot_state_aggressive.json"
        if not os.path.exists(state_file):
            return
        
        try:
            with open(state_file, 'r') as f:
                state = json.load(f)
            
            self.profit_locked = state.get("profit_locked", False)
            
            # Restore balance
            if "current_balance" in state:
                self.trade_history.current_balance = state["current_balance"]
                self.trade_history.daily_start_balance = state.get("daily_start_balance", Config.STARTING_BALANCE)
            
            # Restore recovery state
            self.martingale_level = state.get("martingale_level", {})
            self.consecutive_wins = state.get("consecutive_wins", 0)
            self.consecutive_losses = state.get("consecutive_losses", 0)
            
            logger.info(f"📂 State loaded: Balance=${self.trade_history.current_balance:.2f}, Wins={self.consecutive_wins}, Losses={self.consecutive_losses}")
        
        except Exception as e:
            logger.warning(f"Failed to load state: {e}")
    
    def save_state(self):
        """Save bot state to file"""
        state_file = "bot_state_aggressive.json"
        try:
            state = {
                "profit_locked": self.profit_locked,
                "current_balance": self.trade_history.current_balance,
                "daily_start_balance": self.trade_history.daily_start_balance,
                "martingale_level": self.martingale_level,
                "consecutive_wins": self.consecutive_wins,
                "consecutive_losses": self.consecutive_losses,
                "last_update": datetime.now(UTC).isoformat()
            }
            
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2)
        
        except Exception as e:
            logger.warning(f"Failed to save state: {e}")
    
    def fetch_with_retry(self, endpoint_func, **kwargs) -> Optional[any]:
        """Fetch data with retry logic for API resilience"""
        for attempt in range(StrategyConstants.API_RETRY_ATTEMPTS):
            try:
                time.sleep(StrategyConstants.API_REQUEST_DELAY)
                result = endpoint_func(**kwargs)
                return result
            except Exception as e:
                if attempt < StrategyConstants.API_RETRY_ATTEMPTS - 1:
                    logger.warning(f"⚠️ API error (attempt {attempt+1}/{StrategyConstants.API_RETRY_ATTEMPTS}): {e}")
                    time.sleep(StrategyConstants.API_RETRY_DELAY)
                else:
                    logger.error(f"❌ API failed after {StrategyConstants.API_RETRY_ATTEMPTS} attempts: {e}")
                    return None
        return None
    
    def get_market_data(self, symbol: str, timeframe: str = None) -> Optional[Dict]:
        """Fetch candle data for a symbol with retry logic"""
        if timeframe is None:
            timeframe = Config.TIMEFRAME
        
        try:
            klines = self.fetch_with_retry(
                self.client.klines,
                symbol=symbol,
                interval=timeframe,
                limit=StrategyConstants.CANDLES_LIMIT
            )
            
            if not klines or len(klines) < 30:
                return None
            
            # Parse data
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            df['close'] = df['close'].astype(float)
            df['high'] = df['high'].astype(float)
            df['low'] = df['low'].astype(float)
            df['volume'] = df['volume'].astype(float)
            
            return {
                "close": df['close'].values,
                "high": df['high'].values,
                "low": df['low'].values,
                "volume": df['volume'].values,
                "current_price": float(df['close'].iloc[-1])
            }
        
        except Exception as e:
            logger.warning(f"❌ {symbol} data fetch error: {e}")
            return None
    
    def calculate_signals(self, symbol: str, data: Dict) -> Dict:
        """Calculate trading signals - Same as original bot"""
        close_prices = data["close"]
        high_prices = data["high"]
        low_prices = data["low"]
        volumes = data["volume"]
        current_price = data["current_price"]
        
        # Calculate indicators
        rsi = Indicators.calculate_rsi(close_prices, StrategyConstants.RSI_PERIOD)
        bb_upper, bb_middle, bb_lower = Indicators.calculate_bollinger_bands(
            close_prices, StrategyConstants.BB_PERIOD, StrategyConstants.BB_STD_DEV
        )
        macd_line, macd_signal, macd_hist = Indicators.calculate_macd(
            close_prices, StrategyConstants.MACD_FAST, StrategyConstants.MACD_SLOW, StrategyConstants.MACD_SIGNAL
        )
        atr = Indicators.calculate_atr(high_prices, low_prices, close_prices, StrategyConstants.ATR_PERIOD)
        
        # Calculate EMAs
        ema_fast = np.mean(close_prices[-StrategyConstants.EMA_FAST:]) if len(close_prices) >= StrategyConstants.EMA_FAST else current_price
        ema_slow = np.mean(close_prices[-StrategyConstants.EMA_SLOW:]) if len(close_prices) >= StrategyConstants.EMA_SLOW else current_price
        is_uptrend = ema_fast > ema_slow
        is_downtrend = ema_fast < ema_slow
        
        # Volume analysis
        avg_volume = np.mean(volumes[-StrategyConstants.VOLUME_PERIOD:])
        current_volume = volumes[-1]
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
        
        # Weighted signal scoring
        buy_strength = 0.0
        sell_strength = 0.0
        signal_details = []
        
        # RSI
        if rsi < StrategyConstants.RSI_OVERSOLD:
            buy_strength += 2.0 if rsi < 25 else 1.0
            signal_details.append("RSI<30")
        elif rsi > StrategyConstants.RSI_OVERBOUGHT:
            sell_strength += 2.0 if rsi > 75 else 1.0
            signal_details.append("RSI>70")
        
        # Bollinger Bands
        if current_price < bb_lower:
            buy_strength += 1.5
            signal_details.append("BB<Lower")
        elif current_price > bb_upper:
            sell_strength += 1.5
            signal_details.append("BB>Upper")
        
        # MACD
        last_macd_hist = self.symbol_states[symbol]["last_macd_histogram"]
        if last_macd_hist < 0 and macd_hist > 0:
            buy_strength += 1.5
            signal_details.append("MACD⬆")
        elif last_macd_hist > 0 and macd_hist < 0:
            sell_strength += 1.5
            signal_details.append("MACD⬇")
        
        self.symbol_states[symbol]["last_macd_histogram"] = macd_hist
        
        # Volume multiplier
        if volume_ratio > StrategyConstants.VOLUME_MULTIPLIER:
            buy_strength *= 1.2
            sell_strength *= 1.2
            signal_details.append(f"Vol{volume_ratio:.1f}x")
        
        # Trend alignment bonus
        if is_uptrend and buy_strength > 0:
            buy_strength += 0.5
            signal_details.append("↗Trend")
        elif is_downtrend and sell_strength > 0:
            sell_strength += 0.5
            signal_details.append("↘Trend")
        
        return {
            "buy_signals": 1 if buy_strength > 0 else 0,
            "sell_signals": 1 if sell_strength > 0 else 0,
            "buy_strength": buy_strength,
            "sell_strength": sell_strength,
            "signal_details": signal_details,
            "rsi": rsi,
            "macd_hist": macd_hist,
            "volume_ratio": volume_ratio,
            "atr": atr,
            "current_price": current_price,
            "bb_middle": bb_middle,
            "bb_upper": bb_upper,
            "bb_lower": bb_lower,
            "is_uptrend": is_uptrend,
            "is_downtrend": is_downtrend
        }
    
    def calculate_adaptive_position_size(self, symbol: str, stop_loss_percent: float, current_price: float, is_recovery: bool = False) -> float:
        """Calculate position size with win/loss streak adjustment"""
        base_risk = Config.MAX_LOSS_PER_TRADE / 100
        
        # Adjust based on win/loss streak
        if self.consecutive_wins >= 3:
            size_multiplier = Config.AGGRESSIVE_WIN_STREAK_BONUS
            logger.info(f"🔥 Win streak! Size +{(size_multiplier-1)*100:.0f}%")
        elif self.consecutive_losses >= 2 and not is_recovery:
            size_multiplier = Config.AGGRESSIVE_LOSS_REDUCTION
            logger.info(f"⚠️ Loss streak, reducing size -{(1-size_multiplier)*100:.0f}%")
        else:
            size_multiplier = 1.0
        
        # Recovery mode - use Martingale
        if is_recovery and Config.AGGRESSIVE_ENABLE_SMART_MARTINGALE:
            martingale_mult = Config.AGGRESSIVE_MARTINGALE_MULTIPLIER
            level = self.martingale_level.get(symbol, 0)
            size_multiplier *= (martingale_mult ** level)
            logger.info(f"🔄 Martingale Level {level}: Size {size_multiplier:.2f}x")
        
        risk_amount = self.trade_history.current_balance * base_risk * size_multiplier
        
        # Calculate quantity
        stop_loss_distance = current_price * (stop_loss_percent / 100)
        position_size = risk_amount / stop_loss_distance if stop_loss_distance > 0 else 0
        quantity = position_size / current_price if current_price > 0 else 0
        
        # Minimum quantity
        min_qty = 0.001
        quantity = max(quantity, min_qty)
        
        return quantity
    
    def should_enter_recovery_position(self, symbol: str, current_price: float) -> bool:
        """Check if should add averaging/recovery position"""
        if not Config.AGGRESSIVE_ENABLE_AVERAGING:
            return False
        
        # Check if we have an existing position in recovery
        if symbol not in self.recovery_positions or not self.recovery_positions[symbol]:
            return False
        
        last_position = self.recovery_positions[symbol][-1]
        
        # Check averaging count
        avg_count = self.symbol_states[symbol]["averaging_count"]
        if avg_count >= Config.AGGRESSIVE_MAX_AVERAGING_TIMES:
            return False
        
        # Check price distance
        price_diff_pct = abs(current_price - last_position.entry_price) / last_position.entry_price * 100
        
        if price_diff_pct >= Config.AGGRESSIVE_AVERAGING_DISTANCE:
            # Check if price moved in losing direction
            if last_position.side == "BUY" and current_price < last_position.entry_price:
                return True
            elif last_position.side == "SELL" and current_price > last_position.entry_price:
                return True
        
        return False
    
    def try_entry(self, symbol: str, signals: Dict, data: Dict):
        """Try to enter a position with aggressive strategy"""
        if self.trading_paused:
            return
        
        # ✅ Check Event Manager before trading (เช็คข่าวก่อนเทรด)
        if self.event_manager and Config.ENABLE_EVENT_MANAGER:
            decision = self.event_manager.get_trading_decision()
            
            # EMERGENCY: Stop all trading
            if decision["status"] == "EMERGENCY":
                if self.cycle_count % 10 == 0:  # Show warning every 10 cycles
                    logger.warning(f"🔴 EMERGENCY: {decision['reason']}")
                return
            
            # PAUSE: Only allow closing positions
            if decision["status"] == "PAUSE":
                if self.cycle_count % 20 == 0:
                    logger.warning(f"🟠 PAUSE: {decision['reason']}")
                return
            
            # CAUTION: Reduce signal strength requirement
            if decision["status"] == "CAUTION":
                signals["buy_strength"] *= 0.7
                signals["sell_strength"] *= 0.7
                if self.cycle_count % 30 == 0:
                    logger.warning(f"🟡 CAUTION: {decision['reason']}")
        
        # Use aggressive thresholds
        buy_strength = signals.get("buy_strength", 0)
        sell_strength = signals.get("sell_strength", 0)
        
        # Lower threshold for entry
        if buy_strength < Config.AGGRESSIVE_MIN_SIGNAL_STRENGTH and sell_strength < Config.AGGRESSIVE_MIN_SIGNAL_STRENGTH:
            return
        
        # Determine side
        if buy_strength >= Config.AGGRESSIVE_MIN_SIGNAL_STRENGTH and buy_strength > sell_strength:
            side = "BUY"
            signal_strength = buy_strength
        elif sell_strength >= Config.AGGRESSIVE_MIN_SIGNAL_STRENGTH and sell_strength > buy_strength:
            side = "SELL"
            signal_strength = sell_strength
        else:
            return
        
        # Check if this is a recovery entry
        is_recovery = (self.last_loss_symbol == symbol and 
                      self.consecutive_losses > 0 and
                      self.martingale_level.get(symbol, 0) < Config.AGGRESSIVE_MAX_MARTINGALE_LEVEL)
        
        # Check if should do averaging
        is_averaging = self.should_enter_recovery_position(symbol, signals["current_price"])
        
        # Check basic filters (relaxed for recovery)
        if not is_recovery and not is_averaging:
            current_hour = datetime.now(UTC).hour
            if not (StrategyConstants.TRADING_START_HOUR <= current_hour < StrategyConstants.TRADING_END_HOUR):
                return
        
        # Position limits (allow extra for recovery)
        current_positions = len(self.position_manager.get_all_positions())
        max_positions = Config.MAX_TOTAL_POSITIONS + (3 if is_recovery or is_averaging else 0)
        
        if current_positions >= max_positions:
            return
        
        # Calculate entry parameters
        current_price = signals["current_price"]
        
        # Aggressive TP/SL
        if signal_strength >= 5.0:
            take_profit_percent = Config.AGGRESSIVE_STRONG_TP
        elif signal_strength >= 3.5:
            take_profit_percent = Config.AGGRESSIVE_MEDIUM_TP
        else:
            take_profit_percent = Config.AGGRESSIVE_QUICK_TP
        
        stop_loss_percent = Config.AGGRESSIVE_TIGHT_SL
        
        # Calculate prices
        if side == "BUY":
            stop_loss = current_price * (1 - stop_loss_percent / 100)
            take_profit = current_price * (1 + take_profit_percent / 100)
        else:
            stop_loss = current_price * (1 + stop_loss_percent / 100)
            take_profit = current_price * (1 - take_profit_percent / 100)
        
        # Calculate adaptive position size
        quantity = self.calculate_adaptive_position_size(symbol, stop_loss_percent, current_price, is_recovery or is_averaging)
        
        # Create position
        position = Position(
            symbol=symbol,
            side=side,
            entry_price=current_price,
            quantity=quantity,
            stop_loss=stop_loss,
            take_profit=take_profit,
            confluence_score=int(signal_strength)
        )
        
        # Track recovery positions
        if is_recovery or is_averaging:
            if symbol not in self.recovery_positions:
                self.recovery_positions[symbol] = []
            self.recovery_positions[symbol].append(position)
            
            if is_averaging:
                self.symbol_states[symbol]["averaging_count"] += 1
        
        # Add to position manager
        if self.position_manager.add_position(position):
            entry_type = "🔄 RECOVERY" if is_recovery else ("📊 AVERAGING" if is_averaging else "🟢 ENTRY")
            
            logger.info("="*80)
            logger.info(f"{entry_type}: {symbol} {side} @ ${current_price:.2f}")
            logger.info("-"*80)
            logger.info(f"🎯 TP: ${take_profit:.2f} (+{take_profit_percent:.2f}%) | SL: ${stop_loss:.2f} (-{stop_loss_percent}%)")
            logger.info(f"📏 Size: {quantity:.6f} | Value: ${current_price * quantity:.2f}")
            logger.info(f"💡 Strength: {signal_strength:.1f} | Signals: {', '.join(signals['signal_details'][:3])}")
            
            # Intelligent system context
            context_parts = []
            if self.adaptive_strategy:
                regime = self.adaptive_strategy.current_regime.value[:3].upper()
                context_parts.append(f"Regime:{regime}")
            if self.event_manager:
                decision = self.event_manager.get_trading_decision()
                context_parts.append(f"Evt:{decision['status'][:4]}")
            if context_parts:
                context_str = " | ".join(context_parts)
                logger.info(f"🤖 Context: {context_str}")
            
            if is_recovery:
                level = self.martingale_level.get(symbol, 0)
                logger.info(f"🔄 Martingale Level: {level}/{Config.AGGRESSIVE_MAX_MARTINGALE_LEVEL}")
            elif is_averaging:
                avg_count = self.symbol_states[symbol]["averaging_count"]
                logger.info(f"📊 Averaging: {avg_count}/{Config.AGGRESSIVE_MAX_AVERAGING_TIMES}")
            
            logger.info("="*80)
            
            # Telegram
            self.send_telegram(
                f"{entry_type} <b>{symbol}</b>\n"
                f"Side: {side} @ ${current_price:.2f}\n"
                f"TP: ${take_profit:.2f} (+{take_profit_percent:.2f}%)\n"
                f"SL: ${stop_loss:.2f} (-{stop_loss_percent}%)\n"
                f"Size: {quantity:.4f} (${current_price * quantity:.2f})\n"
                f"Strength: {signal_strength:.1f}\n"
                f"{', '.join(signals['signal_details'])}"
            )
            
            self.save_state()
    
    def check_exits(self):
        """Check all positions for exit conditions with aggressive timing"""
        positions_to_close = []
        
        for position in self.position_manager.get_all_positions():
            symbol = position.symbol
            
            # Get current price
            data = self.get_market_data(symbol)
            if not data:
                continue
            
            current_price = data["current_price"]
            
            # Update trailing stop (more aggressive)
            if Config.TRAILING_STOP_ENABLED:
                self.trailing_stop_manager.update_trailing_stop(position, current_price)
            
            exit_reason = None
            
            # 1. Take Profit (primary exit)
            if position.side == "BUY" and current_price >= position.take_profit:
                exit_reason = "TP ✅"
            elif position.side == "SELL" and current_price <= position.take_profit:
                exit_reason = "TP ✅"
            
            # 2. Stop Loss
            if exit_reason is None:
                if position.side == "BUY" and current_price <= position.stop_loss:
                    exit_reason = "SL ❌"
                elif position.side == "SELL" and current_price >= position.stop_loss:
                    exit_reason = "SL ❌"
            
            # 3. Fast Time Stop (aggressive)
            if exit_reason is None:
                time_in_position = (datetime.now(UTC) - position.entry_time).total_seconds()
                is_recovery = symbol in self.recovery_positions and position in self.recovery_positions.get(symbol, [])
                time_limit = Config.AGGRESSIVE_TIME_STOP_RECOVERY if is_recovery else Config.AGGRESSIVE_TIME_STOP_FAST
                
                if time_in_position >= time_limit:
                    exit_reason = f"Time ({int(time_in_position)}s)"
            
            # Close if triggered
            if exit_reason:
                positions_to_close.append((position, current_price, exit_reason))
        
        # Process exits
        for position, exit_price, exit_reason in positions_to_close:
            self.close_position(position, exit_price, exit_reason)
    
    def close_position(self, position: Position, exit_price: float, exit_reason: str):
        """Close a position and update recovery tracking"""
        position.exit_price = exit_price
        position.exit_time = datetime.now(UTC)
        position.exit_reason = exit_reason
        
        # Calculate P&L
        if position.side == "BUY":
            profit_pct = ((exit_price - position.entry_price) / position.entry_price) * 100
        else:
            profit_pct = ((position.entry_price - exit_price) / position.entry_price) * 100
        
        position.profit_percent = profit_pct
        position_value = position.entry_price * position.quantity
        profit_amount = (profit_pct / 100) * position_value
        position.profit_amount = profit_amount
        
        # Update streak counters
        if profit_pct > 0:
            self.consecutive_wins += 1
            self.consecutive_losses = 0
            
            # Reset martingale on win
            symbol = position.symbol
            if symbol in self.martingale_level:
                logger.info(f"✅ Win! Resetting martingale for {symbol}")
                self.martingale_level[symbol] = 0
            
            # Clear recovery positions
            if symbol in self.recovery_positions:
                self.recovery_positions[symbol] = []
                self.symbol_states[symbol]["averaging_count"] = 0
        else:
            self.consecutive_losses += 1
            self.consecutive_wins = 0
            self.last_loss_symbol = position.symbol
            
            # Increment martingale level
            symbol = position.symbol
            if symbol not in self.martingale_level:
                self.martingale_level[symbol] = 0
            
            if self.martingale_level[symbol] < Config.AGGRESSIVE_MAX_MARTINGALE_LEVEL:
                self.martingale_level[symbol] += 1
                logger.warning(f"🔄 Loss! Martingale {symbol} → Level {self.martingale_level[symbol]}")
        
        # Remove from position manager
        self.position_manager.remove_position(position.position_id)
        
        # Add to trade history
        self.trade_history.add_trade(position)
        
        # Calculate duration
        duration = int((position.exit_time - position.entry_time).total_seconds())
        
        # Get stats
        win_rate = self.trade_history.get_win_rate()
        daily_pnl = self.trade_history.get_daily_pnl_percent()
        
        # Log exit
        emoji = "✅" if profit_pct > 0 else "❌"
        color = "🟢" if profit_pct > 0 else "🔴"
        
        logger.info("="*80)
        logger.info(f"{color} EXIT: {position.symbol} {position.side} @ ${exit_price:.2f} {emoji}")
        logger.info("-"*80)
        logger.info(f"📊 P&L: ${profit_amount:+.2f} ({profit_pct:+.2f}%) | Duration: {duration}s")
        logger.info(f"💼 Entry: ${position.entry_price:.2f} → Exit: ${exit_price:.2f}")
        logger.info(f"📝 Reason: {exit_reason}")
        logger.info("-"*80)
        logger.info(f"💰 Balance: ${self.trade_history.current_balance:.2f} | Daily: {daily_pnl:+.2f}% | WR: {win_rate:.1f}%")
        logger.info(f"🔥 Streak: {self.consecutive_wins}W / {self.consecutive_losses}L")
        logger.info("="*80)
        
        # Telegram
        self.send_telegram(
            f"{emoji} <b>EXIT {position.symbol}</b>\n"
            f"P&L: {profit_pct:+.2f}% (${profit_amount:+.2f})\n"
            f"Entry: ${position.entry_price:.2f}\n"
            f"Exit: ${exit_price:.2f}\n"
            f"Reason: {exit_reason}\n"
            f"Duration: {duration}s\n\n"
            f"Balance: ${self.trade_history.current_balance:.2f}\n"
            f"Daily: {daily_pnl:+.2f}%\n"
            f"Streak: {self.consecutive_wins}W/{self.consecutive_losses}L"
        )
        
        self.save_state()
        self.check_daily_status()
    
    def check_daily_status(self):
        """Check daily limits with STRICT 5% target and immediate stop"""
        daily_pnl = self.trade_history.get_daily_pnl_percent()
        current_balance = self.trade_history.current_balance
        profit_amount = current_balance - self.trade_history.daily_start_balance
        
        # Update peak balance for drawdown tracking
        if current_balance > self.daily_peak_balance:
            self.daily_peak_balance = current_balance
        
        # 🎯 STRICT 5% TARGET - IMMEDIATE STOP (Phase 4)
        if daily_pnl >= Config.AGGRESSIVE_DAILY_TARGET:
            logger.info("="*80)
            logger.info(f"🎯 5% TARGET REACHED: +{daily_pnl:.2f}% - STOPPING IMMEDIATELY!".center(80))
            logger.info("="*80)
            self.send_telegram(
                f"🎯 <b>5% DAILY TARGET ACHIEVED!</b>\n\n"
                f"✅ Daily P&L: +{daily_pnl:.2f}%\n"
                f"💰 Profit: ${profit_amount:+.2f}\n"
                f"💼 Balance: ${current_balance:.2f}\n\n"
                f"🛑 Bot stopped immediately per strategy!\n"
                f"⏰ Mission completed for today! 🎉"
            )
            self.running = False
            return
        
        # 📊 Profit milestone notification at +3% (Phase 4)
        if not self.profit_locked and daily_pnl >= Config.AGGRESSIVE_QUICK_PROFIT_LOCK:
            self.profit_locked = True
            logger.info(f"📊 Approaching target: +{daily_pnl:.2f}% (Target: +5%)")
            self.send_telegram(
                f"📊 <b>Good Progress!</b>\n"
                f"Daily: +{daily_pnl:.2f}%\n"
                f"Target: +{Config.AGGRESSIVE_DAILY_TARGET}%\n"
                f"Remaining: {Config.AGGRESSIVE_DAILY_TARGET - daily_pnl:.2f}%\n"
                f"Keep going! 🚀"
            )
        
        # 🛡️ INTRADAY DRAWDOWN PROTECTION (Phase 4)
        drawdown_from_peak = ((current_balance - self.daily_peak_balance) / self.daily_peak_balance) * 100
        if drawdown_from_peak <= Config.AGGRESSIVE_MAX_INTRADAY_DRAWDOWN:
            logger.error("="*80)
            logger.error(f"🛡️ INTRADAY DRAWDOWN LIMIT: {drawdown_from_peak:.2f}% from peak".center(80))
            logger.error("="*80)
            self.send_telegram(
                f"🛡️ <b>DRAWDOWN PROTECTION</b>\n\n"
                f"Drawdown: {drawdown_from_peak:.2f}%\n"
                f"Peak: ${self.daily_peak_balance:.2f}\n"
                f"Current: ${current_balance:.2f}\n\n"
                f"Bot stopped to protect capital."
            )
            self.running = False
            return
        
        # 🛑 MAX DAILY LOSS
        if daily_pnl <= Config.AGGRESSIVE_MAX_DAILY_LOSS:
            logger.error(f"🛑 MAX DAILY LOSS: {daily_pnl:.2f}%")
            self.send_telegram(
                f"🛑 <b>MAX LOSS LIMIT</b>\n"
                f"Daily: {daily_pnl:.2f}%\n"
                f"Loss: ${-profit_amount:.2f}\n"
                f"Bot stopped."
            )
            self.running = False
    
    def run_cycle(self):
        """Run one trading cycle"""
        self.cycle_count += 1
        
        # Check exits first
        self.check_exits()
        
        # Rotate symbols
        if self.symbol_manager.should_rotate():
            current_positions = {
                symbol: self.position_manager.get_symbol_position_count(symbol)
                for symbol in Config.SYMBOL_POOL
            }
            self.symbol_manager.rotate_symbols(current_positions)
        
        # Scan for entries
        active_symbols = self.symbol_manager.get_active_symbols()
        
        for symbol in active_symbols:
            data = self.get_market_data(symbol)
            if not data:
                continue
            
            signals = self.calculate_signals(symbol, data)
            self.try_entry(symbol, signals, data)
        
        # Status display every cycle
        self._display_status()
    
    def _display_status(self):
        """Display compact status every cycle"""
        positions = self.position_manager.get_all_positions()
        pos_count = len(positions)
        daily_pnl = self.trade_history.get_daily_pnl_percent()
        balance = self.trade_history.current_balance
        win_rate = self.trade_history.get_win_rate()
        total_trades = len(self.trade_history.trades)
        
        perf = "🚀" if daily_pnl > 3 else ("📈" if daily_pnl > 0 else "🔴")
        
        # Event status icon
        evt_status = "✅"
        if self.event_manager:
            decision = self.event_manager.get_trading_decision()
            evt_status = {
                "CLEAR": "✅",
                "CAUTION": "🟡",
                "PAUSE": "🟠",
                "EMERGENCY": "🔴"
            }.get(decision["status"], "❓")
        
        # Every 10 cycles: Show detailed status
        if self.cycle_count % 10 == 0:
            logger.info("="*80)
            logger.info(f"Cycle #{self.cycle_count:04d} │ {perf} ${balance:.2f} ({daily_pnl:+.2f}%)")
            logger.info("-"*80)
            logger.info(f"Trades: {total_trades} │ WR: {win_rate:.1f}% │ "
                       f"Positions: {pos_count}/{Config.MAX_TOTAL_POSITIONS} │ "
                       f"Streak: {self.consecutive_wins}W/{self.consecutive_losses}L")
            
            # Intelligent Systems Status
            if self.event_manager or self.risk_manager or self.adaptive_strategy:
                logger.info("-"*80)
                logger.info("🤖 ระบบอัจฉริยะ")
                
                # Event Manager
                if self.event_manager:
                    decision = self.event_manager.get_trading_decision()
                    status_icon = {
                        "CLEAR": "✅",
                        "CAUTION": "🟡",
                        "PAUSE": "🟠",
                        "EMERGENCY": "🔴"
                    }.get(decision["status"], "❓")
                    
                    logger.info(f"📅 Event Manager: {status_icon} {decision['status']}")
                    logger.info(f"   → {decision['reason'][:60]}")
                    
                    # Sentiment
                    sentiment = self.event_manager.get_sentiment_signal()
                    logger.info(f"💭 ความเชื่อมั่น: {sentiment['message'][:60]}")
                
                # Risk Manager
                if self.risk_manager:
                    metrics = self.risk_manager.get_portfolio_metrics()
                    logger.info(f"⚡ ความเสี่ยง: Exposure {metrics.total_exposure:.1%} | "
                               f"Correlation {metrics.correlation_score:.2f} | "
                               f"Regime: {metrics.volatility_regime.upper()}")
                    
                    if metrics.current_drawdown > 0.05:
                        logger.info(f"   ⚠️ Drawdown: {metrics.current_drawdown:.1%}")
                
                # Adaptive Strategy
                if self.adaptive_strategy:
                    regime = self.adaptive_strategy.current_regime.value.upper()
                    mode = self.adaptive_strategy.current_params.mode.value.upper()
                    logger.info(f"🎯 กลยุทธ์: ตลาด {regime} | โหมด: {mode}")
            
            logger.info("="*80)
        
        # Every cycle: Compact one-liner
        else:
            logger.info(
                f"Cycle #{self.cycle_count:04d} │ "
                f"{perf}${balance:.2f} ({daily_pnl:+.1f}%) │ "
                f"Pos: {pos_count}/{Config.MAX_TOTAL_POSITIONS} │ "
                f"WR: {win_rate:.0f}% │ "
                f"Event: {evt_status} │ "
                f"Streak: {self.consecutive_wins}W/{self.consecutive_losses}L"
            )
    
    def run(self):
        """Main bot loop with aggressive timing"""
        self.running = True
        logger.info("✅ Aggressive Bot is running... Press Ctrl+C to stop\n")
        
        self.send_telegram(
            f"🔥 <b>Aggressive Recovery Bot Started</b>\n\n"
            f"💰 Capital: ${self.trade_history.current_balance:.2f}\n"
            f"🎯 Target: +{Config.AGGRESSIVE_DAILY_TARGET}% to +{Config.AGGRESSIVE_DAILY_MAX}%\n"
            f"⚡ Strategy: Fast scalping + Smart recovery\n"
            f"🔄 Martingale: {Config.AGGRESSIVE_MARTINGALE_MULTIPLIER}x up to {Config.AGGRESSIVE_MAX_MARTINGALE_LEVEL} levels\n\n"
            f"✅ Ready to trade!"
        )
        
        try:
            while self.running:
                self.run_cycle()
                time.sleep(Config.CHECK_INTERVAL)
        
        except KeyboardInterrupt:
            logger.info("\n\n🛑 Bot stopped by user")
        
        except Exception as e:
            logger.error(f"\n\n❌ Fatal error: {e}")
            self.send_telegram(f"❌ <b>BOT ERROR</b>\n{str(e)}")
        
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Cleanup and final reporting"""
        logger.info("="*60)
        logger.info("🛑 Shutting down Aggressive Bot...")
        logger.info("="*60)
        
        # Close remaining positions
        open_positions = self.position_manager.get_all_positions()
        if open_positions:
            logger.warning(f"⚠️ Closing {len(open_positions)} positions...")
            for position in open_positions:
                data = self.get_market_data(position.symbol)
                if data:
                    self.close_position(position, data["current_price"], "🛑 Shutdown")
        
        # Statistics
        total_trades = len(self.trade_history.trades)
        win_rate = self.trade_history.get_win_rate()
        daily_pnl = self.trade_history.get_daily_pnl_percent()
        profit = self.trade_history.current_balance - self.trade_history.daily_start_balance
        
        logger.info("="*60)
        logger.info("📊 Final Summary")
        logger.info("="*60)
        logger.info(f"Total Trades: {total_trades}")
        logger.info(f"Win Rate: {win_rate:.1f}%")
        logger.info(f"Daily P&L: {daily_pnl:+.2f}% (${profit:+.2f})")
        logger.info(f"Final Balance: ${self.trade_history.current_balance:.2f}")
        logger.info(f"Win Streak: {self.consecutive_wins} | Loss Streak: {self.consecutive_losses}")
        logger.info("="*60)
        
        # Final telegram
        self.send_telegram(
            f"🛑 <b>Aggressive Bot Stopped</b>\n\n"
            f"Trades: {total_trades}\n"
            f"Win Rate: {win_rate:.1f}%\n"
            f"Daily P&L: {daily_pnl:+.2f}%\n"
            f"Profit: ${profit:+.2f}\n"
            f"Final: ${self.trade_history.current_balance:.2f}\n\n"
            f"Target: {'✅' if daily_pnl >= Config.AGGRESSIVE_DAILY_TARGET else '❌'}"
        )
        
        self.save_state()
        logger.info("✅ Shutdown complete")


# ===================== ENTRY POINT =====================
if __name__ == "__main__":
    bot = AggressiveRecoveryBot()
    bot.run()

