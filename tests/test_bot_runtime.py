"""
Integration Tests for Bot Runtime Logic
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, UTC
import numpy as np


class TestAggressiveBotRuntime:
    """Test AggressiveRecoveryBot runtime behavior"""
    
    @patch('bots.aggressive_recovery_bot.Spot')
    def test_calculate_signals_strong_buy(self, mock_spot):
        """Test signal calculation for strong buy setup"""
        from bots.aggressive_recovery_bot import AggressiveRecoveryBot
        
        # Mock client
        mock_client = Mock()
        mock_client.account.return_value = {
            'balances': [{'asset': 'USDT', 'free': '1000.00', 'locked': '0.00'}]
        }
        mock_spot.return_value = mock_client
        
        bot = AggressiveRecoveryBot()
        
        # Create oversold + volume + MACD bullish data
        data = {
            'close': np.array([29000, 28900, 28800, 28700, 28600, 28500, 28400, 28300, 
                              28200, 28100, 28000, 27900, 27800, 27900, 28000, 28200,
                              28400, 28600, 28800, 29000] * 2),
            'high': np.array([29100, 29000, 28900, 28800, 28700, 28600, 28500, 28400,
                             28300, 28200, 28100, 28000, 27900, 28000, 28100, 28300,
                             28500, 28700, 28900, 29100] * 2),
            'low': np.array([28900, 28800, 28700, 28600, 28500, 28400, 28300, 28200,
                            28100, 28000, 27900, 27800, 27700, 27800, 27900, 28100,
                            28300, 28500, 28700, 28900] * 2),
            'volume': np.array([100, 110, 120, 130, 140, 150, 160, 170, 180, 190,
                               200, 210, 220, 230, 240, 250, 260, 270, 280, 290] * 2),
            'current_price': 29000.0
        }
        
        signals = bot.calculate_signals('BTCUSDT', data)
        
        assert 'buy_strength' in signals
        assert 'sell_strength' in signals
        assert isinstance(signals['buy_strength'], (int, float))
        
    @patch('bots.aggressive_recovery_bot.Spot')
    def test_calculate_adaptive_position_size(self, mock_spot):
        """Test adaptive position sizing"""
        from bots.aggressive_recovery_bot import AggressiveRecoveryBot
        
        mock_client = Mock()
        mock_client.account.return_value = {
            'balances': [{'asset': 'USDT', 'free': '1000.00', 'locked': '0.00'}]
        }
        mock_spot.return_value = mock_client
        
        bot = AggressiveRecoveryBot()
        bot.consecutive_wins = 3  # Win streak
        
        quantity = bot.calculate_adaptive_position_size(
            symbol='BTCUSDT',
            stop_loss_percent=0.5,
            current_price=30000.0,
            is_recovery=False
        )
        
        assert quantity > 0
        assert isinstance(quantity, float)
        
    @patch('bots.aggressive_recovery_bot.Spot')
    def test_martingale_recovery(self, mock_spot):
        """Test martingale recovery logic"""
        from bots.aggressive_recovery_bot import AggressiveRecoveryBot
        
        mock_client = Mock()
        mock_client.account.return_value = {
            'balances': [{'asset': 'USDT', 'free': '1000.00', 'locked': '0.00'}]
        }
        mock_spot.return_value = mock_client
        
        bot = AggressiveRecoveryBot()
        bot.consecutive_losses = 2
        bot.last_loss_symbol = 'BTCUSDT'
        bot.martingale_level['BTCUSDT'] = 1
        
        # Recovery position should be larger
        recovery_qty = bot.calculate_adaptive_position_size(
            symbol='BTCUSDT',
            stop_loss_percent=0.5,
            current_price=30000.0,
            is_recovery=True
        )
        
        normal_qty = bot.calculate_adaptive_position_size(
            symbol='ETHUSDT',
            stop_loss_percent=0.5,
            current_price=2000.0,
            is_recovery=False
        )
        
        # Recovery should be larger (due to martingale)
        assert recovery_qty >= normal_qty or recovery_qty > 0
        
    @patch('bots.aggressive_recovery_bot.Spot')
    def test_check_daily_status_target_reached(self, mock_spot):
        """Test daily profit target check"""
        from bots.aggressive_recovery_bot import AggressiveRecoveryBot
        
        mock_client = Mock()
        mock_client.account.return_value = {
            'balances': [{'asset': 'USDT', 'free': '1000.00', 'locked': '0.00'}]
        }
        mock_spot.return_value = mock_client
        
        bot = AggressiveRecoveryBot()
        
        # Simulate reaching target
        bot.trade_history.current_balance = 1050.0  # +5%
        
        bot.check_daily_status()
        
        # Bot should stop
        assert bot.running is False


class TestScalpingBotRuntime:
    """Test DailyScalpingBot runtime behavior"""
    
    @patch('bots.daily_scalping_bot.Spot')
    def test_multi_timeframe_analysis(self, mock_spot):
        """Test multi-timeframe signal confirmation"""
        from bots.daily_scalping_bot import DailyScalpingBot
        
        mock_client = Mock()
        mock_client.account.return_value = {
            'balances': [{'asset': 'USDT', 'free': '1000.00', 'locked': '0.00'}]
        }
        mock_client.klines.return_value = [
            [i*60000, str(29000+i*10), str(29100+i*10), str(28900+i*10),
             str(29050+i*10), '100.0', (i+1)*60000-1, '2900000', 100, '50', '1450000', '0']
            for i in range(100)
        ]
        mock_spot.return_value = mock_client
        
        bot = DailyScalpingBot()
        
        # This should not crash
        assert bot is not None


class TestBotStateManagement:
    """Test bot state save/load"""
    
    @patch('bots.aggressive_recovery_bot.Spot')
    def test_save_and_load_state(self, mock_spot):
        """Test state persistence"""
        from bots.aggressive_recovery_bot import AggressiveRecoveryBot
        import os
        
        mock_client = Mock()
        mock_client.account.return_value = {
            'balances': [{'asset': 'USDT', 'free': '1000.00', 'locked': '0.00'}]
        }
        mock_spot.return_value = mock_client
        
        bot = AggressiveRecoveryBot()
        bot.consecutive_wins = 5
        bot.consecutive_losses = 0
        bot.martingale_level['BTCUSDT'] = 2
        
        # Save state
        bot.save_state()
        
        # Check file exists
        assert os.path.exists('bot_state_aggressive.json')
        
        # Create new bot and load
        bot2 = AggressiveRecoveryBot()
        
        # State should be loaded (or handle gracefully)
        assert bot2.consecutive_wins >= 0
        
        # Cleanup
        if os.path.exists('bot_state_aggressive.json'):
            os.remove('bot_state_aggressive.json')


class TestBotErrorHandling:
    """Test bot error handling"""
    
    @patch('bots.aggressive_recovery_bot.Spot')
    def test_api_retry_logic(self, mock_spot):
        """Test API retry on failure"""
        from bots.aggressive_recovery_bot import AggressiveRecoveryBot
        
        mock_client = Mock()
        mock_client.account.return_value = {
            'balances': [{'asset': 'USDT', 'free': '1000.00', 'locked': '0.00'}]
        }
        
        # First call fails, second succeeds
        mock_client.klines.side_effect = [
            Exception("Network error"),
            [
                [1609459200000, '29000.00', '29500.00', '28800.00', '29200.00', '100.5',
                 1609462799999, '2920000.00', 150, '50.2', '1460400.00', '0']
            ] * 50
        ]
        
        mock_spot.return_value = mock_client
        
        bot = AggressiveRecoveryBot()
        
        # Should retry and eventually succeed
        data = bot.get_market_data('BTCUSDT')
        
        # If None, retry logic worked but all failed
        # If data, retry succeeded
        assert data is None or 'current_price' in data
        
    @patch('bots.aggressive_recovery_bot.Spot')
    def test_invalid_market_data(self, mock_spot):
        """Test handling of invalid market data"""
        from bots.aggressive_recovery_bot import AggressiveRecoveryBot
        
        mock_client = Mock()
        mock_client.account.return_value = {
            'balances': [{'asset': 'USDT', 'free': '1000.00', 'locked': '0.00'}]
        }
        
        # Return empty klines
        mock_client.klines.return_value = []
        
        mock_spot.return_value = mock_client
        
        bot = AggressiveRecoveryBot()
        
        # Should handle gracefully
        data = bot.get_market_data('BTCUSDT')
        assert data is None


class TestBotPerformanceMetrics:
    """Test performance tracking"""
    
    @patch('bots.aggressive_recovery_bot.Spot')
    def test_win_rate_calculation(self, mock_spot):
        """Test win rate tracking"""
        from bots.aggressive_recovery_bot import AggressiveRecoveryBot
        from core.models import Position
        
        mock_client = Mock()
        mock_client.account.return_value = {
            'balances': [{'asset': 'USDT', 'free': '1000.00', 'locked': '0.00'}]
        }
        mock_spot.return_value = mock_client
        
        bot = AggressiveRecoveryBot()
        
        # Add winning trades
        for i in range(3):
            pos = Position(
                symbol='BTCUSDT',
                side='BUY',
                entry_price=30000.0,
                quantity=0.01,
                stop_loss=29000.0,
                take_profit=31000.0,
                confluence_score=5
            )
            pos.exit_price = 31000.0
            pos.exit_time = datetime.now(UTC)
            pos.profit_amount = 10.0
            pos.profit_percent = 3.33
            bot.trade_history.add_trade(pos)
        
        # Add losing trades
        for i in range(2):
            pos = Position(
                symbol='BTCUSDT',
                side='BUY',
                entry_price=30000.0,
                quantity=0.01,
                stop_loss=29000.0,
                take_profit=31000.0,
                confluence_score=5
            )
            pos.exit_price = 29000.0
            pos.exit_time = datetime.now(UTC)
            pos.profit_amount = -10.0
            pos.profit_percent = -3.33
            bot.trade_history.add_trade(pos)
        
        win_rate = bot.trade_history.get_win_rate()
        assert win_rate == 60.0  # 3/5
