"""
Unit Tests for Technical Indicators
"""
import pytest
import numpy as np
from core.indicators import Indicators


class TestIndicators:
    """Test suite for technical indicators"""
    
    def test_rsi_calculation(self, sample_price_data):
        """Test RSI indicator calculation"""
        close_prices = sample_price_data['close']
        rsi = Indicators.calculate_rsi(close_prices, period=14)
        
        # RSI should be between 0 and 100
        assert 0 <= rsi <= 100
        assert isinstance(rsi, (int, float))
        
    def test_rsi_overbought_oversold(self):
        """Test RSI detects overbought/oversold conditions"""
        # Overbought scenario (prices going up)
        uptrend = np.array([100, 102, 104, 106, 108, 110, 112, 114, 116, 118, 120, 122, 124, 126, 128])
        rsi_up = Indicators.calculate_rsi(uptrend, period=14)
        assert rsi_up > 70  # Should be overbought
        
        # Oversold scenario (prices going down)
        downtrend = np.array([100, 98, 96, 94, 92, 90, 88, 86, 84, 82, 80, 78, 76, 74, 72])
        rsi_down = Indicators.calculate_rsi(downtrend, period=14)
        assert rsi_down < 30  # Should be oversold
    
    def test_bollinger_bands(self, sample_price_data):
        """Test Bollinger Bands calculation"""
        close_prices = sample_price_data['close']
        upper, middle, lower = Indicators.calculate_bollinger_bands(close_prices, period=20, std_dev=2)
        
        # Upper should be above middle, middle above lower
        assert upper > middle > lower
        
        # Middle should be close to SMA
        sma = np.mean(close_prices[-20:])
        assert abs(middle - sma) < 0.1
        
    def test_macd(self, sample_price_data):
        """Test MACD calculation"""
        close_prices = sample_price_data['close']
        macd_line, signal_line, histogram = Indicators.calculate_macd(
            close_prices, fast=12, slow=26, signal=9
        )
        
        # All values should be numbers
        assert isinstance(macd_line, (int, float))
        assert isinstance(signal_line, (int, float))
        assert isinstance(histogram, (int, float))
        
        # Histogram should be difference between MACD and Signal
        expected_hist = macd_line - signal_line
        assert abs(histogram - expected_hist) < 0.001
        
    def test_atr(self, sample_price_data):
        """Test ATR (Average True Range) calculation"""
        high = sample_price_data['high']
        low = sample_price_data['low']
        close = sample_price_data['close']
        
        atr = Indicators.calculate_atr(high, low, close, period=14)
        
        # ATR should be positive
        assert atr > 0
        assert isinstance(atr, (int, float))
        
    def test_invalid_input(self):
        """Test error handling for invalid inputs"""
        # Short array - should handle gracefully
        short_array = np.array([100, 101, 102])
        result = Indicators.calculate_rsi(short_array, period=14)
        # Should return a number (not raise error)
        assert isinstance(result, (int, float))


class TestIndicatorsEdgeCases:
    """Test edge cases and error handling"""
    
    def test_constant_prices(self):
        """Test indicators with constant prices"""
        constant = np.array([100.0] * 30)
        
        # RSI with constant prices
        rsi = Indicators.calculate_rsi(constant, period=14)
        # May return 100 or 50 depending on implementation
        assert isinstance(rsi, (int, float))
        assert 0 <= rsi <= 100
        
        # Bollinger Bands should collapse
        upper, middle, lower = Indicators.calculate_bollinger_bands(constant, period=20, std_dev=2)
        assert abs(upper - lower) < 1.0  # Very narrow bands
        
    def test_insufficient_data(self):
        """Test with insufficient data points"""
        short_data = np.array([100, 101, 102, 103, 104])
        
        # Should handle gracefully or return default
        try:
            rsi = Indicators.calculate_rsi(short_data, period=14)
            assert rsi is not None
        except (ValueError, IndexError):
            pass  # Expected behavior
