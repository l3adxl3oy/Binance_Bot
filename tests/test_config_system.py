"""
Test Config System
Run: pytest tests/test_config_system.py -v
"""

import pytest
import yaml
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.config_loader import ConfigLoader
from config.migrations import ConfigMigration
from config.schema import ConfigSchema
from pydantic import ValidationError


class TestConfigTemplates:
    """Test built-in config templates"""
    
    def test_load_safe_template(self):
        """Test loading safe template"""
        config = ConfigLoader.load_template('safe')
        
        assert config['config_version'] == '2.0'
        assert config['strategy_name'] == 'Safe Conservative'
        assert config['bot_type'] == 'SCALPING'
        assert config['min_signal_strength'] == 4.5
        assert config['enable_martingale'] is False
    
    def test_load_aggressive_template(self):
        """Test loading aggressive template"""
        config = ConfigLoader.load_template('aggressive')
        
        assert config['config_version'] == '2.0'
        assert config['strategy_name'] == 'Aggressive Recovery'
        assert config['bot_type'] == 'AGGRESSIVE_RECOVERY'
        assert config['min_signal_strength'] == 2.5
        assert config['enable_martingale'] is True
    
    def test_load_balanced_template(self):
        """Test loading balanced template"""
        config = ConfigLoader.load_template('balanced')
        
        assert config['config_version'] == '2.0'
        assert config['strategy_name'] == 'Balanced Scalping'
        assert config['max_positions'] == 7
    
    def test_list_templates(self):
        """Test listing all templates"""
        templates = ConfigLoader.list_templates()
        
        assert len(templates) >= 3
        template_names = [t['name'] for t in templates]
        assert 'safe' in template_names
        assert 'aggressive' in template_names
        assert 'balanced' in template_names


class TestConfigValidation:
    """Test config validation"""
    
    def test_valid_config_passes(self):
        """Valid config should pass validation"""
        valid_config = {
            'config_version': '2.0',
            'strategy_name': 'Test Strategy',
            'bot_type': 'SCALPING',
            'min_signal_strength': 3.5,
            'max_positions': 5,
            'max_active_symbols': 4,
            'position_size_percent': 1.0,
            'risk_management': {
                'atr_sl_multiplier': 1.5,
                'atr_tp_multiplier': 4.0,
                'max_loss_per_trade': 0.15,
                'daily_profit_target': 2.0,
                'max_daily_loss': 3.0
            },
            'enable_martingale': False,
            'trailing_stop_enabled': True,
            'partial_take_profit': True,
            'progressive_recovery': False,
            'ai_score_weight': 0.3,
            'use_ml_prediction': False,
            'enable_event_manager': True,
            'enable_advanced_risk': True,
            'enable_adaptive_strategy': True,
            'check_interval': 20,
            'time_stop_base': 150,
            'symbols': ['BTCUSDT', 'ETHUSDT']
        }
        
        validated = ConfigSchema(**valid_config)
        assert validated.strategy_name == 'Test Strategy'
    
    def test_invalid_signal_strength_fails(self):
        """Invalid signal strength should fail"""
        config = ConfigLoader.load_template('safe')
        config['min_signal_strength'] = 10.0  # Out of range (0-5)
        
        with pytest.raises(ValidationError):
            ConfigSchema(**config)
    
    def test_invalid_bot_type_fails(self):
        """Invalid bot type should fail"""
        config = ConfigLoader.load_template('safe')
        config['bot_type'] = 'INVALID_TYPE'
        
        with pytest.raises(ValidationError):
            ConfigSchema(**config)
    
    def test_missing_required_field_fails(self):
        """Missing required field should fail"""
        config = ConfigLoader.load_template('safe')
        del config['risk_management']
        
        with pytest.raises(ValidationError):
            ConfigSchema(**config)


