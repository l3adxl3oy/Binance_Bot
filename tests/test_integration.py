"""
Integration Tests - Test complete workflows
"""
import pytest
from unittest.mock import Mock, patch
import numpy as np
from datetime import datetime, UTC


class TestTradingWorkflow:
    """Test complete trading workflow"""
    
    @patch('bots.aggressive_recovery_bot.Spot')
    def test_bot_initialization(self, mock_spot):
        """Test bot can initialize properly"""
        # Mock Binance client
        mock_client = Mock()
        mock_client.account.return_value = {
            'balances': [
                {'asset': 'USDT', 'free': '1000.00', 'locked': '0.00'}
            ]
        }
        mock_spot.return_value = mock_client
        
        from bots.aggressive_recovery_bot import AggressiveRecoveryBot
        
        bot = AggressiveRecoveryBot()
        assert bot is not None
        assert bot.trade_history.daily_start_balance > 0
        
    @patch('bots.aggressive_recovery_bot.Spot')
    def test_signal_generation(self, mock_spot):
        """Test signal generation from market data"""
        # Mock Binance client
        mock_client = Mock()
        mock_client.account.return_value = {
            'balances': [
                {'asset': 'USDT', 'free': '1000.00', 'locked': '0.00'}
            ]
        }
        mock_client.klines.return_value = [
            [1609459200000, '29000.00', '29500.00', '28800.00', '29200.00', '100.5',
             1609462799999, '2920000.00', 150, '50.2', '1460400.00', '0']
        ] * 50
        
        mock_spot.return_value = mock_client
        
        from bots.aggressive_recovery_bot import AggressiveRecoveryBot
        
        bot = AggressiveRecoveryBot()
        
        # Get market data
        data = bot.get_market_data('BTCUSDT')
        assert data is not None
        assert 'current_price' in data
        
        # Calculate signals
        signals = bot.calculate_signals('BTCUSDT', data)
        assert 'buy_strength' in signals
        assert 'sell_strength' in signals


class TestDatabaseIntegration:
    """Test database operations"""
    
    def test_database_initialization(self):
        """Test database can be initialized"""
        from database.db import init_db, SessionLocal
        
        try:
            init_db()
            session = SessionLocal()
            session.close()
        except Exception as e:
            pytest.fail(f"Database initialization failed: {e}")
            
    def test_create_user(self):
        """Test creating a user in database"""
        from database.db import SessionLocal
        from database.models import User
        
        session = SessionLocal()
        
        try:
            user = User(
                username="testuser",
                email="test@example.com",
                hashed_password="hashed_password"
            )
            session.add(user)
            session.commit()
            
            # Query user back
            retrieved = session.query(User).filter_by(username="testuser").first()
            assert retrieved is not None
            assert retrieved.email == "test@example.com"
            
            # Cleanup
            session.delete(retrieved)
            session.commit()
            
        finally:
            session.close()
            
    def test_create_trade_record(self):
        """Test creating trade records"""
        from database.db import SessionLocal
        from database.models import User, Trade
        
        session = SessionLocal()
        
        try:
            # Create user first
            user = User(
                username="trader",
                email="trader@example.com",
                hashed_password="hashed"
            )
            session.add(user)
            session.commit()
            
            # Create trade
            trade = Trade(
                user_id=user.id,
                symbol="BTCUSDT",
                side="BUY",
                entry_price=30000.0,
                quantity=0.01,
                profit_loss_usd=100.0,
                profit_loss_percent=3.33,
                status="CLOSED"
            )
            session.add(trade)
            session.commit()
            
            # Verify
            retrieved = session.query(Trade).filter_by(symbol="BTCUSDT").first()
            assert retrieved is not None
            assert retrieved.profit_loss_usd == 100.0
            
            # Cleanup
            session.delete(trade)
            session.delete(user)
            session.commit()
            
        finally:
            session.close()


class TestEndToEnd:
    """End-to-end integration tests"""
    
    @patch('bots.aggressive_recovery_bot.Spot')
    def test_complete_trade_cycle(self, mock_spot):
        """Test complete trade cycle: entry -> monitoring -> exit"""
        # Mock Binance client
        mock_client = Mock()
        mock_client.account.return_value = {
            'balances': [
                {'asset': 'USDT', 'free': '1000.00', 'locked': '0.00'}
            ]
        }
        
        # Mock price data showing bullish trend
        mock_client.klines.return_value = [
            [i*60000, str(29000+i*10), str(29100+i*10), str(28900+i*10), 
             str(29050+i*10), '100.0', (i+1)*60000-1, '2900000', 100, '50', '1450000', '0']
            for i in range(50)
        ]
        
        mock_spot.return_value = mock_client
        
        from bots.aggressive_recovery_bot import AggressiveRecoveryBot
        from core.models import Position
        
        bot = AggressiveRecoveryBot()
        
        # Get market data
        data = bot.get_market_data('BTCUSDT')
        assert data is not None
        
        # Generate signals
        signals = bot.calculate_signals('BTCUSDT', data)
        
        # If strong buy signal, create position
        if signals['buy_strength'] > 3:
            position = Position(
                symbol='BTCUSDT',
                side='BUY',
                entry_price=signals['current_price'],
                quantity=0.01,
                stop_loss=signals['current_price'] * 0.99,
                take_profit=signals['current_price'] * 1.02,
                confluence_score=int(signals['buy_strength'])
            )
            
            # Add position
            added = bot.position_manager.add_position(position)
            assert added is True
            
            # Simulate price reaching TP
            exit_price = position.take_profit
            position.exit_price = exit_price
            position.exit_time = datetime.now(UTC)
            
            # Calculate P&L
            profit_pct = ((exit_price - position.entry_price) / position.entry_price) * 100
            assert profit_pct > 0  # Should be profitable
            
            # Close position
            bot.close_position(position, exit_price, "TP ✅")
            
            # Verify trade was recorded
            assert len(bot.trade_history.trades) == 1
            assert bot.trade_history.current_balance > bot.trade_history.starting_balance
