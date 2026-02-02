"""
🎯 Adaptive Strategy Engine
Learns from performance and adjusts strategy parameters dynamically
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta, UTC
from collections import deque


logger = logging.getLogger(__name__)


class MarketRegime(Enum):
    """Market regime types"""
    BULL = "bull"           # Strong uptrend
    BEAR = "bear"           # Strong downtrend
    RANGING = "ranging"     # Sideways movement
    VOLATILE = "volatile"   # High volatility
    BREAKOUT = "breakout"   # Breaking key levels
    UNKNOWN = "unknown"


class StrategyMode(Enum):
    """Strategy operating modes"""
    AGGRESSIVE = "aggressive"     # Bull market
    DEFENSIVE = "defensive"       # Bear market
    SCALPING = "scalping"        # Ranging market
    MOMENTUM = "momentum"         # Breakout
    SAFE = "safe"                # High volatility


@dataclass
class StrategyParameters:
    """Trading strategy parameters"""
    # Entry thresholds
    min_signal_strength: float
    min_confluence: int
    
    # Risk/Reward
    take_profit_pct: float
    stop_loss_pct: float
    
    # Position sizing
    position_size_multiplier: float
    leverage_multiplier: float
    
    # Timeouts
    max_hold_time: int  # seconds
    
    # Filters
    min_volume_ratio: float
    max_bb_width: float
    
    # Mode
    mode: StrategyMode
    
    def __str__(self):
        return (f"Mode: {self.mode.value}, "
               f"Signals: {self.min_signal_strength:.1f}, "
               f"TP: {self.take_profit_pct:.2%}, "
               f"SL: {self.stop_loss_pct:.2%}")


class AdaptiveStrategyEngine:
    """
    Adaptive Strategy Engine
    
    Features:
    - Market regime detection (bull/bear/range/volatile)
    - Dynamic parameter adjustment based on performance
    - Strategy mode switching
    - Win rate tracking and learning
    - Time-of-day optimization
    - Performance-based tuning
    """
    
    def __init__(self):
        # Current regime and parameters
        self.current_regime = MarketRegime.UNKNOWN
        self.current_params = self._get_default_params()
        
        # Performance tracking
        self.recent_trades: deque = deque(maxlen=50)  # Last 50 trades
        self.regime_history: deque = deque(maxlen=100)
        
        # Parameter history (for learning)
        self.parameter_history: List[Dict] = []
        
        # Regime-specific stats
        self.regime_stats: Dict[MarketRegime, Dict] = {
            regime: {"wins": 0, "losses": 0, "total_pnl": 0.0}
            for regime in MarketRegime
        }
        
        # Time-of-day performance
        self.hourly_stats: Dict[int, Dict] = {
            hour: {"wins": 0, "losses": 0, "avg_pnl": 0.0}
            for hour in range(24)
        }
        
        # Indicator performance weights
        self.indicator_weights = {
            "rsi": 0.25,
            "bb": 0.25,
            "macd": 0.30,
            "volume": 0.20
        }
    
    # ==================== REGIME DETECTION ====================
    
    def detect_regime(self, symbol: str, prices: List[float], 
                     volumes: List[float], atr: float) -> MarketRegime:
        """
        Detect current market regime
        
        Args:
            symbol: Trading symbol
            prices: Recent price history (100+ candles)
            volumes: Recent volume history
            atr: Current ATR value
            
        Returns:
            Detected MarketRegime
        """
        if len(prices) < 50:
            return MarketRegime.UNKNOWN
        
        # Calculate metrics
        returns = np.diff(prices) / prices[:-1]
        
        # Trend strength (30-day return)
        if len(prices) >= 30:
            month_return = (prices[-1] - prices[-30]) / prices[-30]
        else:
            month_return = (prices[-1] - prices[0]) / prices[0]
        
        # Volatility (rolling std)
        vol = np.std(returns[-20:]) if len(returns) >= 20 else np.std(returns)
        
        # ATR relative to price
        atr_pct = atr / prices[-1]
        
        # Volume trend
        avg_vol = np.mean(volumes) if len(volumes) > 0 else 1
        recent_vol = np.mean(volumes[-10:]) if len(volumes) >= 10 else avg_vol
        vol_ratio = recent_vol / avg_vol if avg_vol > 0 else 1
        
        # Decision logic
        logger.info(f"📊 Regime Detection for {symbol}:")
        logger.info(f"  Month Return: {month_return:+.2%}")
        logger.info(f"  Volatility: {vol:.4f}")
        logger.info(f"  ATR %: {atr_pct:.4f}")
        logger.info(f"  Volume Ratio: {vol_ratio:.2f}")
        
        # Extreme volatility check first
        if atr_pct > 0.008 or vol > 0.03:  # >0.8% ATR or >3% volatility
            regime = MarketRegime.VOLATILE
            logger.info(f"  → Regime: VOLATILE ⚡")
            
        # Bull market
        elif month_return > 0.30:  # +30% in 30 days
            regime = MarketRegime.BULL
            logger.info(f"  → Regime: BULL 🚀")
            
        # Bear market
        elif month_return < -0.30:  # -30% in 30 days
            regime = MarketRegime.BEAR
            logger.info(f"  → Regime: BEAR 🐻")
            
        # Ranging market (low volatility, low return)
        elif abs(month_return) < 0.10 and vol < 0.015:
            regime = MarketRegime.RANGING
            logger.info(f"  → Regime: RANGING ↔️")
            
        # Breakout (high volume, moderate movement)
        elif vol_ratio > 1.5 and 0.10 < abs(month_return) < 0.30:
            regime = MarketRegime.BREAKOUT
            logger.info(f"  → Regime: BREAKOUT 📈")
            
        else:
            regime = MarketRegime.UNKNOWN
            logger.info(f"  → Regime: UNKNOWN ❓")
        
        # Update tracking
        self.current_regime = regime
        self.regime_history.append({
            "regime": regime,
            "timestamp": datetime.now(UTC),
            "month_return": month_return,
            "volatility": vol
        })
        
        return regime
    
    # ==================== PARAMETER ADAPTATION ====================
    
    def get_strategy_parameters(self, regime: Optional[MarketRegime] = None,
                               win_rate: Optional[float] = None) -> StrategyParameters:
        """
        Get optimal strategy parameters for current conditions
        
        Args:
            regime: Market regime (uses current if None)
            win_rate: Recent win rate (calculates if None)
            
        Returns:
            StrategyParameters optimized for conditions
        """
        if regime is None:
            regime = self.current_regime
        
        if win_rate is None:
            win_rate = self._calculate_win_rate()
        
        # Base parameters by regime
        if regime == MarketRegime.BULL:
            params = StrategyParameters(
                min_signal_strength=3.5,    # Lower threshold (more trades)
                min_confluence=3,
                take_profit_pct=0.008,      # Higher TP (0.8%)
                stop_loss_pct=0.003,        # Wider SL (0.3%)
                position_size_multiplier=1.3,  # Larger positions
                leverage_multiplier=1.0,    # 3x leverage
                max_hold_time=300,          # Longer holds
                min_volume_ratio=0.7,       # Relaxed volume
                max_bb_width=0.006,         # Allow wider BB
                mode=StrategyMode.AGGRESSIVE
            )
            
        elif regime == MarketRegime.BEAR:
            params = StrategyParameters(
                min_signal_strength=4.2,    # Higher threshold (fewer trades)
                min_confluence=4,
                take_profit_pct=0.003,      # Quick TP (0.3%)
                stop_loss_pct=0.0015,       # Tight SL (0.15%)
                position_size_multiplier=0.5,  # Smaller positions
                leverage_multiplier=0.5,    # 1.5x leverage
                max_hold_time=120,          # Quick exits
                min_volume_ratio=0.9,       # Strict volume
                max_bb_width=0.003,         # Tight BB only
                mode=StrategyMode.DEFENSIVE
            )
            
        elif regime == MarketRegime.RANGING:
            params = StrategyParameters(
                min_signal_strength=3.8,
                min_confluence=3,
                take_profit_pct=0.005,      # Medium TP (0.5%)
                stop_loss_pct=0.002,        # Medium SL (0.2%)
                position_size_multiplier=1.0,
                leverage_multiplier=1.0,    # 3x leverage
                max_hold_time=240,
                min_volume_ratio=0.8,
                max_bb_width=0.004,
                mode=StrategyMode.SCALPING
            )
            
        elif regime == MarketRegime.VOLATILE:
            params = StrategyParameters(
                min_signal_strength=4.5,    # Very high threshold
                min_confluence=4,
                take_profit_pct=0.004,      # Quick TP
                stop_loss_pct=0.0015,       # Very tight SL
                position_size_multiplier=0.4,  # Very small
                leverage_multiplier=0.33,   # 1x leverage
                max_hold_time=90,           # Very quick
                min_volume_ratio=1.0,       # High volume only
                max_bb_width=0.003,
                mode=StrategyMode.SAFE
            )
            
        elif regime == MarketRegime.BREAKOUT:
            params = StrategyParameters(
                min_signal_strength=4.0,
                min_confluence=3,
                take_profit_pct=0.007,      # Larger TP
                stop_loss_pct=0.0025,       # Medium SL
                position_size_multiplier=1.2,
                leverage_multiplier=1.0,
                max_hold_time=300,
                min_volume_ratio=1.2,       # High volume
                max_bb_width=0.005,
                mode=StrategyMode.MOMENTUM
            )
            
        else:  # UNKNOWN
            params = self._get_default_params()
        
        # Adjust based on recent performance
        params = self._adjust_for_performance(params, win_rate)
        
        # Adjust for time of day
        params = self._adjust_for_time_of_day(params)
        
        # Store as current
        self.current_params = params
        
        logger.info(f"🎯 Strategy: {params}")
        
        return params
    
    def _get_default_params(self) -> StrategyParameters:
        """Get default conservative parameters"""
        return StrategyParameters(
            min_signal_strength=3.8,
            min_confluence=3,
            take_profit_pct=0.006,
            stop_loss_pct=0.0035,
            position_size_multiplier=1.0,
            leverage_multiplier=1.0,
            max_hold_time=240,
            min_volume_ratio=0.8,
            max_bb_width=0.004,
            mode=StrategyMode.SCALPING
        )
    
    def _adjust_for_performance(self, params: StrategyParameters, 
                               win_rate: float) -> StrategyParameters:
        """
        Adjust parameters based on recent performance
        
        High win rate → Be more aggressive
        Low win rate → Be more defensive
        """
        if win_rate > 0.65:  # >65% win rate - performing well
            params.min_signal_strength *= 0.95  # Lower threshold
            params.take_profit_pct *= 1.1       # Higher TP
            params.position_size_multiplier *= 1.1
            logger.info(f"  ✅ High win rate ({win_rate:.1%}) - More aggressive")
            
        elif win_rate < 0.50:  # <50% win rate - struggling
            params.min_signal_strength *= 1.1   # Higher threshold
            params.stop_loss_pct *= 0.8         # Tighter SL
            params.take_profit_pct *= 0.9       # Lower TP
            params.position_size_multiplier *= 0.7
            logger.info(f"  ⚠️ Low win rate ({win_rate:.1%}) - More defensive")
        
        return params
    
    def _adjust_for_time_of_day(self, params: StrategyParameters) -> StrategyParameters:
        """
        Adjust parameters based on time of day
        
        High liquidity hours → Normal/Aggressive
        Low liquidity hours → Defensive
        """
        current_hour = datetime.now(UTC).hour
        
        # Low volume hours (02:00-06:00 UTC)
        if 2 <= current_hour < 6:
            params.position_size_multiplier *= 0.5
            params.min_volume_ratio = max(params.min_volume_ratio, 1.0)
            logger.info(f"  🌙 Low liquidity hour ({current_hour}:00 UTC) - Reduced size")
            
        # Best hours (13:00-17:00 UTC - London/NY overlap)
        elif 13 <= current_hour < 17:
            params.position_size_multiplier *= 1.2
            logger.info(f"  ☀️ Peak liquidity hour ({current_hour}:00 UTC) - Increased size")
        
        return params
    
    # ==================== LEARNING & TRACKING ====================
    
    def record_trade(self, symbol: str, entry_price: float, exit_price: float,
                    pnl: float, is_win: bool, regime: MarketRegime,
                    parameters_used: StrategyParameters):
        """
        Record trade result for learning
        
        This is how the bot learns what works and what doesn't
        """
        trade_record = {
            "symbol": symbol,
            "timestamp": datetime.now(UTC),
            "entry": entry_price,
            "exit": exit_price,
            "pnl": pnl,
            "is_win": is_win,
            "regime": regime,
            "mode": parameters_used.mode,
            "params": parameters_used,
            "hour": datetime.now(UTC).hour
        }
        
        self.recent_trades.append(trade_record)
        
        # Update regime stats
        if regime in self.regime_stats:
            self.regime_stats[regime]["wins" if is_win else "losses"] += 1
            self.regime_stats[regime]["total_pnl"] += pnl
        
        # Update hourly stats
        hour = datetime.now(UTC).hour
        if hour in self.hourly_stats:
            self.hourly_stats[hour]["wins" if is_win else "losses"] += 1
            # Running average
            count = self.hourly_stats[hour]["wins"] + self.hourly_stats[hour]["losses"]
            old_avg = self.hourly_stats[hour]["avg_pnl"]
            self.hourly_stats[hour]["avg_pnl"] = (old_avg * (count - 1) + pnl) / count
        
        logger.info(f"📝 Trade recorded: {symbol} {'+' if is_win else '-'} "
                   f"${pnl:.2f} in {regime.value} market")
    
    def _calculate_win_rate(self, last_n: int = 50) -> float:
        """Calculate win rate from recent trades"""
        if not self.recent_trades:
            return 0.55  # Default assumption
        
        recent = list(self.recent_trades)[-last_n:]
        wins = sum(1 for t in recent if t["is_win"])
        
        return wins / len(recent) if recent else 0.55
    
    def get_regime_performance(self) -> Dict[MarketRegime, Dict]:
        """Get performance stats by regime"""
        performance = {}
        
        for regime, stats in self.regime_stats.items():
            total = stats["wins"] + stats["losses"]
            if total > 0:
                win_rate = stats["wins"] / total
                avg_pnl = stats["total_pnl"] / total
                
                performance[regime] = {
                    "win_rate": win_rate,
                    "total_trades": total,
                    "avg_pnl": avg_pnl,
                    "total_pnl": stats["total_pnl"]
                }
        
        return performance
    
    def get_best_trading_hours(self, top_n: int = 5) -> List[Tuple[int, float]]:
        """Get hours with best average P&L"""
        hours_with_pnl = [
            (hour, stats["avg_pnl"])
            for hour, stats in self.hourly_stats.items()
            if stats["wins"] + stats["losses"] > 0
        ]
        
        hours_with_pnl.sort(key=lambda x: x[1], reverse=True)
        
        return hours_with_pnl[:top_n]
    
    # ==================== INDICATOR WEIGHTING ====================
    
    def calculate_atr_based_stops(self, current_price: float, atr: float, 
                                  side: str = "BUY") -> Dict[str, float]:
        """
        Calculate dynamic SL/TP based on ATR (Average True Range)
        
        Args:
            current_price: Current market price
            atr: Current ATR value
            side: "BUY" or "SELL"
            
        Returns:
            Dict with 'stop_loss', 'take_profit', 'sl_pct', 'tp_pct'
        """
        from config.strategy_constants import StrategyConstants
        
        # Get ATR multipliers from constants
        sl_multiplier = StrategyConstants.ATR_SL_MULTIPLIER  # 1.5x
        tp_multiplier = StrategyConstants.ATR_TP_MULTIPLIER  # 3.5x
        
        # Calculate SL/TP distances
        sl_distance = atr * sl_multiplier
        tp_distance = atr * tp_multiplier
        
        # Convert to percentage
        sl_pct = (sl_distance / current_price) * 100
        tp_pct = (tp_distance / current_price) * 100
        
        # Apply minimum/maximum bounds for safety
        # Min: 0.2% (avoid too tight), Max: 1.5% (avoid too wide)
        sl_pct = max(0.2, min(sl_pct, 1.5))
        tp_pct = max(0.4, min(tp_pct, 3.0))
        
        # Calculate actual prices
        if side == "BUY":
            stop_loss = current_price * (1 - sl_pct / 100)
            take_profit = current_price * (1 + tp_pct / 100)
        else:  # SELL
            stop_loss = current_price * (1 + sl_pct / 100)
            take_profit = current_price * (1 - tp_pct / 100)
        
        logger.info(f"📐 ATR-based stops: ATR={atr:.4f} "
                   f"SL={sl_pct:.2f}% TP={tp_pct:.2f}% (RR=1:{tp_pct/sl_pct:.2f})")
        
        return {
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "sl_pct": sl_pct,
            "tp_pct": tp_pct,
            "atr": atr,
            "risk_reward": tp_pct / sl_pct if sl_pct > 0 else 0
        }
    
    def update_indicator_weights(self):
        """
        Learn which indicators perform best
        
        This recalculates weights based on historical accuracy
        """
        if len(self.recent_trades) < 20:
            return  # Need more data
        
        # TODO: Track which indicators fired for each trade
        # For now, keep static weights
        # In future: implement indicator attribution tracking
        
        logger.info(f"📊 Current indicator weights: {self.indicator_weights}")
    
    def get_weighted_signal_score(self, rsi_signal: float, bb_signal: float,
                                  macd_signal: float, volume_signal: float) -> float:
        """
        Calculate weighted signal score
        
        Uses learned weights to emphasize best indicators
        """
        score = (
            rsi_signal * self.indicator_weights["rsi"] +
            bb_signal * self.indicator_weights["bb"] +
            macd_signal * self.indicator_weights["macd"] +
            volume_signal * self.indicator_weights["volume"]
        ) * 4  # Scale to match old system
        
        return score
    
    # ==================== REPORTING ====================
    
    def get_strategy_report(self) -> str:
        """Generate strategy status report"""
        report = ["=" * 50]
        report.append("🎯 ADAPTIVE STRATEGY STATUS")
        report.append("=" * 50)
        
        # Current regime
        report.append(f"\n📊 Market Regime: {self.current_regime.value.upper()}")
        report.append(f"🎮 Strategy Mode: {self.current_params.mode.value.upper()}")
        
        # Current parameters
        report.append(f"\n⚙️ Parameters:")
        report.append(f"  Signal Threshold: {self.current_params.min_signal_strength:.1f}")
        report.append(f"  TP: {self.current_params.take_profit_pct:.2%} | "
                     f"SL: {self.current_params.stop_loss_pct:.2%}")
        report.append(f"  Position Size: {self.current_params.position_size_multiplier:.0%}")
        report.append(f"  Leverage: {self.current_params.leverage_multiplier:.0%}")
        
        # Recent performance
        win_rate = self._calculate_win_rate()
        report.append(f"\n📈 Recent Performance:")
        report.append(f"  Win Rate (50 trades): {win_rate:.1%}")
        
        if self.recent_trades:
            recent_pnl = sum(t["pnl"] for t in self.recent_trades)
            report.append(f"  Recent P&L: ${recent_pnl:+.2f}")
        
        # Regime performance
        report.append(f"\n🏆 Performance by Regime:")
        regime_perf = self.get_regime_performance()
        for regime, stats in regime_perf.items():
            report.append(f"  {regime.value.upper()}: "
                         f"{stats['win_rate']:.1%} WR, "
                         f"${stats['avg_pnl']:+.2f} avg")
        
        # Best hours
        best_hours = self.get_best_trading_hours(3)
        if best_hours:
            report.append(f"\n⏰ Best Trading Hours (UTC):")
            for hour, avg_pnl in best_hours:
                report.append(f"  {hour:02d}:00 - ${avg_pnl:+.2f} avg")
        
        report.append("=" * 50)
        
        return "\n".join(report)
