"""
Database Models for Trading Bot
PostgreSQL schema definitions using SQLAlchemy
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class OrderSide(str, enum.Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderStatus(str, enum.Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


class BotType(str, enum.Enum):
    AGGRESSIVE = "aggressive"
    SCALPING = "scalping"


# ==================== USER MODEL ====================
class User(Base):
    """User accounts for multi-user support"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Binance credentials (encrypted)
    api_key_encrypted = Column(Text, nullable=True)
    api_secret_encrypted = Column(Text, nullable=True)
    
    # Settings
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    trades = relationship("Trade", back_populates="user", cascade="all, delete-orphan")
    bot_configs = relationship("BotConfig", back_populates="user", cascade="all, delete-orphan")


# ==================== BOT CONFIG MODEL ====================
class BotConfig(Base):
    """Bot configuration per user (stores complete YAML config)"""
    __tablename__ = "bot_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Config identification
    name = Column(String(100), nullable=False)  # User-friendly name (changed from config_name)
    config_yaml = Column(Text, nullable=False)  # Complete YAML config
    config_version = Column(String(10), default="2.0")  # Config schema version
    
    # Quick reference fields (extracted from YAML for filtering)
    strategy_name = Column(String(100), nullable=True)
    bot_type = Column(String(50), nullable=True)  # SCALPING or AGGRESSIVE_RECOVERY
    
    # Status
    is_active = Column(Boolean, default=False)  # Currently selected config
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="bot_configs")


# ==================== TRADE MODEL ====================
class Trade(Base):
    """Individual trade records"""
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Trade details
    symbol = Column(String(20), nullable=False, index=True)
    side = Column(Enum(OrderSide), nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.OPEN)
    
    # Binance order info
    order_id = Column(String(50), nullable=True)
    client_order_id = Column(String(50), nullable=True)
    
    # Prices and quantities
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=True)
    quantity = Column(Float, nullable=False)
    
    # Profit/Loss
    profit_loss_usd = Column(Float, default=0.0)
    profit_loss_percent = Column(Float, default=0.0)
    
    # Strategy info
    strategy = Column(String(50), nullable=True)  # e.g., "aggressive", "scalping"
    signal_strength = Column(Float, nullable=True)
    
    # Timestamps
    entry_time = Column(DateTime, default=datetime.utcnow, index=True)
    exit_time = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="trades")


# ==================== DAILY PERFORMANCE MODEL ====================
class DailyPerformance(Base):
    """Daily trading performance summary per user"""
    __tablename__ = "daily_performance"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    date = Column(DateTime, nullable=False, index=True)
    
    # Statistics
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    
    # P&L
    total_profit_loss = Column(Float, default=0.0)
    max_drawdown = Column(Float, default=0.0)
    
    # Win rate
    win_rate = Column(Float, default=0.0)
    
    # Best/Worst trades
    best_trade_profit = Column(Float, default=0.0)
    worst_trade_loss = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)


# ==================== ALERT/LOG MODEL ====================
class Alert(Base):
    """System alerts and notifications per user"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Alert details
    level = Column(String(20), nullable=False)  # CRITICAL, HIGH, MEDIUM, LOW
    category = Column(String(50), nullable=False)  # TRADE, SYSTEM, ERROR, etc.
    message = Column(Text, nullable=False)
    
    # Status
    is_read = Column(Boolean, default=False)
    is_sent_telegram = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


# ==================== MARKET DATA CACHE ====================
class MarketDataCache(Base):
    """Cache for market data to reduce API calls"""
    __tablename__ = "market_data_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False)
    
    # OHLCV data
    timestamp = Column(DateTime, nullable=False, index=True)
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    
    # Indicators (pre-calculated)
    rsi = Column(Float, nullable=True)
    macd = Column(Float, nullable=True)
    bb_upper = Column(Float, nullable=True)
    bb_lower = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
