"""
Daily $100 Scalping Bot - Ultra-Fast Multi-Symbol Trading
Target: 2-5% daily profit on $100 capital
Strategy: 1-minute confluence scalping across 20 symbols
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
    __version__ = "3.0.0"
    BOT_NAME = "BOT SCALPING อัจฉริยะ"


# ===================== LOGGING SETUP =====================
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


# ===================== MAIN BOT ====================
class DailyScalpingBot:
    """Main Daily Scalping Bot - Multi-Symbol Edition"""
    
    def __init__(self, user_id: Optional[int] = None, config_dict: Optional[dict] = None):
        """Initialize bot with optional user_id and config for multi-user support"""
        self.user_id = user_id
        self.config_override = config_dict
        self.running = True
        
        logger.info("="*80)
        logger.info(f"🚀 {BOT_NAME} v{__version__}".center(80))
        if user_id:
            logger.info(f"👤 User ID: {user_id}".center(80))
        logger.info("="*80)
        logger.info(f"💼 โหมด: {'DEMO (ทดสอบปลอดภัย)' if Config.DEMO_MODE else 'LIVE ⚠️ เงินจริง!'}")
        logger.info(f"📊 Symbols: {len(Config.SYMBOL_POOL)} pool, {Config.MAX_ACTIVE_SYMBOLS} active")
        logger.info(f"⏱️  Timeframe: {Config.TIMEFRAME} (Scalping เร็ว)")
        logger.info(f"🎯 เป้าหมายรายวัน: +{Config.DAILY_PROFIT_TARGET}% ถึง +{Config.DAILY_MAX_TARGET}%")
        logger.info("-"*80)
        logger.info("🤖 ระบบอัจฉริยะที่เปิดใช้งาน".center(80))
        logger.info("-"*80)
        
        # Show which intelligent features are enabled
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
        
        logger.info(f"💰 ทุนเริ่มต้น: ${actual_balance:,.2f}")
        
        # Core managers
        self.symbol_manager = SymbolManager(
            symbol_pool=Config.SYMBOL_POOL,
            max_active=Config.MAX_ACTIVE_SYMBOLS,
            rotation_interval=StrategyConstants.SYMBOL_ROTATION_INTERVAL
        )
        
        self.position_manager = PositionManager(
            max_total_positions=Config.MAX_TOTAL_POSITIONS,
            max_per_symbol=Config.MAX_POSITIONS_PER_SYMBOL
        )
        
        self.trade_history = TradeHistory(starting_balance=actual_balance)
        
        self.trailing_stop_manager = TrailingStopManager(
            trail_percent=Config.DAILY_TRAILING_PERCENT,
            activation_profit=Config.DAILY_TRAILING_ACTIVATION
        )
        
        # ==================== INTELLIGENT SYSTEMS ====================
        # Event Manager - Handle economic calendar, crypto events, sentiment
        self.event_manager = None
        if Config.ENABLE_EVENT_MANAGER:
            try:
                self.event_manager = EventManager()
            except Exception as e:
                logger.warning(f"⚠️ Event Manager ล้มเหลว: {e}")
        
        # Risk Manager - Advanced position sizing, correlation, drawdown management
        self.risk_manager = None
        if Config.ENABLE_ADVANCED_RISK:
            try:
                self.risk_manager = RiskManager(initial_capital=actual_balance)
            except Exception as e:
                logger.warning(f"⚠️ Risk Manager ล้มลว: {e}")
        
        # Alert Manager - Enhanced notifications with severity tiers
        self.alert_manager = None
        if Config.ENABLE_ENHANCED_ALERTS:
            try:
                self.alert_manager = AlertManager()
            except Exception as e:
                logger.warning(f"⚠️ Alert Manager ล้มเหลว: {e}")
        
        # Adaptive Strategy - Market regime detection and parameter optimization
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
        
        # State tracking per symbol
        self.symbol_states: Dict[str, Dict] = {}
        for symbol in Config.SYMBOL_POOL:
            self.symbol_states[symbol] = {
                "last_macd_histogram": 0.0,
                "last_check_time": 0,
                "last_price": 0.0  # For cascade detection
            }
        
        # Bot state
        self.running = False
        self.trading_paused = False
        self.recovery_mode = False
        self.profit_locked = False
        self.cycle_count = 0
        
        # Telegram
        if Config.TELEGRAM_ENABLED:
            self.setup_telegram()
        
        # Load saved state
        self.load_state()
        
        logger.info("✅ Bot initialized successfully")
    
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
        if not os.path.exists(StrategyConstants.STATE_FILE):
            return
        
        try:
            with open(StrategyConstants.STATE_FILE, 'r') as f:
                state = json.load(f)
            
            self.recovery_mode = state.get("recovery_mode", False)
            self.profit_locked = state.get("profit_locked", False)
            
            # Restore balance
            if "current_balance" in state:
                self.trade_history.current_balance = state["current_balance"]
                self.trade_history.daily_start_balance = state.get("daily_start_balance", self.trade_history.daily_start_balance)
            
            logger.info(f"📂 State loaded: Balance=${self.trade_history.current_balance:.2f}, Recovery={self.recovery_mode}")
        
        except Exception as e:
            logger.warning(f"Failed to load state: {e}")
    
    def save_state(self):
        """Save bot state to file"""
        try:
            state = {
                "recovery_mode": self.recovery_mode,
                "profit_locked": self.profit_locked,
                "current_balance": self.trade_history.current_balance,
                "daily_start_balance": self.trade_history.daily_start_balance,
                "last_update": datetime.now(UTC).isoformat()
            }
            
            with open(StrategyConstants.STATE_FILE, 'w') as f:
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
            # Use retry logic
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
    
    def get_trend_from_higher_tf(self, symbol: str, timeframe: str) -> Optional[str]:
        """Get trend direction from higher timeframe for multi-TF confirmation"""
        try:
            data = self.get_market_data(symbol, timeframe)
            if not data:
                return None
            
            close_prices = data["close"]
            
            # Calculate EMAs
            ema_fast = np.mean(close_prices[-Config.EMA_FAST:]) if len(close_prices) >= Config.EMA_FAST else None
            ema_slow = np.mean(close_prices[-Config.EMA_SLOW:]) if len(close_prices) >= Config.EMA_SLOW else None
            
            if ema_fast is None or ema_slow is None:
                return None
            
            # Determine trend
            if ema_fast > ema_slow * 1.002:  # At least 0.2% above
                return "up"
            elif ema_fast < ema_slow * 0.998:  # At least 0.2% below
                return "down"
            else:
                return "sideways"
                
        except Exception as e:
            logger.debug(f"Error getting {timeframe} trend for {symbol}: {e}")
            return None
    
    def check_volume_quality(self, volumes: np.ndarray) -> bool:
        """Check if current volume meets quality threshold"""
        if not Config.USE_VOLUME_QUALITY_FILTER:
            return True
        
        if len(volumes) < StrategyConstants.VOLUME_PERIOD:
            return True  # Not enough data, allow trade
        
        avg_volume = np.mean(volumes[-StrategyConstants.VOLUME_PERIOD:])
        current_volume = volumes[-1]
        
        if avg_volume == 0:
            return True
        
        volume_ratio = current_volume / avg_volume
        return volume_ratio >= Config.MIN_VOLUME_RATIO
    
    def calculate_progressive_recovery_size(self, consecutive_losses: int) -> float:
        """Calculate position size multiplier using progressive Kelly-based recovery"""
        if not StrategyConstants.USE_PROGRESSIVE_RECOVERY:
            return 1.0
        
        if consecutive_losses == 0:
            return 1.0
        elif consecutive_losses == 1:
            return StrategyConstants.RECOVERY_SIZE_LOSS_1
        elif consecutive_losses == 2:
            return StrategyConstants.RECOVERY_SIZE_LOSS_2
        else:  # 3+ losses
            return StrategyConstants.RECOVERY_SIZE_LOSS_3
    
    def get_adaptive_max_positions(self) -> int:
        """Get dynamic position limit based on recent performance"""
        if not StrategyConstants.USE_ADAPTIVE_FREQUENCY:
            return Config.MAX_TOTAL_POSITIONS
        
        stats = self.trade_history.get_daily_stats()
        
        if not stats or stats.total_trades < 5:
            return Config.MAX_TOTAL_POSITIONS  # Default until enough data
        
        win_rate = stats.win_rate
        daily_pnl = stats.daily_pnl_percent
        
        # Good performance - increase frequency
        if win_rate >= StrategyConstants.ADAPTIVE_GOOD_PERFORMANCE_WR and daily_pnl >= StrategyConstants.ADAPTIVE_GOOD_PERFORMANCE_PNL:
            return Config.MAX_TOTAL_POSITIONS
        
        # Bad performance - reduce frequency
        elif win_rate <= StrategyConstants.ADAPTIVE_BAD_PERFORMANCE_WR or daily_pnl <= StrategyConstants.ADAPTIVE_BAD_PERFORMANCE_PNL:
            return max(3, Config.MAX_TOTAL_POSITIONS - 3)  # Min 3 positions
        
        # Neutral - maintain current
        return Config.MAX_TOTAL_POSITIONS
    
    def calculate_signals(self, symbol: str, data: Dict) -> Dict:
        """Calculate trading signals for a symbol with weighted scoring"""
        close_prices = data["close"]
        high_prices = data["high"]
        low_prices = data["low"]
        volumes = data["volume"]
        current_price = data["current_price"]
        
        # Calculate indicators
        rsi = Indicators.calculate_rsi(close_prices, Config.RSI_PERIOD)
        bb_upper, bb_middle, bb_lower = Indicators.calculate_bollinger_bands(
            close_prices, Config.BB_PERIOD, Config.BB_STD_DEV
        )
        macd_line, macd_signal, macd_hist = Indicators.calculate_macd(
            close_prices, Config.MACD_FAST, Config.MACD_SLOW, Config.MACD_SIGNAL
        )
        atr = Indicators.calculate_atr(high_prices, low_prices, close_prices, Config.ATR_PERIOD)
        
        # Calculate EMAs for trend filter
        ema_fast = np.mean(close_prices[-Config.EMA_FAST:]) if len(close_prices) >= Config.EMA_FAST else current_price
        ema_slow = np.mean(close_prices[-Config.EMA_SLOW:]) if len(close_prices) >= Config.EMA_SLOW else current_price
        is_uptrend = ema_fast > ema_slow
        is_downtrend = ema_fast < ema_slow
        
        # Volume analysis
        avg_volume = np.mean(volumes[-StrategyConstants.VOLUME_PERIOD:])
        current_volume = volumes[-1]
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
        
        # Weighted signal scoring (NEW!)
        buy_strength = 0.0
        sell_strength = 0.0
        signal_details = []
        
        # 1. RSI Signal (weighted by extremity)
        if rsi < Config.RSI_OVERSOLD:
            if rsi < StrategyConstants.RSI_EXTREME_THRESHOLD:
                buy_strength += 2.0  # Very oversold
                signal_details.append(f"RSI<{StrategyConstants.RSI_EXTREME_THRESHOLD}⭐")
            else:
                buy_strength += 1.0
                signal_details.append("RSI<30")
        elif rsi > Config.RSI_OVERBOUGHT:
            if rsi > (100 - StrategyConstants.RSI_EXTREME_THRESHOLD):
                sell_strength += 2.0  # Very overbought
                signal_details.append(f"RSI>{100-StrategyConstants.RSI_EXTREME_THRESHOLD}⭐")
            else:
                sell_strength += 1.0
                signal_details.append("RSI>70")
        
        # 2. Bollinger Bands Signal (weighted by distance)
        bb_width_percent = ((bb_upper - bb_lower) / bb_middle) * 100 if bb_middle > 0 else 0
        bb_distance_from_lower = abs(current_price - bb_lower) / (bb_upper - bb_lower) if (bb_upper - bb_lower) > 0 else 0.5
        bb_distance_from_upper = abs(current_price - bb_upper) / (bb_upper - bb_lower) if (bb_upper - bb_lower) > 0 else 0.5
        
        if current_price < bb_lower:
            # Weight by how far below lower band
            if bb_distance_from_lower < 0.1:
                buy_strength += 2.0  # Very far below
                signal_details.append("BB<<Lower⭐")
            else:
                buy_strength += 1.0
                signal_details.append("BB<Lower")
        elif current_price > bb_upper:
            # Weight by how far above upper band
            if bb_distance_from_upper < 0.1:
                sell_strength += 2.0  # Very far above
                signal_details.append("BB>>Upper⭐")
            else:
                sell_strength += 1.0
                signal_details.append("BB>Upper")
        
        # 3. MACD Signal with confirmation
        last_macd_hist = self.symbol_states[symbol]["last_macd_histogram"]
        
        # Check for strong crossover (confirmed over 2 bars)
        if last_macd_hist < 0 and macd_hist > 0:
            if abs(macd_hist) > abs(last_macd_hist):
                buy_strength += 1.5  # Strong bullish crossover
                signal_details.append("MACD⬆⭐")
            else:
                buy_strength += 1.0
                signal_details.append("MACD⬆")
        elif last_macd_hist > 0 and macd_hist < 0:
            if abs(macd_hist) > abs(last_macd_hist):
                sell_strength += 1.5  # Strong bearish crossover
                signal_details.append("MACD⬇⭐")
            else:
                sell_strength += 1.0
                signal_details.append("MACD⬇")
        
        self.symbol_states[symbol]["last_macd_histogram"] = macd_hist
        
        # 4. Volume as multiplier (NEW approach!)
        volume_multiplier = 1.0
        if volume_ratio > StrategyConstants.VOLUME_MULTIPLIER:
            volume_multiplier = 1.3  # 30% boost
            signal_details.append(f"Vol{volume_ratio:.1f}x")
        
        # Apply volume multiplier
        buy_strength *= volume_multiplier
        sell_strength *= volume_multiplier
        
        # 5. Trend Filter with Multi-TF Confirmation (IMPROVED!)
        trend_aligned = False
        tf_alignment_score = 0.0
        
        if StrategyConstants.USE_TREND_WEIGHTING:
            # Get primary trend
            if is_uptrend and buy_strength > 0:
                buy_strength += 0.5  # Bonus for trend alignment
                trend_aligned = True
                signal_details.append("↗Trend1m")
            elif is_downtrend and sell_strength > 0:
                sell_strength += 0.5
                trend_aligned = True
                signal_details.append("↘Trend1m")
            else:
                # Counter-trend trade - reduce confidence
                buy_strength *= 0.7
                sell_strength *= 0.7
            
            # Multi-TF confirmation (3m and 5m)
            if StrategyConstants.CONFIRM_TIMEFRAME:
                trend_3m = self.get_trend_from_higher_tf(symbol, "3m")
                trend_5m = self.get_trend_from_higher_tf(symbol, "5m")
                
                # Score alignment
                if buy_strength > 0:  # Bullish signal
                    if trend_3m == "up":
                        tf_alignment_score += 0.5
                        signal_details.append("↗3m")
                    if trend_5m == "up":
                        tf_alignment_score += 0.5
                        signal_details.append("↗5m")
                    
                    # Apply alignment bonus
                    if tf_alignment_score >= StrategyConstants.MIN_TF_ALIGNMENT_SCORE:
                        buy_strength *= (1.0 + tf_alignment_score * 0.15)  # Up to 15% boost
                    else:
                        buy_strength *= 0.85  # Penalty for misalignment
                
                elif sell_strength > 0:  # Bearish signal
                    if trend_3m == "down":
                        tf_alignment_score += 0.5
                        signal_details.append("↘3m")
                    if trend_5m == "down":
                        tf_alignment_score += 0.5
                        signal_details.append("↘5m")
                    
                    # Apply alignment bonus
                    if tf_alignment_score >= StrategyConstants.MIN_TF_ALIGNMENT_SCORE:
                        sell_strength *= (1.0 + tf_alignment_score * 0.15)
                    else:
                        sell_strength *= 0.85
        
        elif StrategyConstants.TRADE_WITH_TREND_ONLY:
            # Legacy trend filter
            if is_uptrend and buy_strength > 0:
                buy_strength += 0.5
                trend_aligned = True
                signal_details.append("↗Trend")
            elif is_downtrend and sell_strength > 0:
                sell_strength += 0.5
                trend_aligned = True
                signal_details.append("↘Trend")
            else:
                buy_strength *= 0.7
                sell_strength *= 0.7
        
        # Count simple signals for backward compatibility
        buy_signals = 1 if buy_strength > 0 else 0
        sell_signals = 1 if sell_strength > 0 else 0
        
        # Update momentum for symbol rotation
        price_change_pct = ((current_price - close_prices[-20]) / close_prices[-20]) * 100 if len(close_prices) >= 20 else 0
        self.symbol_manager.update_momentum(symbol, {
            "price_change_pct": price_change_pct,
            "volume_ratio": volume_ratio,
            "atr": atr,
            "current_price": current_price
        })
        
        return {
            "buy_signals": buy_signals,
            "sell_signals": sell_signals,
            "buy_strength": buy_strength,  # NEW: weighted score
            "sell_strength": sell_strength,  # NEW: weighted score
            "signal_details": signal_details,
            "rsi": rsi,
            "bb_width": bb_width_percent,
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
    
    def check_filters(self, symbol: str, signals: Dict, data: Dict = None) -> tuple[bool, str]:
        """Check if trade passes all filters"""
        # 1. Trading hours (Hybrid Strategy: UTC 08:00-15:00)
        current_hour = datetime.now(UTC).hour
        if not (StrategyConstants.TRADING_START_HOUR <= current_hour < StrategyConstants.TRADING_END_HOUR):
            return False, f"Out of trading hours ({StrategyConstants.TRADING_START_HOUR}-{StrategyConstants.TRADING_END_HOUR} UTC)"
        
        # 2. Sideways market filter
        if signals["bb_width"] < Config.SIDEWAYS_THRESHOLD:
            return False, "Sideways market"
        
        # 3. Volume quality filter
        if data and Config.USE_VOLUME_QUALITY_FILTER:
            if not self.check_volume_quality(data["volume"]):
                return False, "Low volume quality"
        
        # 4. Sector diversification check (NEW - Hybrid Strategy)
        if self.risk_manager and Config.ENABLE_CORRELATION_FILTER:
            can_add, reason = self.risk_manager.check_sector_limits(symbol)
            if not can_add:
                return False, f"Sector limit: {reason}"
        
        # 5. Correlation risk check (NEW - Hybrid Strategy)
        if self.risk_manager and Config.ENABLE_CORRELATION_FILTER:
            can_add, reason = self.risk_manager.check_correlation_risk(symbol)
            if not can_add:
                return False, f"Correlation: {reason}"
        
        # 6. Position limits (adaptive)
        adaptive_max = self.get_adaptive_max_positions()
        self.position_manager.max_total_positions = adaptive_max
        
        if not self.position_manager.can_open_position(symbol):
            return False, "Position limit reached"
        
        # 7. Recovery mode check
        if self.recovery_mode and signals["buy_signals"] + signals["sell_signals"] < StrategyConstants.RECOVERY_CONFLUENCE_REQUIRED:
            return False, "Recovery mode: insufficient signals"
        
        # 8. Profit locked check
        if self.profit_locked and StrategyConstants.PROFIT_LOCK_MODE == "stop":
            return False, "Profit locked - trading paused"
        
        return True, "All filters passed"
    
    def calculate_position_size(self, symbol: str, stop_loss_percent: float, current_price: float) -> float:
        """Calculate position size based on risk with progressive recovery"""
        risk_amount = self.trade_history.current_balance * (Config.MAX_LOSS_PER_TRADE / 100)
        
        # Progressive recovery sizing (Kelly-based)
        if StrategyConstants.USE_PROGRESSIVE_RECOVERY:
            consecutive_losses = self.trade_history.get_consecutive_losses()
            recovery_multiplier = self.calculate_progressive_recovery_size(consecutive_losses)
            
            if recovery_multiplier > 1.0:
                risk_amount *= recovery_multiplier
                logger.info(f"🔄 Progressive recovery: {consecutive_losses} losses, size {recovery_multiplier:.2f}x")
        
        # Position size = Risk / Stop Loss Distance
        stop_loss_distance = current_price * (stop_loss_percent / 100)
        position_size = risk_amount / stop_loss_distance if stop_loss_distance > 0 else 0
        
        # Convert to quantity (in base currency)
        quantity = position_size / current_price if current_price > 0 else 0
        
        # Minimum quantity check
        min_qty = 0.001  # Adjust per symbol
        quantity = max(quantity, min_qty)
        
        return quantity
    
    def try_entry(self, symbol: str, signals: Dict, data: Dict):
        """Try to enter a position with weighted signal support and cost simulation"""
        # Check if trading is paused
        if hasattr(self, 'trading_paused') and self.trading_paused:
            return  # Skip entry if paused
        
        # Use weighted signals if enabled
        if StrategyConstants.USE_WEIGHTED_SIGNALS:
            buy_strength = signals.get("buy_strength", 0)
            sell_strength = signals.get("sell_strength", 0)
            
            # Check minimum strength threshold
            if buy_strength < Config.MIN_SIGNAL_STRENGTH and sell_strength < Config.MIN_SIGNAL_STRENGTH:
                return  # Not strong enough
            
            # Determine side
            if buy_strength >= Config.MIN_SIGNAL_STRENGTH and buy_strength > sell_strength:
                side = "BUY"
                signal_strength = buy_strength
            elif sell_strength >= Config.MIN_SIGNAL_STRENGTH and sell_strength > buy_strength:
                side = "SELL"
                signal_strength = sell_strength
            else:
                return
        else:
            # Legacy confluence counting
            buy_confluence = signals["buy_signals"]
            sell_confluence = signals["sell_signals"]
            
            required_confluence = StrategyConstants.RECOVERY_CONFLUENCE_REQUIRED if self.recovery_mode else Config.MIN_CONFLUENCE_SIGNALS
            
            if buy_confluence < required_confluence and sell_confluence < required_confluence:
                return  # Not enough signals
            
            # Determine side
            if buy_confluence >= required_confluence:
                side = "BUY"
                signal_strength = buy_confluence
            elif sell_confluence >= required_confluence:
                side = "SELL"
                signal_strength = sell_confluence
            else:
                return
        
        # Check filters (with volume quality check)
        passed, reason = self.check_filters(symbol, signals, data)
        if not passed:
            return
        
        # Calculate entry parameters
        current_price = signals["current_price"]
        
        # Simulate slippage (realistic cost)
        if StrategyConstants.SIMULATE_REAL_COSTS:
            if side == "BUY":
                current_price *= (1 + StrategyConstants.EXPECTED_SLIPPAGE / 100)  # Buy higher
            else:
                current_price *= (1 - StrategyConstants.EXPECTED_SLIPPAGE / 100)  # Sell lower
        
        # Calculate SL/TP using ATR-based dynamic stops (Hybrid Strategy)
        if StrategyConstants.USE_ATR_BASED_STOPS and self.adaptive_strategy:
            # Get ATR from data
            atr = signals.get("atr", 0)
            if atr > 0:
                # Use ATR-based calculation
                stops = self.adaptive_strategy.calculate_atr_based_stops(
                    current_price=current_price,
                    atr=atr,
                    side=side
                )
                stop_loss = stops["stop_loss"]
                take_profit = stops["take_profit"]
                stop_loss_percent = stops["sl_pct"]
                take_profit_percent = stops["tp_pct"]
                logger.info(f"🎯 ATR Dynamic: SL={stop_loss_percent:.2f}% TP={take_profit_percent:.2f}% (RR=1:{stops['risk_reward']:.2f})")
            else:
                # Fallback to fixed if ATR not available
                logger.warning(f"⚠️ ATR not available for {symbol}, using fixed stops")
                stop_loss_percent = Config.STOP_LOSS_PERCENT
                take_profit_percent = Config.TAKE_PROFIT_3_SIGNALS
                if side == "BUY":
                    stop_loss = current_price * (1 - stop_loss_percent / 100)
                    take_profit = current_price * (1 + take_profit_percent / 100)
                else:
                    stop_loss = current_price * (1 + stop_loss_percent / 100)
                    take_profit = current_price * (1 - take_profit_percent / 100)
        else:
            # Use fixed stops (old method)
            stop_loss_percent = Config.STOP_LOSS_PERCENT
            
            # Determine TP based on signal strength
            if StrategyConstants.USE_WEIGHTED_SIGNALS:
                # Strong signals get wider TP
                if signal_strength >= 6.0:
                    take_profit_percent = Config.TAKE_PROFIT_4_SIGNALS
                else:
                    take_profit_percent = Config.TAKE_PROFIT_3_SIGNALS
            else:
                if signal_strength == 4:
                    take_profit_percent = Config.TAKE_PROFIT_4_SIGNALS
                else:
                    take_profit_percent = Config.TAKE_PROFIT_3_SIGNALS
            
            # Recovery mode - AIM HIGHER!
            if self.recovery_mode:
                take_profit_percent = take_profit_percent * StrategyConstants.RECOVERY_TP_MULTIPLIER
                logger.info(f"🔴 Recovery TP: {take_profit_percent:.2f}%")
            
            # Calculate prices
            if side == "BUY":
                stop_loss = current_price * (1 - stop_loss_percent / 100)
                take_profit = current_price * (1 + take_profit_percent / 100)
            else:  # SELL
                stop_loss = current_price * (1 + stop_loss_percent / 100)
                take_profit = current_price * (1 - take_profit_percent / 100)
        
        # Calculate position size
        quantity = self.calculate_position_size(symbol, stop_loss_percent, current_price)
        
        # Simulate trading fees
        if StrategyConstants.SIMULATE_REAL_COSTS:
            position_value = current_price * quantity
            entry_fee = position_value * StrategyConstants.TAKER_FEE
            logger.debug(f"Entry fee: ${entry_fee:.4f}")
        
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
        
        # Add to position manager
        if self.position_manager.add_position(position):
            # Log entry with enhanced formatting
            strength_display = f"{signal_strength:.1f}" if StrategyConstants.USE_WEIGHTED_SIGNALS else f"{int(signal_strength)}/4"
            
            # Get intelligent system context
            context_parts = []
            if self.adaptive_strategy:
                regime = self.adaptive_strategy.current_regime.value[:3].upper()
                context_parts.append(f"Regime:{regime}")
            if self.event_manager:
                decision = self.event_manager.get_trading_decision()
                context_parts.append(f"Evt:{decision['status'][:4]}")
            context_str = " | ".join(context_parts) if context_parts else ""
            
            logger.info("="*80)
            logger.info(f"🟢 เปิดออเดอร์: {symbol} {side} @ ${current_price:.2f}")
            logger.info("-"*80)
            logger.info(f"🎯 เป้าหมาย: ${take_profit:.2f} (+{take_profit_percent:.2f}%) | Stop: ${stop_loss:.2f} (-{stop_loss_percent}%)")
            logger.info(f"📏 ขนาด: {quantity:.6f} | มูลค่า: ${current_price * quantity:.2f}")
            logger.info(f"💡 ความแข็งแรง: {strength_display} | สัญญาณ: {', '.join(signals['signal_details'][:2])}")
            if context_str:
                logger.info(f"🤖 Context: {context_str}")
            if self.recovery_mode:
                logger.info("🔴 โหมดกู้คืน - เป้าหมายสูงกว่าปกติ!")
            logger.info("="*80)
            
            # Telegram notification
            self.send_telegram(
                f"🟢 <b>ENTRY {symbol}</b>\n"
                f"Side: {side}\n"
                f"Price: ${current_price:.2f}\n"
                f"TP: ${take_profit:.2f} (+{take_profit_percent:.2f}%)\n"
                f"SL: ${stop_loss:.2f} (-{stop_loss_percent}%)\n"
                f"Strength: {strength_display} {', '.join(signals['signal_details'])}\n"
                f"{'\n🔴 RECOVERY MODE' if self.recovery_mode else ''}\n"
                f"{context_str}"
            )
            
            # Save state
            self.save_state()
    
    def check_exits(self):
        """Check all positions for exit conditions"""
        positions_to_close = []
        
        for position in self.position_manager.get_all_positions():
            symbol = position.symbol
            
            # Get current price
            data = self.get_market_data(symbol)
            if not data:
                continue
            
            current_price = data["current_price"]
            
            # Update trailing stop
            if Config.TRAILING_STOP_ENABLED:
                updated = self.trailing_stop_manager.update_trailing_stop(position, current_price)
                if updated:
                    logger.info(f"📈 {symbol} Trailing stop updated to ${position.stop_loss:.2f}")
            
            # Check exit conditions
            exit_reason = None
            
            # 0. Partial Take Profit (NEW!)
            if Config.PARTIAL_TP_ENABLED and not position.partial_tp_hit:
                profit_pct = 0
                if position.side == "BUY":
                    profit_pct = ((current_price - position.entry_price) / position.entry_price) * 100
                else:
                    profit_pct = ((position.entry_price - current_price) / position.entry_price) * 100
                
                if profit_pct >= StrategyConstants.PARTIAL_TP_PERCENT:
                    # Close partial position
                    old_qty = position.quantity
                    position.quantity = position.quantity * (1 - StrategyConstants.PARTIAL_TP_SIZE)
                    position.partial_tp_hit = True
                    
                    # Log partial profit
                    partial_profit = old_qty * StrategyConstants.PARTIAL_TP_SIZE * current_price * (profit_pct / 100)
                    logger.info(f"💰 {symbol} Partial TP! Closed 50% @+{profit_pct:.2f}% (${partial_profit:.2f})")
                    self.send_telegram(
                        f"💰 <b>PARTIAL TP {symbol}</b>\n"
                        f"Closed 50% @+{profit_pct:.2f}%\n"
                        f"Profit: ${partial_profit:.2f}\n"
                        f"Remaining qty: {position.quantity:.4f}"
                    )
            
            # 1. Take Profit
            if position.side == "BUY" and current_price >= position.take_profit:
                exit_reason = "TP"
            elif position.side == "SELL" and current_price <= position.take_profit:
                exit_reason = "TP"
            
            # 2. Stop Loss (including trailing)
            if exit_reason is None:
                if position.side == "BUY" and current_price <= position.stop_loss:
                    exit_reason = "SL" if not position.trailing_stop_active else "Trail_SL"
                elif position.side == "SELL" and current_price >= position.stop_loss:
                    exit_reason = "SL" if not position.trailing_stop_active else "Trail_SL"
            
            # 3. Time Stop
            if exit_reason is None:
                time_in_position = (datetime.now(UTC) - position.entry_time).total_seconds()
                # Use adaptive time stop based on signal strength
                time_stop = Config.TIME_STOP_STRONG_SIGNAL if position.confluence_score >= 4 else Config.TIME_STOP_BASE
                if time_in_position >= time_stop:
                    exit_reason = "Time"
            
            # Close position if exit triggered
            if exit_reason:
                positions_to_close.append((position, current_price, exit_reason))
        
        # Process exits
        for position, exit_price, exit_reason in positions_to_close:
            self.close_position(position, exit_price, exit_reason)
    
    def close_position(self, position: Position, exit_price: float, exit_reason: str):
        """Close a position"""
        # Set exit details
        position.exit_price = exit_price
        position.exit_time = datetime.now(UTC)
        position.exit_reason = exit_reason
        
        # Calculate P&L
        if position.side == "BUY":
            profit_pct = ((exit_price - position.entry_price) / position.entry_price) * 100
        else:
            profit_pct = ((position.entry_price - exit_price) / position.entry_price) * 100
        
        position.profit_percent = profit_pct
        
        # Calculate profit amount
        position_value = position.entry_price * position.quantity
        profit_amount = (profit_pct / 100) * position_value
        position.profit_amount = profit_amount
        
        # Remove from position manager
        self.position_manager.remove_position(position.position_id)
        
        # Add to trade history
        self.trade_history.add_trade(position)
        
        # Update intelligent systems
        if self.risk_manager:
            self.risk_manager.remove_position(
                position.symbol,
                exit_price,
                profit_amount,
                profit_pct > 0
            )
        
        if self.adaptive_strategy:
            self.adaptive_strategy.record_trade(
                position.symbol,
                position.entry_price,
                exit_price,
                profit_amount,
                profit_pct > 0,
                self.adaptive_strategy.current_regime,
                self.adaptive_strategy.current_params
            )
        
        # Calculate trade duration
        duration = int((position.exit_time - position.entry_time).total_seconds())
        
        # Get stats
        win_rate = self.trade_history.get_win_rate()
        daily_pnl = self.trade_history.get_daily_pnl_percent()
        
        # Enhanced exit log with box
        emoji = "✅" if profit_pct > 0 else "❌"
        color = "🟢" if profit_pct > 0 else "🔴"
        
        logger.info("="*80)
        logger.info(f"{color} ปิดออเดอร์: {position.symbol} {position.side} @ ${exit_price:.2f} {emoji}")
        logger.info("-"*80)
        logger.info(f"📊 กำไร-ขาดทุน: ${profit_amount:+.2f} ({profit_pct:+.2f}%) | ระยะเวลา: {duration}s")
        logger.info(f"💼 เข้า: ${position.entry_price:.2f} → ออก: ${exit_price:.2f}")
        logger.info(f"📝 สาเหตุ: {exit_reason[:60]}")
        logger.info("-"*80)
        logger.info(f"💰 ยอดคงเหลือ: ${self.trade_history.current_balance:.2f} | รายวัน: {daily_pnl:+.2f}% | Win Rate: {win_rate:.1f}%")
        logger.info("="*80)
        
        # Telegram notification
        self.send_telegram(
            f"{emoji} <b>EXIT {position.symbol}</b>\n"
            f"Side: {position.side}\n"
            f"Entry: ${position.entry_price:.2f}\n"
            f"Exit: ${exit_price:.2f}\n"
            f"P&L: {profit_pct:+.2f}% (${profit_amount:+.2f})\n"
            f"Reason: {exit_reason}\n"
            f"Balance: ${self.trade_history.current_balance:.2f}\n"
            f"Daily P&L: {self.trade_history.get_daily_pnl_percent():+.2f}%"
        )
        
        # Save state
        self.save_state()
        
        # Check daily limits
        self.check_daily_status()
    
    def check_daily_status(self):
        """Check daily profit/loss status"""
        daily_pnl = self.trade_history.get_daily_pnl_percent()
        
        # Check profit lock
        if not self.profit_locked and daily_pnl >= StrategyConstants.PROFIT_LOCK_THRESHOLD:
            self.profit_locked = True
            logger.info(f"🔒 PROFIT LOCKED at +{daily_pnl:.2f}% (Target: +{StrategyConstants.PROFIT_LOCK_THRESHOLD}%)")
            self.send_telegram(
                f"🔒 <b>PROFIT TARGET REACHED!</b>\n"
                f"Daily P&L: +{daily_pnl:.2f}%\n"
                f"Profit: ${self.trade_history.current_balance - self.trade_history.daily_start_balance:.2f}\n"
                f"Mode: {StrategyConstants.PROFIT_LOCK_MODE.upper()}"
            )
        
        # Check recovery mode entry
        if not self.recovery_mode and daily_pnl <= StrategyConstants.RECOVERY_MODE_TRIGGER:
            self.recovery_mode = True
            logger.warning(f"🔴 RECOVERY MODE ACTIVATED at {daily_pnl:.2f}%")
            self.send_telegram(
                f"🔴 <b>RECOVERY MODE</b>\n"
                f"Daily P&L: {daily_pnl:.2f}%\n"
                f"Conservative trading activated\n"
                f"Required signals: 4/4"
            )
        
        # Check recovery mode exit
        if self.recovery_mode and daily_pnl >= 0:
            self.recovery_mode = False
            logger.info("✅ Recovery mode deactivated (back to profit)")
        
        # Check daily loss limit
        if self.trade_history.should_stop_trading_today(Config.DAILY_LOSS_LIMIT):
            logger.error(f"🛑 DAILY LOSS LIMIT REACHED: {daily_pnl:.2f}%")
            self.send_telegram(
                f"🛑 <b>DAILY LOSS LIMIT</b>\n"
                f"P&L: {daily_pnl:.2f}%\n"
                f"Loss: ${self.trade_history.daily_start_balance - self.trade_history.current_balance:.2f}\n"
                f"Bot stopped for today."
            )
            self.running = False
    
    def check_intelligent_systems(self) -> bool:
        """
        Check all intelligent systems before trading
        Returns True if trading should proceed, False if should pause/reduce
        """
        # 1. Check Event Manager - Are there upcoming critical events?
        if self.event_manager and Config.ENABLE_EVENT_MANAGER:
            decision = self.event_manager.get_trading_decision()
            
            if decision["status"] == "EMERGENCY":
                # Close all positions before critical event
                logger.warning(f"🔴 {decision['reason']}")
                self._close_all_positions(decision['reason'])
                return False
                
            elif decision["status"] == "PAUSE":
                # Reduce positions and be cautious
                logger.warning(f"🟠 {decision['reason']}")
                # Mark to reduce new positions
                self.trading_paused = True
                return False
                
            elif decision["status"] == "CAUTION":
                logger.info(f"🟡 {decision['reason']}")
                # Continue but with caution (handled in position sizing)
        
        # 2. Check Risk Manager - Portfolio limits
        if self.risk_manager and Config.ENABLE_ADVANCED_RISK:
            # Update capital
            self.risk_manager.current_capital = self.trade_history.current_balance
            
            # Check if should pause
            should_pause, reason = self.risk_manager.should_pause_trading()
            if should_pause:
                logger.warning(f"🚫 Risk Manager: {reason}")
                return False
            
            # Check correlation risk for existing positions
            metrics = self.risk_manager.get_portfolio_metrics()
            if metrics.correlation_score > 0.75:
                logger.warning(f"⚠️ High portfolio correlation: {metrics.correlation_score:.2f}")
        
        # 3. Check Adaptive Strategy - Regime detection
        if self.adaptive_strategy and Config.ENABLE_REGIME_DETECTION:
            # Will be used in position sizing and parameter adjustment
            pass
        
        return True
    
    def _close_all_positions(self, reason: str):
        """Emergency close all positions"""
        positions = self.position_manager.get_all_positions()
        
        if not positions:
            return
        
        logger.warning(f"🚨 Closing {len(positions)} positions: {reason}")
        
        for position in positions:
            data = self.get_market_data(position.symbol)
            if data:
                self.close_position(position, data["current_price"], reason)
        
        if self.alert_manager:
            try:
                import asyncio
                asyncio.run(self.alert_manager.alert_risk_warning(
                    warning_type="EMERGENCY CLOSE",
                    severity=self.alert_manager.AlertSeverity.CRITICAL,
                    details=reason,
                    action=f"Closed all {len(positions)} positions"
                ))
            except:
                pass
    
    def run_cycle(self):
        """Run one trading cycle"""
        self.cycle_count += 1
        
        # ==================== INTELLIGENT PRE-CHECKS ====================
        # Check event manager, risk manager, etc. before trading
        if not self.check_intelligent_systems():
            logger.info("⏸️ Trading paused by intelligent systems")
            time.sleep(60)  # Wait 1 minute before next check
            return
        
        # Check if should rotate symbols
        if self.symbol_manager.should_rotate():
            current_positions = {
                symbol: self.position_manager.get_symbol_position_count(symbol)
                for symbol in Config.SYMBOL_POOL
            }
            new_active = self.symbol_manager.rotate_symbols(current_positions)
            logger.info(f"🔄 Symbol rotation: {', '.join(new_active[:5])}...")
        
        # Check exits first
        self.check_exits()
        
        # Scan active symbols for entries
        active_symbols = self.symbol_manager.get_active_symbols()
        
        for symbol in active_symbols:
            # Get market data
            data = self.get_market_data(symbol)
            if not data:
                continue
            
            # Calculate signals
            signals = self.calculate_signals(symbol, data)
            
            # Try entry (pass data for volume check)
            self.try_entry(symbol, signals, data)
        
        # ==================== CYCLE STATUS OUTPUT ====================
        self._display_cycle_status(active_symbols)
    
    def stop(self):
        """Stop the bot gracefully"""
        logger.info("🛑 Stopping bot...")
        self.running = False
    
    def run(self):
        """Main bot loop"""
        self.running = True
        logger.info("✅ Bot is running... Press Ctrl+C to stop\n")
        
        # Startup notification with intelligent features status
        feature_list = []
        if Config.ENABLE_EVENT_MANAGER:
            feature_list.append("📅 Events")
        if Config.ENABLE_ADVANCED_RISK:
            feature_list.append("⚡ Risk")
        if Config.ENABLE_ADAPTIVE_STRATEGY:
            feature_list.append("🎯 Adaptive")
        if Config.ENABLE_ENHANCED_ALERTS:
            feature_list.append("📢 Alerts")
        
        features_str = " | ".join(feature_list) if feature_list else "Basic Mode"
        
        self.send_telegram(
            f"🚀 <b>Intelligent Scalping Bot v3.0 Started</b>\n\n"
            f"💰 Capital: ${self.trade_history.daily_start_balance:.2f}\n"
            f"📊 Symbols: {len(Config.SYMBOL_POOL)} pool, {Config.MAX_ACTIVE_SYMBOLS} active\n"
            f"🎯 Target: +{Config.DAILY_PROFIT_TARGET}% to +{Config.DAILY_MAX_TARGET}%\n"
            f"💼 Mode: {'🧪 DEMO' if Config.DEMO_MODE else '⚠️ LIVE'}\n\n"
            f"🤖 <b>Features:</b> {features_str}\n\n"
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
    
    def stop(self):
        """Stop the bot gracefully"""
        logger.info("🛑 Stopping bot...")
        self.running = False
    
    def _display_cycle_status(self, active_symbols: List[str]):
        """Display comprehensive cycle status with intelligent system info"""
        # Gather data
        positions = self.position_manager.get_all_positions()
        pos_count = len(positions)
        daily_pnl = self.trade_history.get_daily_pnl_percent()
        daily_pnl_usd = self.trade_history.current_balance - self.trade_history.daily_start_balance
        balance = self.trade_history.current_balance
        win_rate = self.trade_history.get_win_rate()
        total_trades = len(self.trade_history.trades)
        
        # Performance emoji
        if daily_pnl > 5:
            perf_emoji = "🚀"
        elif daily_pnl > 2:
            perf_emoji = "📈"
        elif daily_pnl > 0:
            perf_emoji = "✅"
        elif daily_pnl > -1:
            perf_emoji = "⚠️"
        else:
            perf_emoji = "🔴"
        
        # Mode flags
        mode_flags = []
        if self.recovery_mode:
            mode_flags.append("🔴RECOVERY")
        if self.profit_locked:
            mode_flags.append("🔒LOCKED")
        if self.trading_paused:
            mode_flags.append("⏸️PAUSED")
        
        # Every 10 cycles: Full status
        if self.cycle_count % 10 == 0:
            logger.info("="*80)
            logger.info(f"📊 รอบที่ #{self.cycle_count} - สถานะ")
            logger.info("-"*80)
            
            # Portfolio
            logger.info(f"💰 ยอดเงิน: ${balance:.2f} | รายวัน: {perf_emoji} {daily_pnl:+.2f}% (${daily_pnl_usd:+.2f})")
            logger.info(f"📈 ผลงาน: {total_trades} เทรด | Win Rate: {win_rate:.1f}%")
            
            # Positions
            if positions:
                logger.info(f"📍 ออเดอร์เปิด: {pos_count}/{Config.MAX_TOTAL_POSITIONS}")
                for pos in positions:
                    # Get current price from market data
                    data = self.get_market_data(pos.symbol)
                    if not data:
                        continue
                    
                    current_price = data["current_price"]
                    pnl_pct = ((current_price - pos.entry_price) / pos.entry_price) * 100
                    if pos.side == "BUY":
                        pnl_pct = pnl_pct
                    else:
                        pnl_pct = -pnl_pct
                    
                    time_held = int((datetime.now(UTC) - pos.entry_time).total_seconds())
                    status_emoji = "🟢" if pnl_pct > 0 else "🔴"
                    
                    logger.info(f"  {status_emoji} {pos.symbol}: {pos.side} @ ${pos.entry_price:.2f} | "
                               f"P&L: {pnl_pct:+.2f}% | เวลา: {time_held}s")
            else:
                logger.info(f"📍 ออเดอร์เปิด: 0/{Config.MAX_TOTAL_POSITIONS} (กำลัง Scan...)")
            
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
                    logger.info(f"   TP: {self.adaptive_strategy.current_params.take_profit_pct:.2%} | "
                               f"SL: {self.adaptive_strategy.current_params.stop_loss_pct:.2%}")
            
            # Mode flags
            if mode_flags:
                logger.info("-"*80)
                logger.info(f"🚨 โหมดพิเศษ: {' | '.join(mode_flags)}")
            
            logger.info("="*80)
        
        # Every cycle: Compact one-liner
        else:
            # Event status
            evt_status = "✅"
            if self.event_manager:
                decision = self.event_manager.get_trading_decision()
                evt_status = {
                    "CLEAR": "✅",
                    "CAUTION": "🟡",
                    "PAUSE": "🟠",
                    "EMERGENCY": "🔴"
                }.get(decision["status"], "❓")
            
            # Regime icon
            regime_icon = "❓"
            if self.adaptive_strategy:
                regime_icon = {
                    "bull": "🚀",
                    "bear": "🐻",
                    "ranging": "↔️",
                    "volatile": "⚡",
                    "breakout": "📈",
                    "unknown": "❓"
                }.get(self.adaptive_strategy.current_regime.value, "❓")
            
            # Special warnings
            warnings = []
            if self.risk_manager:
                metrics = self.risk_manager.get_portfolio_metrics()
                if metrics.correlation_score > 0.7:
                    warnings.append(f"⚠️Corr")
            if mode_flags:
                warnings.extend(mode_flags)
            
            # Build clean status line
            warning_str = f" {' '.join(warnings)}" if warnings else ""
            logger.info(
                f"รอบ #{self.cycle_count:04d} │ "
                f"{perf_emoji}${balance:.2f} ({daily_pnl:+.1f}%) │ "
                f"ออเดอร์: {pos_count}/{Config.MAX_TOTAL_POSITIONS} │ "
                f"WR: {win_rate:.0f}% │ "
                f"Event: {evt_status} │ "
                f"ตลาด: {regime_icon}"
                f"{warning_str}"
            )
    
    def shutdown(self):
        """Cleanup and final reporting"""
        end_time = datetime.now()
        runtime = end_time - self.start_time
        hours = runtime.total_seconds() / 3600
        
        logger.info("="*60)
        logger.info("🛑 ปิด BOT - กำลังปิดออเดอร์...")
        logger.info("="*60)
        logger.info(f"⏰ เวลาเริ่มต้น: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"⏰ เวลาสิ้นสุด: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"⏱️  รวมเวลารัน: {int(hours)}ชม {int((hours % 1) * 60)}นาที ({runtime.total_seconds():.0f}วิ)")
        logger.info("="*60)
        
        # Stop telegram handler
        if hasattr(self, 'telegram_handler'):
            self.telegram_handler.running = False
        
        # Close any remaining positions (IMPORTANT!)
        open_positions = self.position_manager.get_all_positions()
        if open_positions:
            logger.warning(f"⚠️ กำลังปิด {len(open_positions)} ออเดอร์...")
            for position in open_positions:
                data = self.get_market_data(position.symbol)
                if data:
                    self.close_position(position, data["current_price"], "🛑 ปิด Bot")
                    logger.info(f"✅ ปิด {position.symbol} ที่ ${data['current_price']:.2f}")
            time.sleep(1)  # Wait for orders to process
        else:
            logger.info("✅ ไม่มีออเดอร์ที่ต้องปิด")
        
        logger.info("="*60)
        logger.info("📊 สรุปรายวัน")
        logger.info("="*60)
        
        # Statistics
        total_trades = len(self.trade_history.trades)
        win_rate = self.trade_history.get_win_rate()
        daily_pnl = self.trade_history.get_daily_pnl_percent()
        profit_amount = self.trade_history.current_balance - self.trade_history.daily_start_balance
        
        logger.info(f"จำนวนเทรด: {total_trades}")
        logger.info(f"Win Rate: {win_rate:.1f}%")
        logger.info(f"กำไร-ขาดทุนรายวัน: {daily_pnl:+.2f}% (${profit_amount:+.2f})")
        logger.info(f"ยอดเงินสุดท้าย: ${self.trade_history.current_balance:.2f}")
        
        # Per-symbol stats
        if self.trade_history.symbol_stats:
            logger.info("\nTop Symbols:")
            for symbol, stats in sorted(
                self.trade_history.symbol_stats.items(),
                key=lambda x: x[1]["pnl"],
                reverse=True
            )[:5]:
                logger.info(f"  {symbol}: {stats['pnl']:+.2f}% ({stats['wins']}W/{stats['losses']}L)")
        
        logger.info("="*60)
        
        # Final telegram report
        runtime = end_time - self.start_time
        hours = runtime.total_seconds() / 3600
        self.send_telegram(
            f"🛑 <b>ปิด BOT</b>\n\n"
            f"⏰ เริ่ม: {self.start_time.strftime('%H:%M:%S')}\n"
            f"⏰ สิ้นสุด: {end_time.strftime('%H:%M:%S')}\n"
            f"⏱️ รวม: {int(hours)}ชม {int((hours % 1) * 60)}นท\n\n"
            f"จำนวนเทรด: {total_trades}\n"
            f"Win Rate: {win_rate:.1f}%\n"
            f"กำไรรายวัน: {daily_pnl:+.2f}%\n"
            f"กำไร: ${profit_amount:+.2f}\n"
            f"ยอดสุดท้าย: ${self.trade_history.current_balance:.2f}\n"
            f"ออเดอร์เปิด: {len(open_positions)} (ปิดหมดแล้ว)\n\n"
            f"เป้าหมาย: {'✅ ถึงแล้ว' if daily_pnl >= Config.DAILY_PROFIT_TARGET else '❌ ไม่ถึง'}"
        )
        
        # Save final state
        self.save_state()
        logger.info("💾 บันทึกสถานะสำเร็จ")
        logger.info("✅ ปิด Bot สำเร็จ - ปิดออเดอร์ทั้งหมดปลอดภัย")


# ===================== ENTRY POINT =====================
if __name__ == "__main__":
    bot = DailyScalpingBot()
    bot.run()

