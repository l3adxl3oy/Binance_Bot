"""
Config Migration System
Handles automatic upgrade of old config versions to current version
Ensures backward compatibility when code is updated
"""

import copy
from typing import Dict, Any
import warnings


class ConfigMigration:
    """Handles config version migrations"""
    
    CURRENT_VERSION = "2.0"
    
    @staticmethod
    def migrate(config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Migrate config from any old version to current version
        
        Args:
            config: Config dictionary (any version)
            
        Returns:
            Migrated config (current version)
        """
        # Make a copy to avoid modifying original
        config = copy.deepcopy(config)
        
        config_version = config.get('config_version', '1.0')
        original_version = config_version
        
        print(f"\n🔄 Config Migration Started")
        print(f"   From: v{config_version}")
        print(f"   To:   v{ConfigMigration.CURRENT_VERSION}\n")
        
        # Migration chain: 1.0 → 1.5 → 2.0
        if config_version == '1.0':
            config = ConfigMigration._migrate_1_0_to_1_5(config)
            config_version = '1.5'
        
        if config_version == '1.5':
            config = ConfigMigration._migrate_1_5_to_2_0(config)
            config_version = '2.0'
        
        if config_version == ConfigMigration.CURRENT_VERSION:
            print(f"✅ Migration completed: v{original_version} → v{config_version}\n")
        else:
            print(f"⚠️ Unknown version: {config_version}\n")
        
        return config
    
    @staticmethod
    def _migrate_1_0_to_1_5(config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Migrate v1.0 → v1.5
        
        Changes:
        - Add trailing_stop_enabled (default: True)
        - Rename stop_loss_pct → stop_loss_percent
        - Rename take_profit_pct → take_profit_percent
        - Add default symbols if missing
        """
        print("⚡ Migrating v1.0 → v1.5...")
        
        # 1. Add new parameters with defaults
        if 'trailing_stop_enabled' not in config:
            config['trailing_stop_enabled'] = True
            print("  ✅ Added: trailing_stop_enabled = True")
        
        if 'partial_take_profit' not in config:
            config['partial_take_profit'] = True
            print("  ✅ Added: partial_take_profit = True")
        
        # 2. Rename parameters
        if 'stop_loss_pct' in config:
            config['stop_loss_percent'] = config.pop('stop_loss_pct')
            print("  ✅ Renamed: stop_loss_pct → stop_loss_percent")
        
        if 'take_profit_pct' in config:
            config['take_profit_percent'] = config.pop('take_profit_pct')
            print("  ✅ Renamed: take_profit_pct → take_profit_percent")
        
        # 3. Add default symbols
        if 'symbols' not in config:
            config['symbols'] = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT"]
            print("  ✅ Added: default symbols list")
        
        # 4. Add check_interval
        if 'check_interval' not in config:
            config['check_interval'] = 20
            print("  ✅ Added: check_interval = 20")
        
        config['config_version'] = '1.5'
        print("  ✅ Updated version: 1.0 → 1.5\n")
        
        return config
    
    @staticmethod
    def _migrate_1_5_to_2_0(config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Migrate v1.5 → v2.0
        
        Changes:
        - Restructure risk params into nested 'risk_management' object
        - Convert bot_type to uppercase enum
        - Add AI/ML parameters
        - Add advanced feature flags
        - Add position sizing adjustments
        """
        print("⚡ Migrating v1.5 → v2.0...")
        
        # 1. Create nested risk_management structure
        risk_params = {}
        
        # Migrate flat params to nested structure
        if 'atr_sl_multiplier' in config:
            risk_params['atr_sl_multiplier'] = config.pop('atr_sl_multiplier')
        else:
            risk_params['atr_sl_multiplier'] = 1.5
        
        if 'atr_tp_multiplier' in config:
            risk_params['atr_tp_multiplier'] = config.pop('atr_tp_multiplier')
        else:
            risk_params['atr_tp_multiplier'] = 4.0
        
        if 'max_loss_per_trade' in config:
            risk_params['max_loss_per_trade'] = config.pop('max_loss_per_trade')
        else:
            risk_params['max_loss_per_trade'] = 0.15
        
        if 'daily_profit_target' in config:
            risk_params['daily_profit_target'] = config.pop('daily_profit_target')
        else:
            risk_params['daily_profit_target'] = 2.0
        
        if 'max_daily_loss' in config:
            risk_params['max_daily_loss'] = config.pop('max_daily_loss')
        else:
            risk_params['max_daily_loss'] = 3.0
        
        config['risk_management'] = risk_params
        print("  ✅ Restructured: Created nested risk_management object")
        
        # 2. Convert bot_type to uppercase enum
        if 'bot_type' in config and isinstance(config['bot_type'], str):
            bot_type_map = {
                'scalping': 'SCALPING',
                'aggressive': 'AGGRESSIVE_RECOVERY',
                'aggressive_recovery': 'AGGRESSIVE_RECOVERY'
            }
            old_type = config['bot_type'].lower()
            config['bot_type'] = bot_type_map.get(old_type, 'SCALPING')
            print(f"  ✅ Converted: bot_type '{old_type}' → '{config['bot_type']}'")
        
        # 3. Add AI/ML parameters (v2.0+)
        if 'ai_score_weight' not in config:
            config['ai_score_weight'] = 0.3
            print("  ✅ Added: ai_score_weight = 0.3")
        
        if 'use_ml_prediction' not in config:
            config['use_ml_prediction'] = False
            print("  ✅ Added: use_ml_prediction = False")
        
        # 4. Add advanced feature flags
        if 'enable_event_manager' not in config:
            config['enable_event_manager'] = True
            print("  ✅ Added: enable_event_manager = True")
        
        if 'enable_advanced_risk' not in config:
            config['enable_advanced_risk'] = True
            print("  ✅ Added: enable_advanced_risk = True")
        
        if 'enable_adaptive_strategy' not in config:
            config['enable_adaptive_strategy'] = True
            print("  ✅ Added: enable_adaptive_strategy = True")
        
        # 5. Add position sizing adjustments
        if 'position_size_percent' not in config:
            config['position_size_percent'] = 1.0
            print("  ✅ Added: position_size_percent = 1.0")
        
        if 'max_active_symbols' not in config:
            config['max_active_symbols'] = config.get('max_positions', 5)
            print(f"  ✅ Added: max_active_symbols = {config['max_active_symbols']}")
        
        # 6. Add time_stop_base
        if 'time_stop_base' not in config:
            config['time_stop_base'] = 150
            print("  ✅ Added: time_stop_base = 150")
        
        # 7. Add progressive_recovery flag
        if 'progressive_recovery' not in config:
            config['progressive_recovery'] = False
            print("  ✅ Added: progressive_recovery = False")
        
        # 8. Remove deprecated params (with warning)
        deprecated_params = ['stop_loss_percent', 'take_profit_percent']
        for param in deprecated_params:
            if param in config:
                value = config.pop(param)
                warnings.warn(
                    f"⚠️ '{param}' is deprecated in v2.0. "
                    f"Use risk_management.atr_sl_multiplier/atr_tp_multiplier instead.",
                    DeprecationWarning
                )
                print(f"  ⚠️ Removed deprecated: {param} (was {value})")
        
        config['config_version'] = '2.0'
        print("  ✅ Updated version: 1.5 → 2.0\n")
        
        return config
    
    @staticmethod
    def is_current_version(config: Dict[str, Any]) -> bool:
        """Check if config is current version"""
        config_version = config.get('config_version', '1.0')
        return config_version == ConfigMigration.CURRENT_VERSION
    
    @staticmethod
    def get_migration_summary(old_version: str, new_version: str) -> str:
        """Get human-readable migration summary"""
        summaries = {
            ('1.0', '1.5'): [
                "Added trailing_stop_enabled parameter",
                "Renamed stop_loss_pct → stop_loss_percent",
                "Added default symbols list",
                "Added check_interval parameter"
            ],
            ('1.5', '2.0'): [
                "Restructured risk parameters into nested object",
                "Converted bot_type to uppercase enum",
                "Added AI/ML prediction parameters",
                "Added advanced feature flags (event, risk, adaptive)",
                "Added position sizing adjustments",
                "Deprecated old stop_loss_percent/take_profit_percent"
            ],
            ('1.0', '2.0'): [
                "Complete upgrade from v1.0 to v2.0",
                "All v1.5 and v2.0 changes applied",
                "Config fully modernized"
            ]
        }
        
        return summaries.get((old_version, new_version), [])
