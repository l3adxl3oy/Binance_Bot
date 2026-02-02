"""
Trailing Stop Module
Manages dynamic stop loss adjustments
"""

from typing import Optional
from core.models import Position


class TrailingStopManager:
    """จัดการ Trailing Stop สำหรับ positions"""
    
    def __init__(self, trail_percent: float = 0.3, activation_profit: float = 0.3):
        """
        Args:
            trail_percent: Distance of trailing stop from peak (%)
            activation_profit: Minimum profit % before trailing activates
        """
        self.trail_percent = trail_percent
        self.activation_profit = activation_profit
    
    def should_activate(self, position: Position, current_price: float) -> bool:
        """Check if trailing stop should be activated"""
        if position.trailing_stop_active:
            return True
        
        # Calculate current profit
        if position.side == "BUY":
            profit_pct = ((current_price - position.entry_price) / position.entry_price) * 100
        else:  # SELL
            profit_pct = ((position.entry_price - current_price) / position.entry_price) * 100
        
        # Activate if profit threshold reached
        return profit_pct >= self.activation_profit
    
    def update_trailing_stop(self, position: Position, current_price: float) -> bool:
        """
        Update trailing stop for a position
        
        Returns:
            True if stop loss was updated, False otherwise
        """
        # Check if should activate
        if not self.should_activate(position, current_price):
            return False
        
        updated = False
        
        if position.side == "BUY":
            # For long positions, trail below the highest price
            if position.highest_price is None or current_price > position.highest_price:
                position.highest_price = current_price
                new_stop = current_price * (1 - self.trail_percent / 100)
                
                # Only update if new stop is higher than current
                if new_stop > position.stop_loss:
                    position.stop_loss = new_stop
                    position.trailing_stop_active = True
                    updated = True
        
        else:  # SELL
            # For short positions, trail above the lowest price
            if position.lowest_price is None or current_price < position.lowest_price:
                position.lowest_price = current_price
                new_stop = current_price * (1 + self.trail_percent / 100)
                
                # Only update if new stop is lower than current
                if new_stop < position.stop_loss:
                    position.stop_loss = new_stop
                    position.trailing_stop_active = True
                    updated = True
        
        return updated
    
    def check_stop_hit(self, position: Position, current_price: float) -> bool:
        """Check if trailing stop has been hit"""
        if position.side == "BUY":
            return current_price <= position.stop_loss
        else:  # SELL
            return current_price >= position.stop_loss
    
    def get_trail_info(self, position: Position, current_price: float) -> dict:
        """Get trailing stop information for a position"""
        if position.side == "BUY":
            profit_pct = ((current_price - position.entry_price) / position.entry_price) * 100
            distance_to_stop = ((current_price - position.stop_loss) / current_price) * 100 if current_price > 0 else 0
            peak_price = position.highest_price if position.highest_price else position.entry_price
        else:  # SELL
            profit_pct = ((position.entry_price - current_price) / position.entry_price) * 100
            distance_to_stop = ((position.stop_loss - current_price) / current_price) * 100 if current_price > 0 else 0
            peak_price = position.lowest_price if position.lowest_price else position.entry_price
        
        return {
            "active": position.trailing_stop_active,
            "current_profit_pct": round(profit_pct, 2),
            "stop_loss": position.stop_loss,
            "distance_to_stop_pct": round(distance_to_stop, 2),
            "peak_price": peak_price,
            "trail_percent": self.trail_percent
        }


class ATRTrailingStop:
    """ATR-based trailing stop (alternative to percentage-based)"""
    
    def __init__(self, atr_multiplier: float = 2.0, activation_profit: float = 0.3):
        """
        Args:
            atr_multiplier: ATR multiplier for stop distance
            activation_profit: Minimum profit % before trailing activates
        """
        self.atr_multiplier = atr_multiplier
        self.activation_profit = activation_profit
    
    def update_trailing_stop(self, position: Position, current_price: float, atr: float) -> bool:
        """Update trailing stop based on ATR"""
        # Calculate current profit
        if position.side == "BUY":
            profit_pct = ((current_price - position.entry_price) / position.entry_price) * 100
        else:
            profit_pct = ((position.entry_price - current_price) / position.entry_price) * 100
        
        # Check activation
        if profit_pct < self.activation_profit:
            return False
        
        updated = False
        trail_distance = atr * self.atr_multiplier
        
        if position.side == "BUY":
            if position.highest_price is None or current_price > position.highest_price:
                position.highest_price = current_price
                new_stop = current_price - trail_distance
                
                if new_stop > position.stop_loss:
                    position.stop_loss = new_stop
                    position.trailing_stop_active = True
                    updated = True
        
        else:  # SELL
            if position.lowest_price is None or current_price < position.lowest_price:
                position.lowest_price = current_price
                new_stop = current_price + trail_distance
                
                if new_stop < position.stop_loss:
                    position.stop_loss = new_stop
                    position.trailing_stop_active = True
                    updated = True
        
        return updated
