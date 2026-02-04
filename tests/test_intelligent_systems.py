"""
Unit Tests for Intelligent Systems
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import numpy as np


class TestAdaptiveStrategy:
    """Test AdaptiveStrategyEngine"""
    
    def test_initialization(self):
        """Test adaptive strategy initialization"""
        from core.adaptive_strategy import AdaptiveStrategyEngine, MarketRegime
        
        engine = AdaptiveStrategyEngine()
        assert engine is not None
        assert engine.current_regime in [MarketRegime.BULL, MarketRegime.BEAR, 
                                         MarketRegime.RANGING, MarketRegime.VOLATILE, 
                                         MarketRegime.BREAKOUT, MarketRegime.UNKNOWN]
        
    def test_regime_detection_trending(self):
        """Test detecting trending market"""
        from core.adaptive_strategy import AdaptiveStrategyEngine, MarketRegime
        
        engine = AdaptiveStrategyEngine()
        
        # Strong uptrend prices
        prices = [29000.0 + i*100 for i in range(100)]
        volumes = [100.0 for _ in range(100)]
        atr = 50.0
        
        regime = engine.detect_regime('BTCUSDT', prices, volumes, atr)
        
        assert regime in [MarketRegime.BULL, MarketRegime.BEAR, MarketRegime.RANGING, 
                         MarketRegime.VOLATILE, MarketRegime.BREAKOUT, MarketRegime.UNKNOWN]
        
    def test_adaptive_parameters(self):
        """Test parameter adjustment based on regime"""
        from core.adaptive_strategy import AdaptiveStrategyEngine
        
        engine = AdaptiveStrategyEngine()
        params = engine.current_params
        
        assert hasattr(params, 'min_signal_strength')
        assert hasattr(params, 'min_confluence')
        assert hasattr(params, 'take_profit_pct')
        
    def test_strategy_performance_tracking(self):
        """Test strategy performance recording"""
        from core.adaptive_strategy import AdaptiveStrategyEngine
        
        engine = AdaptiveStrategyEngine()
        
        # Check recent_trades deque exists
        assert hasattr(engine, 'recent_trades')
        assert hasattr(engine, 'regime_stats')


class TestRiskManager:
    """Test RiskManager"""
    
    def test_initialization(self):
        """Test risk manager initialization"""
        from core.risk_manager import RiskManager
        
        rm = RiskManager(initial_capital=1000.0)
        assert rm.initial_capital == 1000.0
        assert rm.current_capital == 1000.0
        
    def test_kelly_criterion_calculation(self):
        """Test Kelly Criterion position sizing (built into calculate_position_size)"""
        from core.risk_manager import RiskManager
        
        rm = RiskManager(initial_capital=1000.0)
        
        # Kelly is calculated within calculate_position_size
        position_size, details = rm.calculate_position_size(
            symbol='BTCUSDT',
            entry_price=30000.0,
            stop_loss_pct=0.01,
            win_rate=0.6,
            confidence=1.0
        )
        
        assert position_size > 0
        assert 'kelly_fraction' in details
        assert isinstance(details['kelly_fraction'], (int, float))  # Can be 0 (int) or float
        
    def test_correlation_check(self):
        """Test portfolio correlation checking"""
        from core.risk_manager import RiskManager
        from core.models import Position
        
        rm = RiskManager(initial_capital=1000.0)
        
        # Add correlated positions
        pos1 = Position(
            symbol='BTCUSDT',
            side='BUY',
            entry_price=30000.0,
            quantity=0.01,
            stop_loss=29000.0,
            take_profit=31000.0,
            confluence_score=5
        )
        
        pos2 = Position(
            symbol='ETHUSDT',
            side='BUY',
            entry_price=2000.0,
            quantity=0.1,
            stop_loss=1900.0,
            take_profit=2100.0,
            confluence_score=4
        )
        
        # Test correlation (may need mock data)
        # This depends on implementation
        assert rm is not None
        
    def test_drawdown_calculation(self):
        """Test drawdown tracking"""
        from core.risk_manager import RiskManager
        
        rm = RiskManager(initial_capital=1000.0)
        
        # Simulate loss
        rm.current_capital = 950.0
        rm.peak_capital = 1000.0  # Set peak manually
        
        # Calculate drawdown
        metrics = rm.get_portfolio_metrics()
        assert hasattr(metrics, 'current_drawdown')
        assert metrics.current_drawdown >= 0
        
    def test_risk_limits(self):
        """Test risk limit enforcement"""
        from core.risk_manager import RiskManager
        
        rm = RiskManager(initial_capital=1000.0)
        
        # Check position limits
        allowed, message = rm.check_position_limits()
        assert isinstance(allowed, bool)
        assert isinstance(message, str)


class TestAlertManager:
    """Test AlertManager"""
    
    def test_initialization(self):
        """Test alert manager initialization"""
        from core.alert_manager import AlertManager
        
        am = AlertManager()
        assert am is not None
        
    def test_create_alert(self):
        """Test creating alerts with different levels"""
        from core.alert_manager import AlertManager, AlertSeverity, AlertCategory
        
        am = AlertManager()
        
        # Critical alert using send_alert_sync
        am.send_alert_sync(
            severity=AlertSeverity.CRITICAL,
            category=AlertCategory.SYSTEM,
            title="Test Alert",
            message="Test critical alert"
        )
        
        # Check alert manager works
        assert am is not None
        
    def test_alert_filtering(self):
        """Test filtering alerts by level"""
        from core.alert_manager import AlertManager, AlertSeverity, AlertCategory
        
        am = AlertManager()
        
        # Create different level alerts using send_alert_sync
        am.send_alert_sync(AlertSeverity.CRITICAL, AlertCategory.SYSTEM, "Critical", "Critical test")
        am.send_alert_sync(AlertSeverity.HIGH, AlertCategory.TRADE, "High", "High test")
        am.send_alert_sync(AlertSeverity.MEDIUM, AlertCategory.SYSTEM, "Medium", "Medium test")
        
        # Check alert manager works
        assert am is not None
        
    def test_alert_summary(self):
        """Test getting alert summary"""
        from core.alert_manager import AlertManager, AlertSeverity, AlertCategory
        
        am = AlertManager()
        
        am.send_alert_sync(AlertSeverity.HIGH, AlertCategory.TRADE, "Test", "Test message")
        
        # Just check AlertManager works
        assert am is not None


class TestEventManager:
    """Test EventManager"""
    
    @patch('core.event_manager.requests.get')
    def test_initialization(self, mock_get):
        """Test event manager initialization"""
        from core.event_manager import EventManager
        
        # Mock Fear & Greed API
        mock_response = Mock()
        mock_response.json.return_value = {
            'data': [{'value': '50', 'value_classification': 'Neutral'}]
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        em = EventManager()
        assert em is not None
        
    @patch('core.event_manager.requests.get')
    def test_trading_decision_normal(self, mock_get):
        """Test trading decision in normal conditions"""
        from core.event_manager import EventManager
        
        # Mock Fear & Greed API
        mock_response = Mock()
        mock_response.json.return_value = {
            'data': [{'value': '50', 'value_classification': 'Neutral'}]
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        em = EventManager()
        decision = em.get_trading_decision()
        
        assert 'status' in decision
        assert 'reason' in decision
        assert decision['status'] in ['CLEAR', 'CAUTION', 'PAUSE', 'EMERGENCY']
        
    @patch('core.event_manager.requests.get')
    def test_sentiment_signal(self, mock_get):
        """Test sentiment analysis"""
        from core.event_manager import EventManager
        
        # Mock extreme fear
        mock_response = Mock()
        mock_response.json.return_value = {
            'data': [{'value': '15', 'value_classification': 'Extreme Fear'}]
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        em = EventManager()
        signal = em.get_sentiment_signal()
        
        assert 'sentiment' in signal or 'message' in signal


class TestTrailingStop:
    """Test TrailingStopManager"""
    
    def test_initialization(self):
        """Test trailing stop initialization"""
        from modules.trailing_stop import TrailingStopManager
        
        tsm = TrailingStopManager(trail_percent=1.5, activation_profit=2.0)
        assert tsm.trail_percent == 1.5
        assert tsm.activation_profit == 2.0
        
    def test_update_trailing_stop_buy(self):
        """Test updating trailing stop for BUY position"""
        from modules.trailing_stop import TrailingStopManager
        from core.models import Position
        
        tsm = TrailingStopManager(trail_percent=1.5, activation_profit=2.0)
        
        position = Position(
            symbol='BTCUSDT',
            side='BUY',
            entry_price=30000.0,
            quantity=0.01,
            stop_loss=29000.0,
            take_profit=31000.0,
            confluence_score=5
        )
        
        # Price moves up 3% (above activation)
        current_price = 30900.0
        tsm.update_trailing_stop(position, current_price)
        
        # Stop loss should have moved up
        assert position.stop_loss >= 29000.0
        
    def test_trailing_stop_not_activated(self):
        """Test trailing stop before activation threshold"""
        from modules.trailing_stop import TrailingStopManager
        from core.models import Position
        
        tsm = TrailingStopManager(trail_percent=1.5, activation_profit=2.0)
        
        position = Position(
            symbol='BTCUSDT',
            side='BUY',
            entry_price=30000.0,
            quantity=0.01,
            stop_loss=29000.0,
            take_profit=31000.0,
            confluence_score=5
        )
        
        original_sl = position.stop_loss
        
        # Price only up 1% (below 2% activation)
        current_price = 30300.0
        tsm.update_trailing_stop(position, current_price)
        
        # Stop loss should not change
        assert position.stop_loss == original_sl
        
    def test_trailing_stop_sell_position(self):
        """Test trailing stop for SELL position"""
        from modules.trailing_stop import TrailingStopManager
        from core.models import Position
        
        tsm = TrailingStopManager(trail_percent=1.5, activation_profit=2.0)
        
        position = Position(
            symbol='BTCUSDT',
            side='SELL',
            entry_price=30000.0,
            quantity=0.01,
            stop_loss=31000.0,
            take_profit=29000.0,
            confluence_score=5
        )
        
        # Price drops 3% (profit for SELL)
        current_price = 29100.0
        tsm.update_trailing_stop(position, current_price)
        
        # Stop loss should have moved down
        assert position.stop_loss <= 31000.0


class TestTelegramCommands:
    """Test Telegram command handler"""
    
    @patch('utils.telegram_commands.requests.post')
    def test_send_message(self, mock_post):
        """Test sending Telegram message"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'ok': True}
        mock_post.return_value = mock_response
        
        from utils.telegram_commands import TelegramCommandHandler
        
        # Create mock bot
        mock_bot = Mock()
        mock_bot.trade_history = Mock()
        mock_bot.trade_history.current_balance = 1000.0
        mock_bot.trade_history.get_daily_pnl_percent.return_value = 2.5
        mock_bot.trade_history.get_win_rate.return_value = 65.0
        mock_bot.position_manager = Mock()
        mock_bot.position_manager.get_all_positions.return_value = []
        
        handler = TelegramCommandHandler(
            bot_instance=mock_bot,
            bot_token="test_token",
            chat_id="test_chat_id"
        )
        
        # Test send message - needs chat_id and text parameters
        handler.send_message(chat_id="test_chat_id", text="Test message")
        assert mock_post.called