class TestConfigMigration:
    """Test config migration system"""
    
    def test_v1_0_to_v2_0_migration(self):
        """Test full migration from v1.0 to v2.0"""
        old_config = {
            'strategy_name': 'Old Strategy',
            'bot_type': 'scalping',
            'min_signal_strength': 4.0,
            'max_positions': 5,
            'stop_loss_pct': 1.0,
            'take_profit_pct': 2.0
        }
        
        migrated = ConfigMigration.migrate(old_config)
        
        assert migrated['config_version'] == '2.0'
        assert migrated['bot_type'] == 'SCALPING'  # Uppercase
        assert 'risk_management' in migrated  # Nested structure
        assert 'ai_score_weight' in migrated  # New v2.0 param
        assert 'stop_loss_pct' not in migrated  # Removed
    
    def test_v1_5_to_v2_0_migration(self):
        """Test migration from v1.5 to v2.0"""
        v1_5_config = {
            'config_version': '1.5',
            'strategy_name': 'Test',
            'bot_type': 'scalping',
            'min_signal_strength': 3.5,
            'max_positions': 5,
            'atr_sl_multiplier': 1.5,
            'atr_tp_multiplier': 4.0,
            'max_loss_per_trade': 0.15,
            'daily_profit_target': 2.0,
            'max_daily_loss': 3.0,
            'enable_martingale': False,
            'trailing_stop_enabled': True
        }
        
        migrated = ConfigMigration.migrate(v1_5_config)
        
        assert migrated['config_version'] == '2.0'
        assert 'risk_management' in migrated
        assert migrated['risk_management']['atr_sl_multiplier'] == 1.5
    
    def test_current_version_no_migration(self):
        """Current version config should not be migrated"""
        config = ConfigLoader.load_template('safe')
        original_version = config['config_version']
        
        migrated = ConfigMigration.migrate(config)
        
        assert migrated['config_version'] == original_version
        assert ConfigMigration.is_current_version(migrated)


class TestYAMLValidation:
    """Test YAML string validation"""
    
    def test_valid_yaml_string(self):
        """Valid YAML string should pass"""
        yaml_string = """
config_version: "2.0"
strategy_name: "Test"
bot_type: "SCALPING"
min_signal_strength: 3.5
max_positions: 5
max_active_symbols: 4
position_size_percent: 1.0
risk_management:
  atr_sl_multiplier: 1.5
  atr_tp_multiplier: 4.0
  max_loss_per_trade: 0.15
  daily_profit_target: 2.0
  max_daily_loss: 3.0
enable_martingale: false
trailing_stop_enabled: true
partial_take_profit: true
progressive_recovery: false
ai_score_weight: 0.3
use_ml_prediction: false
enable_event_manager: true
enable_advanced_risk: true
enable_adaptive_strategy: true
check_interval: 20
time_stop_base: 150
symbols:
  - BTCUSDT
  - ETHUSDT
"""
        
        is_valid, error, config = ConfigLoader.validate_yaml_string(yaml_string)
        
        assert is_valid is True
        assert error is None
        assert config is not None
        assert config['strategy_name'] == 'Test'
    
    def test_invalid_yaml_syntax(self):
        """Invalid YAML syntax should fail"""
        yaml_string = """
config_version: "2.0"
  invalid: indentation
    more: problems
"""
        
        is_valid, error, config = ConfigLoader.validate_yaml_string(yaml_string)
        
        assert is_valid is False
        assert error is not None
        assert config is None
    
    def test_yaml_with_old_version_auto_migrates(self):
        """Old version YAML should auto-migrate"""
        yaml_string = """
config_version: "1.0"
strategy_name: "Old"
bot_type: "scalping"
min_signal_strength: 4.0
max_positions: 5
stop_loss_pct: 1.0
take_profit_pct: 2.0
"""
        
        is_valid, error, config = ConfigLoader.validate_yaml_string(yaml_string)
        
        assert is_valid is True
        assert config['config_version'] == '2.0'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
