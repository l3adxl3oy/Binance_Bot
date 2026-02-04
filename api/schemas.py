"""
Pydantic Models for API Requests and Responses
Used for FastAPI validation and serialization
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime


# ==================== AUTH MODELS ====================

class UserSignup(BaseModel):
    """User signup request"""
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6, max_length=100)
    
    @validator('username')
    def validate_username(cls, v):
        if not v.isalnum() and '_' not in v:
            raise ValueError('Username must be alphanumeric or contain underscores')
        return v.lower()


class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
    email: str


class UserProfile(BaseModel):
    """User profile response"""
    id: int
    username: str
    email: str
    is_active: bool
    is_verified: bool
    has_api_keys: bool
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True


class APIKeysUpdate(BaseModel):
    """Update Binance API keys"""
    api_key: str = Field(min_length=10)
    api_secret: str = Field(min_length=10)
    use_testnet: bool = Field(default=True)


# ==================== CONFIG MODELS ====================

class ConfigCreate(BaseModel):
    """Create new config"""
    config_name: str = Field(min_length=3, max_length=100)
    config_yaml: str = Field(min_length=10)


class ConfigUpdate(BaseModel):
    """Update existing config"""
    config_name: Optional[str] = None
    config_yaml: Optional[str] = None


class ConfigResponse(BaseModel):
    """Config response"""
    id: int
    user_id: int
    config_name: str
    config_version: str
    strategy_name: Optional[str]
    bot_type: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_used_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ConfigDetail(ConfigResponse):
    """Detailed config with YAML content"""
    config_yaml: str


class TemplateInfo(BaseModel):
    """Built-in template info"""
    name: str
    file: str
    strategy_name: str
    bot_type: str
    version: str
    description: Optional[str] = None


# ==================== BOT MODELS ====================

class BotStart(BaseModel):
    """Start bot request"""
    config_id: Optional[int] = None  # Use saved config
    config_yaml: Optional[str] = None  # Or provide YAML directly
    demo_mode: bool = Field(default=True)


class BotStatus(BaseModel):
    """Bot status response"""
    is_running: bool
    config_name: Optional[str]
    demo_mode: bool
    uptime_seconds: Optional[int]
    current_balance: Optional[float]
    daily_pnl: Optional[float]
    active_positions: int
    total_trades_today: int


# ==================== TRADE MODELS ====================

class TradeResponse(BaseModel):
    """Trade response"""
    id: int
    symbol: str
    side: str
    status: str
    entry_price: float
    exit_price: Optional[float]
    quantity: float
    profit_loss_usd: float
    profit_loss_percent: float
    strategy: Optional[str]
    signal_strength: Optional[float]
    entry_time: datetime
    exit_time: Optional[datetime]
    
    class Config:
        from_attributes = True


class TradeFilter(BaseModel):
    """Trade filtering parameters"""
    symbol: Optional[str] = None
    status: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    limit: int = Field(default=100, le=1000)
    offset: int = Field(default=0, ge=0)


# ==================== PERFORMANCE MODELS ====================

class PerformanceResponse(BaseModel):
    """Daily performance response"""
    date: datetime
    total_trades: int
    winning_trades: int
    losing_trades: int
    total_profit_loss: float
    max_drawdown: float
    win_rate: float
    best_trade_profit: float
    worst_trade_loss: float
    
    class Config:
        from_attributes = True


# ==================== GENERIC MODELS ====================

class SuccessResponse(BaseModel):
    """Generic success response"""
    success: bool = True
    message: str
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    """Generic error response"""
    success: bool = False
    error: str
    details: Optional[str] = None
