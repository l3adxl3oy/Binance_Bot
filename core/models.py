"""
Data models for Position and Trade tracking
Enhanced for multi-symbol trading
"""

from datetime import datetime, UTC
from typing import Optional, List


class Position:
    """ข้อมูล Position ปัจจุบัน - Enhanced for multi-symbol"""
    
    def __init__(self, symbol: str, side: str, entry_price: float, quantity: float, 
                 stop_loss: float, take_profit: float, confluence_score: int,
                 position_id: Optional[str] = None):
        self.symbol = symbol  # NEW: Track which symbol
        self.position_id = position_id or f"{symbol}_{datetime.now(UTC).timestamp()}"  # NEW: Unique ID
        self.side = side  # "BUY" or "SELL"
        self.entry_price = entry_price
        self.quantity = quantity
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.confluence_score = confluence_score
        self.entry_time = datetime.now(UTC)
        self.exit_price: Optional[float] = None
        self.exit_time: Optional[datetime] = None
        self.profit_percent: Optional[float] = None
        self.profit_amount: Optional[float] = None  # NEW: Actual $ profit
        self.exit_reason: Optional[str] = None
        
        # Trailing stop fields
        self.trailing_stop_active = False
        self.highest_price = entry_price if side == "BUY" else None
        self.lowest_price = entry_price if side == "SELL" else None
        
        # Partial TP tracking
        self.partial_tp_hit = False  # NEW: Track if partial TP was hit
    
    def update_trailing_stop(self, current_price: float, trail_percent: float = 0.3):
        """Update trailing stop levels"""
        if self.side == "BUY":
            if current_price > self.highest_price:
                self.highest_price = current_price
                self.stop_loss = current_price * (1 - trail_percent / 100)
                self.trailing_stop_active = True
        else:  # SELL
            if current_price < self.lowest_price:
                self.lowest_price = current_price
                self.stop_loss = current_price * (1 + trail_percent / 100)
                self.trailing_stop_active = True


class TradeHistory:
    """เก็บประวัติการเทรดทั้งหมด - Enhanced for multi-symbol"""
    
    def __init__(self, starting_balance: float = 100.0):  # Start with $100
        self.trades: List[Position] = []
        self.daily_pnl: float = 0.0
        self.daily_start_balance: float = starting_balance
        self.current_balance: float = starting_balance
        
        # Per-symbol tracking
        self.symbol_stats: dict = {}  # {symbol: {"wins": 0, "losses": 0, "pnl": 0.0}}
    
    def add_trade(self, position: Position):
        """เพิ่ม trade ที่ปิดแล้ว"""
        self.trades.append(position)
        
        # คำนวณ P&L
        if position.side == "BUY":
            pnl_percent = ((position.exit_price - position.entry_price) / position.entry_price) * 100
        else:  # SELL
            pnl_percent = ((position.entry_price - position.exit_price) / position.entry_price) * 100
        
        position.profit_percent = pnl_percent
        
        # Calculate actual profit amount
        pnl_amount = (pnl_percent / 100) * (position.quantity * position.entry_price)
        position.profit_amount = pnl_amount
        
        # Update balance
        self.current_balance += pnl_amount
        self.daily_pnl += pnl_percent
        
        # Update per-symbol stats
        if position.symbol not in self.symbol_stats:
            self.symbol_stats[position.symbol] = {"wins": 0, "losses": 0, "pnl": 0.0, "trades": 0}
        
        self.symbol_stats[position.symbol]["trades"] += 1
        self.symbol_stats[position.symbol]["pnl"] += pnl_percent
        
        if pnl_percent > 0:
            self.symbol_stats[position.symbol]["wins"] += 1
        else:
            self.symbol_stats[position.symbol]["losses"] += 1
    
    def get_win_rate(self) -> float:
        """คำนวณ Win Rate"""
        if not self.trades:
            return 0.0
        
        wins = sum(1 for t in self.trades if t.profit_percent and t.profit_percent > 0)
        return (wins / len(self.trades)) * 100
    
    def get_symbol_win_rate(self, symbol: str) -> float:
        """Get win rate for specific symbol"""
        if symbol not in self.symbol_stats:
            return 0.0
        
        stats = self.symbol_stats[symbol]
        total = stats["wins"] + stats["losses"]
        if total == 0:
            return 0.0
        
        return (stats["wins"] / total) * 100
    
    def get_daily_pnl_percent(self) -> float:
        """คำนวณ Daily P&L %"""
        if self.daily_start_balance == 0:
            return 0.0
        return ((self.current_balance - self.daily_start_balance) / self.daily_start_balance) * 100
    
    def should_stop_trading_today(self, daily_loss_limit: float = 3.0) -> bool:
        """ตรวจสอบว่าควรหยุดเทรดวันนี้หรือไม่ (เกิน daily loss limit)"""
        return self.get_daily_pnl_percent() <= -daily_loss_limit
    
    def should_lock_profit(self, daily_target: float = 2.0) -> bool:
        """Check if daily profit target reached"""
        return self.get_daily_pnl_percent() >= daily_target
    
    def reset_daily(self):
        """Reset daily stats เมื่อเริ่มวันใหม่"""
        self.daily_start_balance = self.current_balance
        self.daily_pnl = 0.0
    
    def get_best_symbols(self, top_n: int = 5) -> List[str]:
        """Get top performing symbols by P&L"""
        if not self.symbol_stats:
            return []
        
        sorted_symbols = sorted(
            self.symbol_stats.items(),
            key=lambda x: x[1]["pnl"],
            reverse=True
        )
        
        return [symbol for symbol, _ in sorted_symbols[:top_n]]
    
    def get_consecutive_losses(self) -> int:
        """Get number of consecutive losing trades (for progressive recovery)"""
        if not self.trades:
            return 0
        
        consecutive = 0
        for trade in reversed(self.trades):
            if trade.profit_percent and trade.profit_percent < 0:
                consecutive += 1
            else:
                break
        
        return consecutive
    
    def get_daily_stats(self):
        """Get comprehensive daily statistics"""
        from dataclasses import dataclass
        
        @dataclass
        class DailyStats:
            total_trades: int
            win_rate: float
            daily_pnl_percent: float
            current_balance: float
        
        return DailyStats(
            total_trades=len([t for t in self.trades if t.entry_time.date() == datetime.now(UTC).date()]),
            win_rate=self.get_win_rate(),
            daily_pnl_percent=self.get_daily_pnl_percent(),
            current_balance=self.current_balance
        )

