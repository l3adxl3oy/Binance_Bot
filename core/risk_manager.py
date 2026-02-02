"""
⚡ Advanced Risk Management Engine
Protects capital with intelligent position sizing, correlation tracking, and dynamic adjustments
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta, UTC
from collections import deque


logger = logging.getLogger(__name__)


@dataclass
class PortfolioMetrics:
    """Current portfolio risk metrics"""
    total_exposure: float  # % of capital in positions
    position_count: int
    largest_position: float
    correlation_score: float  # 0-1, higher = more correlated
    volatility_regime: str  # "low", "medium", "high", "extreme"
    current_drawdown: float  # Current % drawdown from peak
    daily_var: float  # Value at Risk (95% confidence)


class RiskManager:
    """
    Advanced Risk Management System
    
    Features:
    - Dynamic position sizing (Kelly Criterion)
    - Correlation matrix tracking
    - Volatility-based adjustments
    - Liquidation protection
    - Drawdown management
    - Portfolio heat monitoring
    - Consecutive loss protection
    - Sector-based diversification (NEW!)
    """
    
    # Sector grouping for crypto assets
    SECTOR_GROUPS = {
        "blue_chip": ["BTCUSDT", "ETHUSDT"],  # Large cap, high liquidity
        "exchange_tokens": ["BNBUSDT"],  # Exchange tokens
        "layer1": ["SOLUSDT", "ADAUSDT", "DOTUSDT", "AVAXUSDT", "ATOMUSDT", "APTUSDT"],  # Layer 1 blockchains
        "defi": ["LINKUSDT", "FILUSDT", "ICPUSDT"],  # DeFi tokens
        "altcoins": ["XRPUSDT", "DOGEUSDT", "TRXUSDT", "LTCUSDT", "ETCUSDT", "XLMUSDT"]  # Other altcoins
    }
    
    # Maximum positions per sector (diversification)
    MAX_POSITIONS_PER_SECTOR = 2
    
    def __init__(self, initial_capital: float):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.peak_capital = initial_capital
        
        # Risk parameters
        self.max_risk_per_trade = 0.006  # 0.6% base
        self.max_portfolio_heat = 0.15  # 15% max total exposure
        self.max_correlation = 0.7  # Max avg correlation allowed
        self.max_daily_loss = 0.025  # 2.5% daily loss limit
        self.max_monthly_loss = 0.10  # 10% monthly loss limit
        
        # Tracking
        self.positions: Dict[str, Dict] = {}  # symbol -> position info
        self.price_history: Dict[str, deque] = {}  # For correlation calc
        self.trade_history: List[Dict] = []
        self.consecutive_losses = 0
        self.consecutive_wins = 0
        
        # Performance tracking
        self.daily_start_capital = initial_capital
        self.monthly_start_capital = initial_capital
        self.last_reset_day = datetime.now(UTC).day
        self.last_reset_month = datetime.now(UTC).month
        
        # Volatility regime
        self.current_atr: Dict[str, float] = {}
        self.atr_history: Dict[str, deque] = {}
        
    # ==================== POSITION SIZING ====================
    
    def calculate_position_size(self, symbol: str, entry_price: float, 
                               stop_loss_pct: float, win_rate: float = 0.55,
                               confidence: float = 1.0) -> Tuple[float, Dict]:
        """
        Calculate optimal position size using Kelly Criterion with adjustments
        
        Args:
            symbol: Trading pair
            entry_price: Entry price
            stop_loss_pct: Stop loss percentage (e.g., 0.0035 for 0.35%)
            win_rate: Historical win rate (0-1)
            confidence: Signal confidence (0-1)
            
        Returns:
            (position_size_in_base_currency, details_dict)
        """
        # Base risk amount
        base_risk = self.current_capital * self.max_risk_per_trade
        
        # Kelly Criterion: f = (p*b - q) / b
        # where p = win rate, q = 1-p, b = win/loss ratio
        # For simplicity, assume avg win = 0.6%, avg loss = 0.35%
        avg_win = 0.006
        avg_loss = stop_loss_pct
        win_loss_ratio = avg_win / avg_loss if avg_loss > 0 else 1.7
        
        kelly_fraction = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio
        kelly_fraction = max(0, min(kelly_fraction, 0.25))  # Cap at 25%
        
        # Use fractional Kelly (0.25x) for safety
        kelly_size = self.current_capital * kelly_fraction * 0.25
        
        # Start with base risk, adjust with Kelly
        position_value = base_risk
        if kelly_size > base_risk:
            # Kelly suggests larger size - scale up cautiously
            position_value = base_risk * (1 + min(kelly_fraction, 0.5))
        
        # Apply confidence multiplier
        position_value *= confidence
        
        # Check portfolio constraints
        portfolio_metrics = self.get_portfolio_metrics()
        
        # Adjust for current exposure (เข้มงวดขึ้นเพราะเทรดบ่อยขึ้น)
        if portfolio_metrics.total_exposure > 0.12:  # Over 12% exposure
            position_value *= 0.6  # Reduce new positions more aggressively
        elif portfolio_metrics.total_exposure > 0.08:  # Over 8%
            position_value *= 0.8  # Reduce moderately
        
        # Adjust for correlation (เข้มงวดขึ้นเพราะมี positions มากขึ้น)
        if portfolio_metrics.correlation_score > 0.6:
            position_value *= 0.4  # High correlation - reduce drastically
        elif portfolio_metrics.correlation_score > 0.5:
            position_value *= 0.7  # Moderate correlation - reduce
        
        # Adjust for volatility regime
        vol_multiplier = self._get_volatility_multiplier(symbol)
        position_value *= vol_multiplier
        
        # Adjust for drawdown
        drawdown_multiplier = self._get_drawdown_multiplier()
        position_value *= drawdown_multiplier
        
        # Adjust for consecutive losses
        loss_multiplier = self._get_consecutive_loss_multiplier()
        position_value *= loss_multiplier
        
        # Calculate actual position size in base currency
        position_size = position_value / entry_price
        
        # Details
        details = {
            "base_risk": base_risk,
            "kelly_fraction": kelly_fraction,
            "kelly_size": kelly_size,
            "confidence_adj": confidence,
            "vol_multiplier": vol_multiplier,
            "drawdown_multiplier": drawdown_multiplier,
            "loss_multiplier": loss_multiplier,
            "final_value": position_value,
            "position_size": position_size,
            "risk_pct": (position_value * stop_loss_pct / self.current_capital) * 100
        }
        
        logger.info(f"📏 Position size for {symbol}: {position_size:.6f} "
                   f"(${position_value:.2f}, risk: {details['risk_pct']:.2f}%)")
        
        return position_size, details
    
    def _get_volatility_multiplier(self, symbol: str) -> float:
        """
        Adjust position size based on volatility regime
        
        Low volatility → larger positions
        High volatility → smaller positions
        """
        if symbol not in self.current_atr or symbol not in self.atr_history:
            return 1.0
        
        current_atr = self.current_atr[symbol]
        atr_history = list(self.atr_history[symbol])
        
        if len(atr_history) < 20:
            return 1.0
        
        avg_atr = np.mean(atr_history)
        
        # Calculate volatility ratio
        vol_ratio = current_atr / avg_atr if avg_atr > 0 else 1.0
        
        # Determine regime and multiplier
        if vol_ratio < 0.7:  # Low volatility
            return 1.3
        elif vol_ratio < 1.3:  # Normal
            return 1.0
        elif vol_ratio < 2.0:  # High
            return 0.7
        else:  # Extreme
            return 0.4
    
    def _get_drawdown_multiplier(self) -> float:
        """
        Reduce position size during drawdowns
        """
        drawdown = (self.peak_capital - self.current_capital) / self.peak_capital
        
        if drawdown < 0.05:  # < 5% drawdown
            return 1.0
        elif drawdown < 0.10:  # 5-10%
            return 0.9
        elif drawdown < 0.15:  # 10-15%
            return 0.7
        elif drawdown < 0.20:  # 15-20%
            return 0.5
        else:  # > 20%
            return 0.3
    
    def _get_consecutive_loss_multiplier(self) -> float:
        """
        Reduce size after consecutive losses
        """
        if self.consecutive_losses == 0:
            return 1.0
        elif self.consecutive_losses == 1:
            return 1.0
        elif self.consecutive_losses == 2:
            return 0.9
        elif self.consecutive_losses == 3:
            return 0.8
        elif self.consecutive_losses == 4:
            return 0.6
        else:  # 5+
            return 0.4
    
    # ==================== CORRELATION TRACKING ====================
    
    def update_price_history(self, symbol: str, price: float, max_history: int = 100):
        """Track price history for correlation calculation"""
        if symbol not in self.price_history:
            self.price_history[symbol] = deque(maxlen=max_history)
        
        self.price_history[symbol].append(price)
    
    def calculate_correlation_matrix(self) -> Dict[str, Dict[str, float]]:
        """
        Calculate correlation between all tracked symbols
        
        Returns correlation matrix as nested dict
        """
        symbols = list(self.price_history.keys())
        
        if len(symbols) < 2:
            return {}
        
        correlation_matrix = {}
        
        for sym1 in symbols:
            correlation_matrix[sym1] = {}
            prices1 = list(self.price_history[sym1])
            
            if len(prices1) < 20:  # Need at least 20 data points
                continue
            
            returns1 = np.diff(prices1) / prices1[:-1]
            
            for sym2 in symbols:
                if sym1 == sym2:
                    correlation_matrix[sym1][sym2] = 1.0
                    continue
                
                prices2 = list(self.price_history[sym2])
                if len(prices2) < 20:
                    continue
                
                returns2 = np.diff(prices2) / prices2[:-1]
                
                # Match lengths
                min_len = min(len(returns1), len(returns2))
                r1 = returns1[-min_len:]
                r2 = returns2[-min_len:]
                
                # Calculate Pearson correlation
                if len(r1) > 1:
                    corr = np.corrcoef(r1, r2)[0, 1]
                    correlation_matrix[sym1][sym2] = corr
        
        return correlation_matrix
    
    def get_portfolio_correlation_score(self) -> float:
        """
        Calculate average correlation of current positions
        
        Returns 0-1, where 1 = all positions perfectly correlated
        """
        if len(self.positions) < 2:
            return 0.0
        
        corr_matrix = self.calculate_correlation_matrix()
        
        if not corr_matrix:
            return 0.0
        
        position_symbols = list(self.positions.keys())
        correlations = []
        
        for i, sym1 in enumerate(position_symbols):
            for sym2 in position_symbols[i+1:]:
                if sym1 in corr_matrix and sym2 in corr_matrix[sym1]:
                    correlations.append(abs(corr_matrix[sym1][sym2]))
        
        if not correlations:
            return 0.0
        
        return np.mean(correlations)
    
    def check_correlation_risk(self, new_symbol: str) -> Tuple[bool, str]:
        """
        Check if adding new position would create too much correlation
        
        Returns (can_add, reason)
        """
        if len(self.positions) == 0:
            return True, "First position"
        
        corr_matrix = self.calculate_correlation_matrix()
        
        if new_symbol not in corr_matrix:
            return True, "No correlation data yet"
        
        # Check correlation with existing positions
        high_correlations = []
        for existing_symbol in self.positions.keys():
            if existing_symbol in corr_matrix[new_symbol]:
                corr = abs(corr_matrix[new_symbol][existing_symbol])
                if corr > 0.8:
                    high_correlations.append((existing_symbol, corr))
        
        if high_correlations:
            symbols = ", ".join([f"{s}({c:.2f})" for s, c in high_correlations])
            return False, f"High correlation with: {symbols}"
        
        # Check if overall portfolio correlation would be too high
        simulated_positions = self.positions.copy()
        simulated_positions[new_symbol] = {"size": 1}  # Dummy
        
        correlations = []
        position_symbols = list(simulated_positions.keys())
        
        for i, sym1 in enumerate(position_symbols):
            for sym2 in position_symbols[i+1:]:
                if sym1 in corr_matrix and sym2 in corr_matrix.get(sym1, {}):
                    correlations.append(abs(corr_matrix[sym1][sym2]))
        
        if correlations:
            avg_corr = np.mean(correlations)
            if avg_corr > self.max_correlation:
                return False, f"Portfolio correlation too high: {avg_corr:.2f}"
        
        return True, "Correlation acceptable"
    
    def get_symbol_sector(self, symbol: str) -> Optional[str]:
        """Get the sector for a given symbol"""
        for sector, symbols in self.SECTOR_GROUPS.items():
            if symbol in symbols:
                return sector
        return None
    
    def check_sector_limits(self, new_symbol: str) -> Tuple[bool, str]:
        """
        Check if adding new symbol violates sector diversification limits
        
        Args:
            new_symbol: Symbol to check
            
        Returns:
            (can_add, reason)
        """
        new_sector = self.get_symbol_sector(new_symbol)
        
        if new_sector is None:
            return True, "Symbol not in sector groups"
        
        # Count existing positions in this sector
        sector_count = 0
        sector_symbols = []
        
        for symbol in self.positions.keys():
            if self.get_symbol_sector(symbol) == new_sector:
                sector_count += 1
                sector_symbols.append(symbol)
        
        # Check limit
        if sector_count >= self.MAX_POSITIONS_PER_SECTOR:
            return False, f"Sector {new_sector} full: {', '.join(sector_symbols)}"
        
        logger.info(f"✅ Sector check passed: {new_sector} has {sector_count}/{self.MAX_POSITIONS_PER_SECTOR} positions")
        return True, "Sector limit OK"
    
    # ==================== POSITION TRACKING ====================
    
    def add_position(self, symbol: str, size: float, entry_price: float, 
                    stop_loss: float, take_profit: float):
        """Register new position for tracking"""
        position_value = size * entry_price
        
        self.positions[symbol] = {
            "size": size,
            "entry_price": entry_price,
            "current_price": entry_price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "value": position_value,
            "unrealized_pnl": 0.0,
            "entry_time": datetime.now(UTC)
        }
        
        logger.info(f"📍 Tracked position: {symbol} ${position_value:.2f}")
    
    def update_position(self, symbol: str, current_price: float):
        """Update position with current price"""
        if symbol not in self.positions:
            return
        
        pos = self.positions[symbol]
        pos["current_price"] = current_price
        
        # Calculate unrealized P&L
        price_change = current_price - pos["entry_price"]
        pos["unrealized_pnl"] = price_change * pos["size"]
        pos["value"] = pos["size"] * current_price
    
    def remove_position(self, symbol: str, exit_price: float, 
                       realized_pnl: float, is_win: bool):
        """Remove closed position and update stats"""
        if symbol in self.positions:
            del self.positions[symbol]
        
        # Update capital
        self.current_capital += realized_pnl
        
        # Update peak
        if self.current_capital > self.peak_capital:
            self.peak_capital = self.current_capital
        
        # Track consecutive wins/losses
        if is_win:
            self.consecutive_wins += 1
            self.consecutive_losses = 0
        else:
            self.consecutive_losses += 1
            self.consecutive_wins = 0
        
        # Add to history
        self.trade_history.append({
            "symbol": symbol,
            "exit_price": exit_price,
            "pnl": realized_pnl,
            "is_win": is_win,
            "time": datetime.now(UTC),
            "capital_after": self.current_capital
        })
        
        logger.info(f"✅ Position closed: {symbol} P&L: ${realized_pnl:+.2f} "
                   f"(Capital: ${self.current_capital:.2f})")
    
    # ==================== RISK CHECKS ====================
    
    def check_daily_limit(self) -> Tuple[bool, str]:
        """Check if daily loss limit hit"""
        self._reset_daily_if_needed()
        
        daily_pnl = self.current_capital - self.daily_start_capital
        daily_pnl_pct = daily_pnl / self.daily_start_capital
        
        if daily_pnl_pct <= -self.max_daily_loss:
            return False, f"Daily loss limit hit: {daily_pnl_pct:.2%}"
        
        return True, f"Daily P&L: {daily_pnl_pct:+.2%}"
    
    def check_monthly_limit(self) -> Tuple[bool, str]:
        """Check if monthly loss limit hit"""
        self._reset_monthly_if_needed()
        
        monthly_pnl = self.current_capital - self.monthly_start_capital
        monthly_pnl_pct = monthly_pnl / self.monthly_start_capital
        
        if monthly_pnl_pct <= -self.max_monthly_loss:
            return False, f"Monthly loss limit hit: {monthly_pnl_pct:.2%}"
        
        return True, f"Monthly P&L: {monthly_pnl_pct:+.2%}"
    
    def check_position_limits(self) -> Tuple[bool, str]:
        """Check if can add more positions"""
        metrics = self.get_portfolio_metrics()
        
        if metrics.total_exposure > self.max_portfolio_heat:
            return False, f"Portfolio heat too high: {metrics.total_exposure:.1%}"
        
        return True, f"Portfolio heat: {metrics.total_exposure:.1%}"
    
    def should_pause_trading(self) -> Tuple[bool, str]:
        """
        Determine if trading should be paused
        
        Reasons to pause:
        - Daily loss limit hit
        - Monthly loss limit hit
        - Too many consecutive losses (5+)
        - Extreme drawdown (>20%)
        """
        # Check daily limit
        can_trade, reason = self.check_daily_limit()
        if not can_trade:
            return True, f"PAUSE: {reason}"
        
        # Check monthly limit
        can_trade, reason = self.check_monthly_limit()
        if not can_trade:
            return True, f"PAUSE: {reason}"
        
        # Check consecutive losses
        if self.consecutive_losses >= 5:
            return True, f"PAUSE: {self.consecutive_losses} consecutive losses"
        
        # Check drawdown
        drawdown = (self.peak_capital - self.current_capital) / self.peak_capital
        if drawdown > 0.20:
            return True, f"PAUSE: Extreme drawdown {drawdown:.1%}"
        
        return False, "Trading allowed"
    
    # ==================== PORTFOLIO METRICS ====================
    
    def get_portfolio_metrics(self) -> PortfolioMetrics:
        """Calculate current portfolio metrics"""
        if not self.positions:
            return PortfolioMetrics(
                total_exposure=0.0,
                position_count=0,
                largest_position=0.0,
                correlation_score=0.0,
                volatility_regime="low",
                current_drawdown=0.0,
                daily_var=0.0
            )
        
        # Total exposure
        total_value = sum(pos["value"] for pos in self.positions.values())
        total_exposure = total_value / self.current_capital
        
        # Largest position
        largest = max(pos["value"] / self.current_capital for pos in self.positions.values())
        
        # Correlation
        corr_score = self.get_portfolio_correlation_score()
        
        # Volatility regime
        vol_regime = self._determine_volatility_regime()
        
        # Drawdown
        drawdown = (self.peak_capital - self.current_capital) / self.peak_capital
        
        # Daily VaR (simplified)
        daily_var = total_exposure * 0.02  # Assume 2% daily move
        
        return PortfolioMetrics(
            total_exposure=total_exposure,
            position_count=len(self.positions),
            largest_position=largest,
            correlation_score=corr_score,
            volatility_regime=vol_regime,
            current_drawdown=drawdown,
            daily_var=daily_var
        )
    
    def _determine_volatility_regime(self) -> str:
        """Determine overall market volatility regime"""
        if not self.current_atr:
            return "unknown"
        
        # Average ATR ratio across all symbols
        ratios = []
        for symbol in self.current_atr.keys():
            if symbol in self.atr_history and len(self.atr_history[symbol]) >= 20:
                current = self.current_atr[symbol]
                avg = np.mean(list(self.atr_history[symbol]))
                if avg > 0:
                    ratios.append(current / avg)
        
        if not ratios:
            return "unknown"
        
        avg_ratio = np.mean(ratios)
        
        if avg_ratio < 0.7:
            return "low"
        elif avg_ratio < 1.3:
            return "medium"
        elif avg_ratio < 2.0:
            return "high"
        else:
            return "extreme"
    
    def update_atr(self, symbol: str, atr: float):
        """Update ATR tracking"""
        self.current_atr[symbol] = atr
        
        if symbol not in self.atr_history:
            self.atr_history[symbol] = deque(maxlen=100)
        
        self.atr_history[symbol].append(atr)
    
    # ==================== TIME RESETS ====================
    
    def _reset_daily_if_needed(self):
        """Reset daily tracking at start of new day"""
        current_day = datetime.now(UTC).day
        
        if current_day != self.last_reset_day:
            self.daily_start_capital = self.current_capital
            self.last_reset_day = current_day
            logger.info(f"📅 Daily reset: Starting capital ${self.current_capital:.2f}")
    
    def _reset_monthly_if_needed(self):
        """Reset monthly tracking at start of new month"""
        current_month = datetime.now(UTC).month
        
        if current_month != self.last_reset_month:
            self.monthly_start_capital = self.current_capital
            self.last_reset_month = current_month
            logger.info(f"📅 Monthly reset: Starting capital ${self.current_capital:.2f}")
    
    # ==================== REPORTING ====================
    
    def get_risk_report(self) -> str:
        """Generate comprehensive risk report"""
        metrics = self.get_portfolio_metrics()
        
        report = ["=" * 50]
        report.append("⚡ RISK MANAGER STATUS")
        report.append("=" * 50)
        
        # Capital
        report.append(f"\n💰 Capital: ${self.current_capital:.2f} (Peak: ${self.peak_capital:.2f})")
        report.append(f"📉 Drawdown: {metrics.current_drawdown:.2%}")
        
        # Daily/Monthly
        daily_ok, daily_msg = self.check_daily_limit()
        monthly_ok, monthly_msg = self.check_monthly_limit()
        report.append(f"\n📊 {daily_msg}")
        report.append(f"📊 {monthly_msg}")
        
        # Positions
        report.append(f"\n📍 Open Positions: {metrics.position_count}")
        report.append(f"💼 Total Exposure: {metrics.total_exposure:.1%}")
        report.append(f"🔝 Largest Position: {metrics.largest_position:.1%}")
        report.append(f"🔗 Correlation: {metrics.correlation_score:.2f}")
        
        # Volatility
        report.append(f"\n📈 Volatility Regime: {metrics.volatility_regime.upper()}")
        report.append(f"⚠️ Daily VaR (95%): {metrics.daily_var:.2%}")
        
        # Performance
        report.append(f"\n🏆 Consecutive Wins: {self.consecutive_wins}")
        report.append(f"❌ Consecutive Losses: {self.consecutive_losses}")
        
        # Trading status
        should_pause, pause_reason = self.should_pause_trading()
        if should_pause:
            report.append(f"\n🚫 TRADING PAUSED: {pause_reason}")
        else:
            report.append(f"\n✅ Trading Active")
        
        report.append("=" * 50)
        
        return "\n".join(report)
