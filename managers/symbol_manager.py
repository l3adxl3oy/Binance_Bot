"""
Symbol Manager for Multi-Symbol Trading
Handles momentum scoring and symbol rotation
"""

import time
from typing import List, Dict, Optional
from datetime import datetime, UTC
import numpy as np


class SymbolManager:
    """จัดการ multi-symbol trading with momentum-based rotation"""
    
    def __init__(self, symbol_pool: List[str], max_active: int = 10, rotation_interval: int = 900):
        """
        Args:
            symbol_pool: List of all symbols to monitor
            max_active: Maximum number of symbols to trade simultaneously
            rotation_interval: Seconds between rotation checks (default: 15 min)
        """
        self.symbol_pool = symbol_pool
        self.max_active = max_active
        self.rotation_interval = rotation_interval
        self.last_rotation_time = time.time()
        
        # Active trading symbols (start with first max_active symbols)
        self.active_symbols: List[str] = symbol_pool[:max_active]
        
        # Momentum scores for each symbol
        self.momentum_scores: Dict[str, float] = {symbol: 0.0 for symbol in symbol_pool}
        
        # Performance tracking
        self.symbol_performance: Dict[str, Dict] = {
            symbol: {"score": 0.0, "last_update": time.time()}
            for symbol in symbol_pool
        }
    
    def calculate_momentum_score(self, symbol_data: Dict) -> float:
        """
        Calculate momentum score for a symbol
        
        Args:
            symbol_data: {
                "price_change_pct": float,  # % change in recent period
                "volume_ratio": float,       # current volume / avg volume
                "atr": float,                # Average True Range
                "current_price": float
            }
        
        Returns:
            Momentum score (higher = better)
        """
        # Weight factors
        PRICE_WEIGHT = 0.4
        VOLUME_WEIGHT = 0.3
        VOLATILITY_WEIGHT = 0.3
        
        # Price momentum (absolute value - we trade both directions)
        price_score = abs(symbol_data.get("price_change_pct", 0)) * 10  # Scale up
        
        # Volume surge
        volume_ratio = symbol_data.get("volume_ratio", 1.0)
        volume_score = min(volume_ratio * 20, 100)  # Cap at 100
        
        # Volatility (ATR relative to price)
        atr = symbol_data.get("atr", 0)
        current_price = symbol_data.get("current_price", 1)
        volatility_score = (atr / current_price) * 1000 if current_price > 0 else 0
        
        # Combined score
        total_score = (
            price_score * PRICE_WEIGHT +
            volume_score * VOLUME_WEIGHT +
            volatility_score * VOLATILITY_WEIGHT
        )
        
        return total_score
    
    def update_momentum(self, symbol: str, symbol_data: Dict):
        """Update momentum score for a symbol"""
        score = self.calculate_momentum_score(symbol_data)
        self.momentum_scores[symbol] = score
        self.symbol_performance[symbol]["score"] = score
        self.symbol_performance[symbol]["last_update"] = time.time()
    
    def should_rotate(self) -> bool:
        """Check if it's time to rotate symbols"""
        return (time.time() - self.last_rotation_time) >= self.rotation_interval
    
    def rotate_symbols(self, current_positions: Dict[str, int]) -> List[str]:
        """
        Rotate symbols based on momentum scores
        
        Args:
            current_positions: {symbol: num_open_positions}
        
        Returns:
            Updated list of active symbols
        """
        # Sort symbols by momentum score
        sorted_symbols = sorted(
            self.momentum_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Get top N symbols
        top_symbols = [symbol for symbol, score in sorted_symbols[:self.max_active]]
        
        # Don't remove symbols with open positions
        protected_symbols = [s for s, count in current_positions.items() if count > 0]
        
        # Combine: protected + top momentum (up to max_active)
        new_active = list(set(protected_symbols + top_symbols))[:self.max_active]
        
        # If we still have room, add from top scorers
        if len(new_active) < self.max_active:
            for symbol, score in sorted_symbols:
                if symbol not in new_active:
                    new_active.append(symbol)
                    if len(new_active) >= self.max_active:
                        break
        
        self.active_symbols = new_active
        self.last_rotation_time = time.time()
        
        return new_active
    
    def get_active_symbols(self) -> List[str]:
        """Get currently active trading symbols"""
        return self.active_symbols.copy()
    
    def get_top_momentum_symbols(self, n: int = 5) -> List[tuple]:
        """Get top N symbols by momentum score"""
        sorted_symbols = sorted(
            self.momentum_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_symbols[:n]
    
    def is_symbol_active(self, symbol: str) -> bool:
        """Check if symbol is currently active for trading"""
        return symbol in self.active_symbols
    
    def get_symbol_score(self, symbol: str) -> float:
        """Get momentum score for specific symbol"""
        return self.momentum_scores.get(symbol, 0.0)
    
    def get_rotation_status(self) -> Dict:
        """Get rotation status info"""
        time_since_rotation = time.time() - self.last_rotation_time
        time_until_next = max(0, self.rotation_interval - time_since_rotation)
        
        return {
            "last_rotation": datetime.fromtimestamp(self.last_rotation_time, UTC).strftime("%H:%M:%S"),
            "next_rotation_in": int(time_until_next),
            "active_count": len(self.active_symbols),
            "total_pool": len(self.symbol_pool)
        }
