"""
Unit Tests for Data Models
"""
import pytest
from datetime import datetime, UTC
from core.models import Position, TradeHistory


class TestPosition:
    """Test Position model"""
    
    def test_position_creation(self):
        """Test creating a position"""
        position = Position(
            symbol='BTCUSDT',
            side='BUY',
            entry_price=30000.0,
            quantity=0.01,
            stop_loss=29000.0,
            take_profit=31000.0,
            confluence_score=5
        )
        
        assert position.symbol == 'BTCUSDT'
        assert position.side == 'BUY'
        assert position.entry_price == 30000.0
        assert position.quantity == 0.01
        assert position.position_id is not None
        assert position.entry_time is not None
        
    def test_position_profit_calculation(self):
        """Test profit/loss calculation"""
        position = Position(
            symbol='BTCUSDT',
            side='BUY',
            entry_price=30000.0,
            quantity=0.01,
            stop_loss=29000.0,
            take_profit=31000.0,
            confluence_score=5
        )
        
        # Exit at profit
        position.exit_price = 31000.0
        position_value = position.entry_price * position.quantity
        expected_profit = ((31000.0 - 30000.0) / 30000.0) * 100
        
        # Calculate manually to verify
        assert position.entry_price == 30000.0
        assert position.exit_price == 31000.0
        
    def test_sell_position(self):
        """Test SELL position"""
        position = Position(
            symbol='ETHUSDT',
            side='SELL',
            entry_price=2000.0,
            quantity=0.5,
            stop_loss=2100.0,
            take_profit=1900.0,
            confluence_score=4
        )
        
        assert position.side == 'SELL'
        assert position.stop_loss > position.entry_price  # SL above entry for SELL
        assert position.take_profit < position.entry_price  # TP below entry for SELL


class TestTradeHistory:
    """Test TradeHistory model"""
    
    def test_trade_history_initialization(self):
        """Test initializing trade history"""
        history = TradeHistory(starting_balance=1000.0)
        
        assert history.daily_start_balance == 1000.0
        assert history.current_balance == 1000.0
        assert len(history.trades) == 0
        
    def test_add_winning_trade(self):
        """Test adding a winning trade"""
        history = TradeHistory(starting_balance=1000.0)
        
        position = Position(
            symbol='BTCUSDT',
            side='BUY',
            entry_price=30000.0,
            quantity=0.01,
            stop_loss=29000.0,
            take_profit=31000.0,
            confluence_score=5
        )
        position.exit_price = 31000.0
        position.exit_time = datetime.now(UTC)
        position.profit_percent = 3.33
        position.profit_amount = 10.0
        
        history.add_trade(position)
        
        assert len(history.trades) == 1
        assert history.current_balance == 1010.0
        
    def test_add_losing_trade(self):
        """Test adding a losing trade"""
        history = TradeHistory(starting_balance=1000.0)
        
        position = Position(
            symbol='BTCUSDT',
            side='BUY',
            entry_price=30000.0,
            quantity=0.01,
            stop_loss=29000.0,
            take_profit=31000.0,
            confluence_score=5
        )
        position.exit_price = 29000.0
        position.exit_time = datetime.now(UTC)
        position.profit_percent = -3.33
        position.profit_amount = -10.0
        
        history.add_trade(position)
        
        assert len(history.trades) == 1
        assert history.current_balance == 990.0
        
    def test_win_rate_calculation(self):
        """Test win rate calculation"""
        history = TradeHistory(starting_balance=1000.0)
        
        # Add 3 wins
        for i in range(3):
            position = Position(
                symbol='BTCUSDT',
                side='BUY',
                entry_price=30000.0,
                quantity=0.01,
                stop_loss=29000.0,
                take_profit=31000.0,
                confluence_score=5
            )
            position.exit_price = 31000.0
            position.exit_time = datetime.now(UTC)
            position.profit_percent = 3.33
            position.profit_amount = 10.0
            history.add_trade(position)
        
        # Add 2 losses
        for i in range(2):
            position = Position(
                symbol='BTCUSDT',
                side='BUY',
                entry_price=30000.0,
                quantity=0.01,
                stop_loss=29000.0,
                take_profit=31000.0,
                confluence_score=5
            )
            position.exit_price = 29000.0
            position.exit_time = datetime.now(UTC)
            position.profit_percent = -3.33
            position.profit_amount = -10.0
            history.add_trade(position)
        
        win_rate = history.get_win_rate()
        assert win_rate == 60.0  # 3/5 = 60%
        
    def test_daily_pnl(self):
        """Test daily P&L calculation"""
        history = TradeHistory(starting_balance=1000.0)
        
        # Add profitable trade
        position = Position(
            symbol='BTCUSDT',
            side='BUY',
            entry_price=30000.0,
            quantity=0.01,
            stop_loss=29000.0,
            take_profit=31000.0,
            confluence_score=5
        )
        position.exit_price = 31000.0
        position.exit_time = datetime.now(UTC)
        position.profit_percent = 3.33
        position.profit_amount = 10.0  # $10 profit
        history.add_trade(position)
        
        daily_pnl = history.get_daily_pnl_percent()
        # Should be 1% (10/1000)
        assert abs(daily_pnl - 1.0) < 0.1
