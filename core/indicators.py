"""
Technical Indicators for Trading Bot
Extracted from advanced_scalping_bot.py for modularity
"""

import numpy as np
import pandas as pd
from typing import Tuple, List


class Indicators:
    """คำนวณ Technical Indicators ต่างๆ"""
    
    @staticmethod
    def calculate_rsi(prices: np.ndarray, period: int = 14) -> float:
        """คำนวณ RSI (Relative Strength Index)"""
        if len(prices) < period + 1:
            return 50.0
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def calculate_bollinger_bands(prices: np.ndarray, period: int = 20, std_dev: float = 2.0) -> Tuple[float, float, float]:
        """คำนวณ Bollinger Bands (Upper, Middle, Lower)"""
        if len(prices) < period:
            return 0.0, 0.0, 0.0
        
        sma = np.mean(prices[-period:])
        std = np.std(prices[-period:])
        
        upper = sma + (std_dev * std)
        lower = sma - (std_dev * std)
        
        return upper, sma, lower
    
    @staticmethod
    def calculate_macd(prices: np.ndarray, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[float, float, float]:
        """คำนวณ MACD (MACD Line, Signal Line, Histogram)"""
        if len(prices) < slow + signal:
            return 0.0, 0.0, 0.0
        
        # EMA Calculation
        ema_fast = pd.Series(prices).ewm(span=fast, adjust=False).mean()
        ema_slow = pd.Series(prices).ewm(span=slow, adjust=False).mean()
        
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return macd_line.iloc[-1], signal_line.iloc[-1], histogram.iloc[-1]
    
    @staticmethod
    def calculate_atr(high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int = 14) -> float:
        """คำนวณ ATR (Average True Range)"""
        if len(high) < period + 1:
            return 0.0
        
        tr_list = []
        for i in range(1, len(high)):
            tr = max(
                high[i] - low[i],
                abs(high[i] - close[i - 1]),
                abs(low[i] - close[i - 1])
            )
            tr_list.append(tr)
        
        atr = np.mean(tr_list[-period:])
        return atr
    
    @staticmethod
    def find_support_resistance(prices: np.ndarray, window: int = 5) -> Tuple[List[float], List[float]]:
        """หา Support และ Resistance levels จาก local min/max"""
        if len(prices) < window * 2:
            return [], []
        
        supports = []
        resistances = []
        
        for i in range(window, len(prices) - window):
            # Local minimum (support)
            if prices[i] == min(prices[i - window:i + window + 1]):
                supports.append(prices[i])
            
            # Local maximum (resistance)
            if prices[i] == max(prices[i - window:i + window + 1]):
                resistances.append(prices[i])
        
        # เอาแค่ level ที่สำคัญ (กรอง duplicates)
        supports = sorted(list(set(supports)))[-3:] if supports else []
        resistances = sorted(list(set(resistances)))[-3:] if resistances else []
        
        return supports, resistances
