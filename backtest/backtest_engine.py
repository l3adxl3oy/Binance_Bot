"""
🚀 Backtest Engine
จำลองการเทรดด้วยข้อมูลย้อนหลัง
"""

import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, UTC
from typing import Dict, List, Optional, Tuple
import sys
from pathlib import Path

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.indicators import Indicators
from core.models import Position
from config.strategy_constants import StrategyConstants

logger = logging.getLogger(__name__)


class BacktestEngine:
    """
    Backtest Engine - จำลองการเทรดด้วยข้อมูลย้อนหลัง
    
    Features:
    - Realistic order execution with slippage
    - Commission/fee calculation
    - Position management
    - Multiple symbol support
    - Signal generation using bot's strategy
    """
    
    def __init__(
        self,
        initial_balance: float,
        commission_rate: float = 0.001,  # 0.1% per trade
        slippage_pct: float = 0.0005,    # 0.05% slippage
        max_positions: int = 3,
        position_size_pct: float = 0.33   # 33% per position
    ):
        """
        Initialize backtest engine
        
        Args:
            initial_balance: Starting capital
            commission_rate: Trading fee (0.001 = 0.1%)
            slippage_pct: Slippage percentage
            max_positions: Maximum concurrent positions
            position_size_pct: Position size as % of balance
        """
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.commission_rate = commission_rate
        self.slippage_pct = slippage_pct
        self.max_positions = max_positions
        self.position_size_pct = position_size_pct
        
        # Trading state
        self.positions: Dict[str, Position] = {}
        self.trades: List[Dict] = []
        self.equity_curve: List[Dict] = []
        
        # Statistics
        self.total_commission = 0
        self.total_slippage = 0
        
        # Strategy parameters (for aggressive mode support)
        self._current_strategy_params = None
        
    def run_backtest(
        self,
        data: Dict[str, pd.DataFrame],
        strategy_params: Optional[Dict] = None
    ) -> Dict:
        """
        รัน backtest บนข้อมูลหลายคู่เทรด
        
        Args:
            data: Dict mapping symbol -> DataFrame
            strategy_params: Optional strategy parameters
            
        Returns:
            Dict with backtest results
        """
        logger.info("🚀 Starting backtest...")
        logger.info(f"💰 Initial Balance: ${self.initial_balance:,.2f}")
        logger.info(f"📊 Symbols: {len(data)}")
        
        # Get common timestamps across all symbols
        timestamps = self._get_common_timestamps(data)
        logger.info(f"⏰ Total candles to process: {len(timestamps)}")
        
        # Process each timestamp
        for i, timestamp in enumerate(timestamps):
            # Get current market data for all symbols
            current_data = {}
            for symbol, df in data.items():
                candle = df[df['timestamp'] == timestamp]
                if len(candle) > 0:
                    # Get historical data up to this point
                    historical = df[df['timestamp'] <= timestamp]
                    current_data[symbol] = {
                        'current': candle.iloc[0],
                        'historical': historical
                    }
            
            # Process this timestamp
            self._process_timestamp(timestamp, current_data, strategy_params)
            
            # Log progress
            if (i + 1) % 1000 == 0:
                logger.info(f"⏳ Processed {i+1}/{len(timestamps)} candles...")
        
        # Close any remaining positions
        self._close_all_positions(timestamp)
        
        logger.info("✅ Backtest completed!")
        
        return {
            "trades": self.trades,
            "equity_curve": self.equity_curve,
            "final_balance": self.balance,
            "total_commission": self.total_commission,
            "total_slippage": self.total_slippage
        }
    
    def _process_timestamp(
        self,
        timestamp: datetime,
        current_data: Dict,
        strategy_params: Optional[Dict]
    ):
        """ประมวลผล timestamp เดียว"""
        
        # 1. Check existing positions for exit signals
        self._check_exit_signals(timestamp, current_data)
        
        # 2. Check for new entry signals (if not at max positions)
        if len(self.positions) < self.max_positions:
            self._check_entry_signals(timestamp, current_data, strategy_params)
        
        # Store strategy params for position management
        self._current_strategy_params = strategy_params
        
        # 3. Record equity
        self._record_equity(timestamp)
    
    def _check_entry_signals(
        self,
        timestamp: datetime,
        current_data: Dict,
        strategy_params: Optional[Dict]
    ):
        """ตรวจสอบสัญญาณเข้า"""
        
        for symbol, data in current_data.items():
            # Skip if already in position
            if symbol in self.positions:
                continue
            
            historical = data['historical']
            
            # Need enough data for indicators
            if len(historical) < 50:
                continue
            
            # Calculate indicators
            signals = self._calculate_signals(historical)
            
            # Check entry conditions
            # For aggressive mode, check signal strength threshold
            min_signal_strength = 3  # Default
            if strategy_params and strategy_params.get('strategy_mode') == 'aggressive':
                min_signal_strength = strategy_params.get('min_signal_strength', 3.0)
            
            if self._should_enter_long(signals, min_signal_strength):
                self._open_position(symbol, 'LONG', timestamp, data['current'], strategy_params)
            elif self._should_enter_short(signals, min_signal_strength):
                # For spot trading, we skip shorts
                # self._open_position(symbol, 'SHORT', timestamp, data['current'], strategy_params)
                pass
    
    def _check_exit_signals(self, timestamp: datetime, current_data: Dict):
        """ตรวจสอบสัญญาณออก"""
        
        positions_to_close = []
        
        for symbol, position in self.positions.items():
            if symbol not in current_data:
                continue
            
            current_price = float(current_data[symbol]['current']['close'])
            
            # Check stop loss
            if position.stop_loss and current_price <= position.stop_loss:
                positions_to_close.append((symbol, current_price, 'STOP_LOSS'))
                continue
            
            # Check take profit
            if position.take_profit and current_price >= position.take_profit:
                positions_to_close.append((symbol, current_price, 'TAKE_PROFIT'))
                continue
            
            # Check time-based exit (max hold time)
            entry_time_naive = position.entry_time.replace(tzinfo=None) if position.entry_time.tzinfo else position.entry_time
            hold_time = (timestamp - entry_time_naive).total_seconds()
            
            # Use strategy_params time_stop if available
            strategy_params = getattr(self, '_current_strategy_params', None)
            max_hold_time = 3600  # Default 1 hour
            if strategy_params and strategy_params.get('strategy_mode') == 'aggressive':
                max_hold_time = strategy_params.get('time_stop_seconds', 600)
            
            if hold_time > max_hold_time:
                positions_to_close.append((symbol, current_price, 'TIME_EXIT'))
                continue
            
            # Check trailing stop or other exit conditions
            historical = current_data[symbol]['historical']
            signals = self._calculate_signals(historical)
            
            # Get strategy params for exit logic
            strategy_params = getattr(self, '_current_strategy_params', None)
            if self._should_exit(signals, position, strategy_params):
                positions_to_close.append((symbol, current_price, 'SIGNAL_EXIT'))
        
        # Close positions
        for symbol, price, reason in positions_to_close:
            self._close_position(symbol, timestamp, price, reason)
    
    def _calculate_signals(self, df: pd.DataFrame) -> Dict:
        """คำนวณ signals ตามกลยุทธ์ของบอท"""
        
        close = df['close'].values
        high = df['high'].values
        low = df['low'].values
        volume = df['volume'].values
        
        # RSI
        rsi = Indicators.calculate_rsi(close, StrategyConstants.RSI_PERIOD)
        
        # Bollinger Bands
        bb_upper, bb_middle, bb_lower = Indicators.calculate_bollinger_bands(
            close,
            StrategyConstants.BB_PERIOD,
            StrategyConstants.BB_STD_DEV
        )
        
        # MACD
        macd, signal, histogram = Indicators.calculate_macd(
            close,
            StrategyConstants.MACD_FAST,
            StrategyConstants.MACD_SLOW,
            StrategyConstants.MACD_SIGNAL
        )
        
        # ATR
        atr = Indicators.calculate_atr(high, low, close, StrategyConstants.ATR_PERIOD)
        
        # EMAs for trend
        ema_fast = np.mean(close[-StrategyConstants.EMA_FAST:]) if len(close) >= StrategyConstants.EMA_FAST else close[-1]
        ema_slow = np.mean(close[-StrategyConstants.EMA_SLOW:]) if len(close) >= StrategyConstants.EMA_SLOW else close[-1]
        
        # Volume analysis
        avg_volume = np.mean(volume[-StrategyConstants.VOLUME_PERIOD:]) if len(volume) >= StrategyConstants.VOLUME_PERIOD else volume[-1]
        volume_ratio = volume[-1] / avg_volume if avg_volume > 0 else 1.0
        
        current_price = close[-1]
        bb_position = (current_price - bb_lower) / (bb_upper - bb_lower) if (bb_upper - bb_lower) > 0 else 0.5
        
        return {
            'rsi': rsi,
            'bb_upper': bb_upper,
            'bb_middle': bb_middle,
            'bb_lower': bb_lower,
            'bb_position': bb_position,
            'macd': macd,
            'macd_signal': signal,
            'macd_histogram': histogram,
            'atr': atr,
            'ema_fast': ema_fast,
            'ema_slow': ema_slow,
            'volume_ratio': volume_ratio,
            'current_price': current_price
        }
    
    def _should_enter_long(self, signals: Dict, min_confluence: int = 3) -> bool:
        """ตรวจสอบเงื่อนไขเข้า LONG"""
        
        confluence = 0
        
        # RSI oversold
        if signals['rsi'] < StrategyConstants.RSI_OVERSOLD:
            confluence += 1
        
        # Price near lower BB
        if signals['bb_position'] < 0.2:
            confluence += 1
        
        # MACD bullish crossover
        if signals['macd'] > signals['macd_signal'] and signals['macd_histogram'] > 0:
            confluence += 1
        
        # Uptrend
        if signals['ema_fast'] > signals['ema_slow']:
            confluence += 1
        
        # Volume confirmation
        if signals['volume_ratio'] > StrategyConstants.VOLUME_MULTIPLIER:
            confluence += 1
        
        # Check against required confluence (default 3, aggressive might require more)
        return confluence >= min_confluence
    
    def _should_enter_short(self, signals: Dict, min_confluence: int = 3) -> bool:
        """ตรวจสอบเงื่อนไขเข้า SHORT"""
        
        confluence = 0
        
        # RSI overbought
        if signals['rsi'] > StrategyConstants.RSI_OVERBOUGHT:
            confluence += 1
        
        # Price near upper BB
        if signals['bb_position'] > 0.8:
            confluence += 1
        
        # MACD bearish crossover
        if signals['macd'] < signals['macd_signal'] and signals['macd_histogram'] < 0:
            confluence += 1
        
        # Downtrend
        if signals['ema_fast'] < signals['ema_slow']:
            confluence += 1
        
        # Volume confirmation
        if signals['volume_ratio'] > StrategyConstants.VOLUME_MULTIPLIER:
            confluence += 1
        
        # Check against required confluence
        return confluence >= min_confluence
    
    def _should_exit(self, signals: Dict, position: Position, strategy_params: Optional[Dict] = None) -> bool:
        """ตรวจสอบเงื่อนไขออกจากเทรด"""
        
        if position.side == 'LONG':
            # Exit if RSI overbought
            if signals['rsi'] > StrategyConstants.RSI_OVERBOUGHT:
                return True
            
            # Exit if price hits upper BB
            if signals['bb_position'] > 0.9:
                return True
            
            # Exit if MACD bearish crossover
            if signals['macd'] < signals['macd_signal']:
                return True
        
        return False
    
    def _open_position(
        self,
        symbol: str,
        side: str,
        timestamp: datetime,
        candle: pd.Series,
        strategy_params: Optional[Dict] = None
    ):
        """เปิดตำแหน่งเทรด"""
        
        entry_price = float(candle['close'])
        
        # Apply slippage
        if side == 'LONG':
            entry_price *= (1 + self.slippage_pct)
        else:
            entry_price *= (1 - self.slippage_pct)
        
        # Calculate position size
        position_value = self.balance * self.position_size_pct
        quantity = position_value / entry_price
        
        # Calculate commission
        commission = position_value * self.commission_rate
        self.total_commission += commission
        
        # Calculate SL/TP based on strategy mode
        if strategy_params and strategy_params.get('strategy_mode') == 'aggressive':
            # Use aggressive parameters from strategy_params
            tp_pct = strategy_params.get('take_profit_pct', 0.012)  # Default 1.2%
            sl_pct = strategy_params.get('stop_loss_pct', 0.006)    # Default 0.6%
            
            if side == 'LONG':
                stop_loss = entry_price * (1 - sl_pct)
                take_profit = entry_price * (1 + tp_pct)
            else:
                stop_loss = entry_price * (1 + sl_pct)
                take_profit = entry_price * (1 - tp_pct)
        else:
            # Use default ATR-based calculation for non-aggressive strategies
            atr = float(candle['close']) * 0.01  # Simple 1% ATR approximation
            stop_loss = entry_price - (2 * atr) if side == 'LONG' else entry_price + (2 * atr)
            take_profit = entry_price + (3 * atr) if side == 'LONG' else entry_price - (3 * atr)
        
        # Create position (note: entry_time is set automatically in Position.__init__)
        position = Position(
            symbol=symbol,
            side='BUY' if side == 'LONG' else 'SELL',  # Convert to BUY/SELL
            entry_price=entry_price,
            quantity=quantity,
            stop_loss=stop_loss,
            take_profit=take_profit,
            confluence_score=3  # Backtest default
        )
        
        self.positions[symbol] = position
        
        logger.debug(f"📈 OPEN {side} {symbol} @ ${entry_price:.4f} | Qty: {quantity:.4f}")
    
    def _close_position(
        self,
        symbol: str,
        timestamp: datetime,
        exit_price: float,
        reason: str
    ):
        """ปิดตำแหน่งเทรด"""
        
        if symbol not in self.positions:
            return
        
        position = self.positions[symbol]
        
        # Apply slippage
        if position.side == 'LONG':
            exit_price *= (1 - self.slippage_pct)
        else:
            exit_price *= (1 + self.slippage_pct)
        
        # Calculate P&L
        if position.side == 'LONG':
            pnl = (exit_price - position.entry_price) * position.quantity
        else:
            pnl = (position.entry_price - exit_price) * position.quantity
        
        # Subtract commission
        position_value = exit_price * position.quantity
        commission = position_value * self.commission_rate
        self.total_commission += commission
        pnl -= commission
        
        # Update balance
        self.balance += pnl
        
        # Calculate P&L percentage
        pnl_pct = (pnl / (position.entry_price * position.quantity)) * 100
        
        # Calculate duration (handle timezone difference)
        entry_time_naive = position.entry_time.replace(tzinfo=None) if position.entry_time.tzinfo else position.entry_time
        duration_seconds = (timestamp - entry_time_naive).total_seconds()
        
        # Record trade
        trade = {
            'symbol': symbol,
            'side': position.side,
            'entry_time': position.entry_time,
            'exit_time': timestamp,
            'entry_price': position.entry_price,
            'exit_price': exit_price,
            'quantity': position.quantity,
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'reason': reason,
            'duration_seconds': duration_seconds
        }
        
        self.trades.append(trade)
        
        # Remove position
        del self.positions[symbol]
        
        emoji = "✅" if pnl > 0 else "❌"
        logger.debug(f"{emoji} CLOSE {symbol} @ ${exit_price:.4f} | P&L: ${pnl:.2f} ({pnl_pct:+.2f}%) | {reason}")
    
    def _close_all_positions(self, timestamp: datetime):
        """ปิดตำแหน่งทั้งหมดที่เหลือ"""
        
        symbols = list(self.positions.keys())
        for symbol in symbols:
            position = self.positions[symbol]
            # Use entry price as approximation for exit
            self._close_position(symbol, timestamp, position.entry_price, 'BACKTEST_END')
    
    def _record_equity(self, timestamp: datetime):
        """บันทึก equity ณ เวลาปัจจุบัน"""
        
        # Calculate unrealized P&L
        unrealized_pnl = 0
        # (In real backtest, we'd calculate current value of open positions)
        
        equity = self.balance + unrealized_pnl
        
        self.equity_curve.append({
            'timestamp': timestamp,
            'balance': self.balance,
            'equity': equity,
            'open_positions': len(self.positions)
        })
    
    def _get_common_timestamps(self, data: Dict[str, pd.DataFrame]) -> List[datetime]:
        """หา timestamps ที่มีอยู่ในทุก symbol"""
        
        # Get all unique timestamps
        all_timestamps = set()
        for df in data.values():
            all_timestamps.update(df['timestamp'].tolist())
        
        # Sort chronologically
        return sorted(list(all_timestamps))
