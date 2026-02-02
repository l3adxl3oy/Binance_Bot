"""
Position Manager for Multi-Position Tracking
Handles multiple concurrent positions across symbols
"""

from typing import List, Dict, Optional
from core.models import Position


class PositionManager:
    """จัดการ multiple positions พร้อมกันหลาย symbols"""
    
    def __init__(self, max_total_positions: int = 10, max_per_symbol: int = 2):
        """
        Args:
            max_total_positions: Maximum total open positions
            max_per_symbol: Maximum positions per symbol
        """
        self.max_total_positions = max_total_positions
        self.max_per_symbol = max_per_symbol
        
        # Active positions storage
        self.positions: Dict[str, Position] = {}  # {position_id: Position}
        
        # Index by symbol for quick lookup
        self.symbol_positions: Dict[str, List[str]] = {}  # {symbol: [position_ids]}
    
    def add_position(self, position: Position) -> bool:
        """
        Add a new position
        
        Returns:
            True if added successfully, False if limits exceeded
        """
        # Check total limit
        if len(self.positions) >= self.max_total_positions:
            return False
        
        # Check per-symbol limit
        symbol_count = len(self.symbol_positions.get(position.symbol, []))
        if symbol_count >= self.max_per_symbol:
            return False
        
        # Add position
        self.positions[position.position_id] = position
        
        # Update symbol index
        if position.symbol not in self.symbol_positions:
            self.symbol_positions[position.symbol] = []
        self.symbol_positions[position.symbol].append(position.position_id)
        
        return True
    
    def remove_position(self, position_id: str) -> Optional[Position]:
        """Remove and return a position"""
        if position_id not in self.positions:
            return None
        
        position = self.positions.pop(position_id)
        
        # Update symbol index
        if position.symbol in self.symbol_positions:
            self.symbol_positions[position.symbol].remove(position_id)
            if not self.symbol_positions[position.symbol]:
                del self.symbol_positions[position.symbol]
        
        return position
    
    def get_position(self, position_id: str) -> Optional[Position]:
        """Get position by ID"""
        return self.positions.get(position_id)
    
    def get_all_positions(self) -> List[Position]:
        """Get all active positions"""
        return list(self.positions.values())
    
    def get_symbol_positions(self, symbol: str) -> List[Position]:
        """Get all positions for a specific symbol"""
        position_ids = self.symbol_positions.get(symbol, [])
        return [self.positions[pid] for pid in position_ids if pid in self.positions]
    
    def get_position_count(self) -> int:
        """Get total number of open positions"""
        return len(self.positions)
    
    def get_symbol_position_count(self, symbol: str) -> int:
        """Get number of positions for a symbol"""
        return len(self.symbol_positions.get(symbol, []))
    
    def can_open_position(self, symbol: str) -> bool:
        """Check if we can open a new position for this symbol"""
        if self.get_position_count() >= self.max_total_positions:
            return False
        
        if self.get_symbol_position_count(symbol) >= self.max_per_symbol:
            return False
        
        return True
    
    def get_total_exposure(self) -> float:
        """Calculate total capital exposure (sum of all position values)"""
        total = 0.0
        for position in self.positions.values():
            position_value = position.entry_price * position.quantity
            total += position_value
        return total
    
    def get_symbol_exposure(self, symbol: str) -> float:
        """Calculate exposure for specific symbol"""
        total = 0.0
        for position in self.get_symbol_positions(symbol):
            position_value = position.entry_price * position.quantity
            total += position_value
        return total
    
    def get_positions_by_side(self, side: str) -> List[Position]:
        """Get all positions with specific side (BUY/SELL)"""
        return [p for p in self.positions.values() if p.side == side]
    
    def get_oldest_position(self, symbol: Optional[str] = None) -> Optional[Position]:
        """Get oldest position, optionally filtered by symbol"""
        positions = self.get_symbol_positions(symbol) if symbol else self.get_all_positions()
        
        if not positions:
            return None
        
        return min(positions, key=lambda p: p.entry_time)
    
    def get_positions_summary(self) -> Dict:
        """Get summary statistics of all positions"""
        if not self.positions:
            return {
                "total": 0,
                "by_symbol": {},
                "by_side": {"BUY": 0, "SELL": 0},
                "total_exposure": 0.0
            }
        
        # Count by symbol
        by_symbol = {}
        for symbol, pos_ids in self.symbol_positions.items():
            by_symbol[symbol] = len(pos_ids)
        
        # Count by side
        buy_count = len([p for p in self.positions.values() if p.side == "BUY"])
        sell_count = len([p for p in self.positions.values() if p.side == "SELL"])
        
        return {
            "total": len(self.positions),
            "by_symbol": by_symbol,
            "by_side": {"BUY": buy_count, "SELL": sell_count},
            "total_exposure": self.get_total_exposure()
        }
    
    def clear_all(self):
        """Clear all positions (use with caution!)"""
        self.positions.clear()
        self.symbol_positions.clear()
