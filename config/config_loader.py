"""
Config Loader with Auto-Migration Support
Loads YAML configs and automatically upgrades old versions
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import ValidationError
import shutil
from datetime import datetime

from .schema import ConfigSchema
from .migrations import ConfigMigration


class ConfigLoader:
    """Load and validate config files with auto-migration"""
    
    TEMPLATES_DIR = Path(__file__).parent / "templates"
    
    @staticmethod
    def load_config(config_path: str, auto_migrate: bool = True) -> Dict[str, Any]:
        """
        Load config from YAML file with optional auto-migration
        
        Args:
            config_path: Path to config YAML file
            auto_migrate: Automatically migrate old versions (default: True)
            
        Returns:
            Validated config dictionary
            
        Raises:
            FileNotFoundError: Config file not found
            ValueError: Invalid config format or validation failed
        """
        path = Path(config_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        # 1. Load YAML
        try:
            with open(path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML syntax: {e}")
        
        if not isinstance(config, dict):
            raise ValueError("Config must be a YAML dictionary/object")
        
        # 2. Check version and migrate if needed
        config_version = config.get('config_version', '1.0')
        current_version = ConfigMigration.CURRENT_VERSION
        
        if config_version != current_version:
            if auto_migrate:
                print(f"\n📦 Config version mismatch detected:")
                print(f"   File: {path.name}")
                print(f"   Current: v{config_version}")
                print(f"   Required: v{current_version}")
                
                # Migrate config
                config = ConfigMigration.migrate(config)
                
                # Save migrated config (backup original first)
                ConfigLoader._backup_and_save(path, config)
            else:
                raise ValueError(
                    f"Config version mismatch: got v{config_version}, "
                    f"expected v{current_version}. Set auto_migrate=True to fix."
                )
        else:
            print(f"✅ Config is up-to-date (v{config_version}): {path.name}")
        
        # 3. Validate schema
        try:
            validated = ConfigSchema(**config)
            print(f"✅ Config validation passed\n")
            return validated.dict()
        except ValidationError as e:
            error_msg = "Config validation failed:\n"
            for error in e.errors():
                field = '.'.join(str(x) for x in error['loc'])
                error_msg += f"  - {field}: {error['msg']}\n"
            raise ValueError(error_msg)
    
    @staticmethod
    def load_template(template_name: str) -> Dict[str, Any]:
        """
        Load a built-in template
        
        Args:
            template_name: Template name (safe, aggressive, balanced)
            
        Returns:
            Config dictionary
        """
        template_file = ConfigLoader.TEMPLATES_DIR / f"{template_name}.yaml"
        
        if not template_file.exists():
            available = [f.stem for f in ConfigLoader.TEMPLATES_DIR.glob("*.yaml")]
            raise ValueError(
                f"Template '{template_name}' not found. "
                f"Available: {', '.join(available)}"
            )
        
        return ConfigLoader.load_config(str(template_file), auto_migrate=False)
    
    @staticmethod
    def list_templates() -> list:
        """List all available built-in templates"""
        if not ConfigLoader.TEMPLATES_DIR.exists():
            return []
        
        templates = []
        for file in ConfigLoader.TEMPLATES_DIR.glob("*.yaml"):
            try:
                config = ConfigLoader.load_config(str(file), auto_migrate=False)
                templates.append({
                    'name': file.stem,
                    'file': file.name,
                    'strategy_name': config.get('strategy_name', 'Unknown'),
                    'bot_type': config.get('bot_type', 'Unknown'),
                    'version': config.get('config_version', '1.0')
                })
            except Exception as e:
                print(f"⚠️ Failed to load template {file.name}: {e}")
        
        return templates
    
    @staticmethod
    def validate_yaml_string(yaml_string: str) -> tuple[bool, Optional[str], Optional[Dict]]:
        """
        Validate YAML string without saving to file
        
        Args:
            yaml_string: YAML content as string
            
        Returns:
            Tuple of (is_valid, error_message, config_dict)
        """
        try:
            # Parse YAML
            config = yaml.safe_load(yaml_string)
            
            if not isinstance(config, dict):
                return False, "Config must be a YAML dictionary/object", None
            
            # Check if migration needed
            config_version = config.get('config_version', '1.0')
            if config_version != ConfigMigration.CURRENT_VERSION:
                config = ConfigMigration.migrate(config)
            
            # Validate schema
            validated = ConfigSchema(**config)
            return True, None, validated.dict()
            
        except yaml.YAMLError as e:
            return False, f"Invalid YAML syntax: {e}", None
        except ValidationError as e:
            errors = []
            for error in e.errors():
                field = '.'.join(str(x) for x in error['loc'])
                errors.append(f"{field}: {error['msg']}")
            return False, "\n".join(errors), None
        except Exception as e:
            return False, str(e), None
    
    @staticmethod
    def _backup_and_save(config_path: Path, new_config: Dict[str, Any]):
        """Backup original config and save migrated version"""
        # Create backup with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = config_path.with_suffix(f'.backup_{timestamp}.yaml')
        
        if config_path.exists():
            shutil.copy(config_path, backup_path)
            print(f"📦 Backup created: {backup_path.name}")
        
        # Save migrated config
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(new_config, f, allow_unicode=True, indent=2, sort_keys=False)
        
        print(f"💾 Updated config saved: {config_path.name}\n")
    
    @staticmethod
    def save_config(config: Dict[str, Any], file_path: str):
        """
        Save config to YAML file
        
        Args:
            config: Config dictionary
            file_path: Path to save file
        """
        # Validate before saving
        validated = ConfigSchema(**config)
        
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(validated.dict(), f, allow_unicode=True, indent=2, sort_keys=False)
        
        print(f"💾 Config saved: {path}")
