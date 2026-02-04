"""
Config Schema Validation using Pydantic
Ensures all configs meet required structure and types
"""

from pydantic import BaseModel, Field, validator
from typing import List, Literal, Optional
from enum import Enum


class BotType(str, Enum):
    """Bot type enumeration"""
    SCALPING = "SCALPING"
    AGGRESSIVE_RECOVERY = "AGGRESSIVE_RECOVERY"


class RiskManagement(BaseModel):
    """Risk management parameters (nested structure for v2.0+)"""
    atr_sl_multiplier: float = Field(ge=0.5, le=3.0, description="ATR multiplier for stop loss")
    atr_tp_multiplier: float = Field(ge=1.0, le=10.0, description="ATR multiplier for take profit")
    max_loss_per_trade: float = Field(ge=0.05, le=1.0, description="Max loss per trade (%)")
    daily_profit_target: float = Field(ge=0.5, le=20.0, description="Daily profit target (%)")
    max_daily_loss: float = Field(ge=1.0, le=20.0, description="Max daily loss (%)")


class ConfigSchema(BaseModel):
    """
    Config Schema v2.0
    All configs must conform to this schema
    """
    # Version tracking
    config_version: str = Field(default="2.0", description="Config version")
    
    # Basic info
    strategy_name: str = Field(min_length=3, max_length=100, description="Strategy name")
    bot_type: BotType = Field(description="Bot type (SCALPING or AGGRESSIVE_RECOVERY)")
    
    # Signal configuration
    min_signal_strength: float = Field(ge=0.0, le=5.0, description="Minimum signal strength (0-5)")
    max_positions: int = Field(ge=1, le=20, description="Maximum concurrent positions")
    max_active_symbols: int = Field(ge=1, le=12, description="Number of symbols to monitor")
    position_size_percent: float = Field(ge=0.1, le=5.0, description="Position size (% of balance)")
    
    # Risk management (nested structure)
    risk_management: RiskManagement
    
    # Trading features
    enable_martingale: bool = Field(default=False, description="Enable martingale/averaging")
    martingale_multiplier: Optional[float] = Field(default=1.3, ge=1.0, le=3.0, description="Martingale multiplier")
    martingale_max_levels: Optional[int] = Field(default=2, ge=1, le=5, description="Max martingale levels")
    trailing_stop_enabled: bool = Field(default=True, description="Enable trailing stop")
    partial_take_profit: bool = Field(default=True, description="Enable partial TP")
    progressive_recovery: bool = Field(default=False, description="Aggressive recovery mode")
    
    # Advanced features (v2.0+)
    ai_score_weight: float = Field(default=0.3, ge=0.0, le=1.0, description="AI sentiment weight")
    use_ml_prediction: bool = Field(default=False, description="Use ML prediction")
    enable_event_manager: bool = Field(default=True, description="Economic calendar")
    enable_advanced_risk: bool = Field(default=True, description="Advanced risk management")
    enable_adaptive_strategy: bool = Field(default=True, description="Adaptive strategy")
    
    # Time management
    check_interval: int = Field(default=20, ge=5, le=120, description="Check interval (seconds)")
    time_stop_base: int = Field(default=150, ge=60, le=600, description="Time stop base (seconds)")
    
    # Optional position sizing adjustments
    win_streak_multiplier: Optional[float] = Field(default=1.0, ge=1.0, le=2.0)
    loss_streak_multiplier: Optional[float] = Field(default=1.0, ge=0.3, le=1.0)
    max_drawdown_percent: Optional[float] = Field(default=15.0, ge=5.0, le=30.0)
    
    # Symbols
    symbols: List[str] = Field(min_items=1, max_items=12, description="Trading symbols")
    
    @validator('strategy_name')
    def validate_strategy_name(cls, v):
        """Validate strategy name"""
        if len(v.strip()) < 3:
            raise ValueError("Strategy name must be at least 3 characters")
        return v.strip()
    
    @validator('symbols')
    def validate_symbols(cls, v):
        """Validate symbol format"""
        for symbol in v:
            if not symbol.endswith('USDT'):
                raise ValueError(f"Symbol {symbol} must end with USDT")
        return v
    
    class Config:
        use_enum_values = True


class ConfigSchemaV1_5(BaseModel):
    """Config Schema v1.5 (for migration testing)"""
    config_version: str = "1.5"
    strategy_name: str
    bot_type: str
    min_signal_strength: float
    max_positions: int
    # Flat structure (no nested risk_management)
    atr_sl_multiplier: float
    atr_tp_multiplier: float
    max_loss_per_trade: float
    daily_profit_target: float
    max_daily_loss: float
    enable_martingale: bool = False
    trailing_stop_enabled: bool = True


class ConfigSchemaV1_0(BaseModel):
    """Config Schema v1.0 (legacy, for migration testing)"""
    strategy_name: str
    bot_type: str
    min_signal_strength: float
    max_positions: int
    stop_loss_pct: float  # Old naming
    take_profit_pct: float  # Old naming
