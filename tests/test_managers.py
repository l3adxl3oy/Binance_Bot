"""
Unit Tests for Manager classes
"""
import pytest
from managers.position_manager import PositionManager
from managers.symbol_manager import SymbolManager
from core.models import Position


class TestPositionManager:
    """Test PositionManager"""
    
    def test_initialization(self):
        """Test position manager initialization"""
        manager = PositionManager(max_total_positions=10, max_per_symbol=3)
        
        assert manager.max_total_positions == 10
        assert manager.max_per_symbol == 3
        assert len(manager.positions) == 0
        
    def test_add_position(self):
        """Test adding a position"""
        manager = PositionManager(max_total_positions=10, max_per_symbol=3)
        
        position = Position(
            symbol='BTCUSDT',
            side='BUY',
            entry_price=30000.0,
            quantity=0.01,
            stop_loss=29000.0,
            take_profit=31000.0,
            confluence_score=5
        )
        
        result = manager.add_position(position)
        assert result is True
        assert len(manager.get_all_positions()) == 1
        
    def test_max_positions_limit(self):
        """Test max positions limit"""
        manager = PositionManager(max_total_positions=2, max_per_symbol=2)
        
        # Add 2 positions (max)
        for i in range(2):
            position = Position(
                symbol=f'BTC{i}USDT',
                side='BUY',
                entry_price=30000.0,
                quantity=0.01,
                stop_loss=29000.0,
                take_profit=31000.0,
                confluence_score=5
            )
            manager.add_position(position)
        
        # Try to add 3rd position (should fail)
        position3 = Position(
            symbol='ETHUSDT',
            side='BUY',
            entry_price=2000.0,
            quantity=0.1,
            stop_loss=1900.0,
            take_profit=2100.0,
            confluence_score=4
        )
        result = manager.add_position(position3)
        assert result is False
        assert len(manager.get_all_positions()) == 2
        
    def test_remove_position(self):
        """Test removing a position"""
        manager = PositionManager(max_total_positions=10, max_per_symbol=3)
        
        position = Position(
            symbol='BTCUSDT',
            side='BUY',
            entry_price=30000.0,
            quantity=0.01,
            stop_loss=29000.0,
            take_profit=31000.0,
            confluence_score=5
        )
        
        manager.add_position(position)
        position_id = position.position_id
        
        result = manager.remove_position(position_id)
        # remove_position returns the Position object or None
        assert result is not None
        assert len(manager.get_all_positions()) == 0
        
    def test_get_symbol_position_count(self):
        """Test getting position count per symbol"""
        manager = PositionManager(max_total_positions=10, max_per_symbol=3)
        
        # Add 2 BTC positions
        for i in range(2):
            position = Position(
                symbol='BTCUSDT',
                side='BUY',
                entry_price=30000.0 + i*100,
                quantity=0.01,
                stop_loss=29000.0,
                take_profit=31000.0,
                confluence_score=5
            )
            manager.add_position(position)
        
        count = manager.get_symbol_position_count('BTCUSDT')
        assert count == 2


class TestSymbolManager:
    """Test SymbolManager"""
    
    def test_initialization(self):
        """Test symbol manager initialization"""
        symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
        manager = SymbolManager(
            symbol_pool=symbols,
            max_active=2,
            rotation_interval=300
        )
        
        assert len(manager.symbol_pool) == 3
        # Check that active symbols are limited
        active = manager.get_active_symbols()
        assert len(active) <= 2
        
    def test_get_active_symbols(self):
        """Test getting active symbols"""
        symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT']
        manager = SymbolManager(
            symbol_pool=symbols,
            max_active=2,
            rotation_interval=300
        )
        
        active = manager.get_active_symbols()
        assert len(active) <= 2
        assert all(s in symbols for s in active)
        
    def test_should_rotate(self):
        """Test rotation timing"""
        symbols = ['BTCUSDT', 'ETHUSDT']
        manager = SymbolManager(
            symbol_pool=symbols,
            max_active=2,
            rotation_interval=1  # 1 second for testing
        )
        
        # Initially should not rotate
        assert manager.should_rotate() is False
        
        # After waiting, should rotate
        import time
        time.sleep(1.1)
        assert manager.should_rotate() is True
