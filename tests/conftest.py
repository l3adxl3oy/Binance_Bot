"""
Pytest configuration and fixtures
"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
from unittest.mock import Mock, MagicMock
from datetime import datetime


# ==================== MOCK DATA ====================
@pytest.fixture
def sample_klines_data():
    """Sample klines data for testing"""
    return [
        [1609459200000, '29000.00', '29500.00', '28800.00', '29200.00', '100.5', 
         1609462799999, '2920000.00', 150, '50.2', '1460400.00', '0'],
        [1609462800000, '29200.00', '29600.00', '29100.00', '29400.00', '95.3',
         1609466399999, '2800000.00', 140, '48.1', '1414000.00', '0'],
        # Add more candles for testing
    ] * 20  # 40 candles total


@pytest.fixture
def sample_price_data():
    """Sample price data for indicators"""
    return {
        'close': np.array([29000, 29200, 29400, 29300, 29500, 29600, 29400, 29700, 29800, 30000] * 3),
        'high': np.array([29500, 29600, 29800, 29700, 29900, 30000, 29800, 30100, 30200, 30400] * 3),
        'low': np.array([28800, 29000, 29200, 29100, 29300, 29400, 29200, 29500, 29600, 29800] * 3),
        'volume': np.array([100, 95, 110, 105, 120, 115, 100, 130, 125, 140] * 3),
        'current_price': 30000.0
    }


@pytest.fixture
def mock_binance_client():
    """Mock Binance API client"""
    client = Mock()
    
    # Mock account balance
    client.account.return_value = {
        'balances': [
            {'asset': 'USDT', 'free': '1000.00', 'locked': '0.00'},
            {'asset': 'BTC', 'free': '0.00', 'locked': '0.00'}
        ]
    }
    
    # Mock klines
    client.klines.return_value = [
        [1609459200000, '29000.00', '29500.00', '28800.00', '29200.00', '100.5',
         1609462799999, '2920000.00', 150, '50.2', '1460400.00', '0']
    ] * 50
    
    # Mock ticker price
    client.ticker_price.return_value = {'symbol': 'BTCUSDT', 'price': '30000.00'}
    
    return client


@pytest.fixture
def mock_position():
    """Mock Position object"""
    from core.models import Position
    
    return Position(
        symbol='BTCUSDT',
        side='BUY',
        entry_price=29000.0,
        quantity=0.01,
        stop_loss=28500.0,
        take_profit=30000.0,
        confluence_score=5
    )


@pytest.fixture
def mock_config(monkeypatch):
    """Mock configuration"""
    from config import config
    
    monkeypatch.setattr(config.Config, 'DEMO_MODE', True)
    monkeypatch.setattr(config.Config, 'API_KEY', 'test_key')
    monkeypatch.setattr(config.Config, 'API_SECRET', 'test_secret')
    monkeypatch.setattr(config.Config, 'TELEGRAM_ENABLED', False)
    
    return config.Config
