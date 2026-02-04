"""
Config Management API Endpoints
Handles YAML config templates, user configs, validation
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
import yaml

from database.db import get_db
from database.models import User, BotConfig
from api.schemas import (
    ConfigCreate, ConfigUpdate, ConfigResponse, ConfigDetail,
    TemplateInfo, SuccessResponse
)
from api.auth import get_current_user
from config.config_loader import ConfigLoader

router = APIRouter(prefix="/configs", tags=["Configuration"])


# ==================== TEMPLATE ENDPOINTS ====================

@router.get("/templates", response_model=List[TemplateInfo])
async def list_templates():
    """
    List all built-in config templates
    
    Returns:
        List of available templates (safe, aggressive, balanced)
    """
    templates = ConfigLoader.list_templates()
    
    # Add descriptions
    descriptions = {
        'safe': 'Low risk strategy with high signal requirements (4.5★). Best for beginners.',
        'aggressive': 'High risk/reward with martingale recovery (2.5★). For experienced traders.',
        'balanced': 'Medium risk balanced approach (3.5★). Good for most traders.'
    }
    
    result = []
    for template in templates:
        result.append(TemplateInfo(
            **template,
            description=descriptions.get(template['name'], '')
        ))
    
    return result


@router.get("/templates/{template_name}", response_model=ConfigDetail)
async def get_template(template_name: str):
    """
    Get specific template YAML content
    
    Args:
        template_name: Template name (safe, aggressive, balanced)
        
    Returns:
        Template config with YAML content
    """
    try:
        config = ConfigLoader.load_template(template_name)
        
        # Convert back to YAML string
        config_yaml = yaml.dump(config, allow_unicode=True, indent=2, sort_keys=False)
        
        return ConfigDetail(
            id=0,  # Templates don't have IDs
            user_id=0,
            name=f"{template_name.title()} Template",
            config_version=config.get('config_version', '2.0'),
            strategy_name=config.get('strategy_name'),
            bot_type=config.get('bot_type'),
            is_active=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            last_used_at=None,
            config_yaml=config_yaml
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# ==================== USER CONFIG ENDPOINTS ====================

@router.get("/my-configs", response_model=List[ConfigResponse])
async def list_user_configs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all configs created by current user
    
    Returns:
        List of user's saved configs
    """
    configs = db.query(BotConfig).filter(
        BotConfig.user_id == current_user.id
    ).order_by(BotConfig.updated_at.desc()).all()
    
    return configs


@router.get("/my-configs/{config_id}", response_model=ConfigDetail)
async def get_user_config(
    config_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get specific user config with full YAML content
    
    Args:
        config_id: Config ID
        
    Returns:
        Config with YAML content
    """
    config = db.query(BotConfig).filter(
        BotConfig.id == config_id,
        BotConfig.user_id == current_user.id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Config not found"
        )
    
    return config


@router.post("/validate")
async def validate_config_yaml(config_yaml: str):
    """
    Validate YAML config without saving
    
    Args:
        config_yaml: YAML config string (send as plain text body)
        
    Returns:
        Validation result with errors if any
    """
    is_valid, error, config_dict = ConfigLoader.validate_yaml_string(config_yaml)
    
    if is_valid:
        return {
            "valid": True,
            "message": "Config is valid",
            "config": config_dict,
            "migrated": config_dict.get('config_version') != '2.0'  # Was migrated?
        }
    else:
        return {
            "valid": False,
            "message": "Config validation failed",
            "errors": error.split('\n') if error else []
        }


@router.post("/create", response_model=ConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_config(
    config_data: ConfigCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create new config from YAML
    
    Args:
        config_data: Config name and YAML content
        
    Returns:
        Created config
    """
    # Validate YAML first
    is_valid, error, config_dict = ConfigLoader.validate_yaml_string(config_data.config_yaml)
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid config: {error}"
        )
    
    # Check if name already exists for this user
    existing = db.query(BotConfig).filter(
        BotConfig.user_id == current_user.id,
        BotConfig.name == config_data.name
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Config with name '{config_data.name}' already exists"
        )
    
    # Create new config
    new_config = BotConfig(
        user_id=current_user.id,
        name=config_data.name,
        config_yaml=config_data.config_yaml,
        config_version=config_dict.get('config_version', '2.0'),
        strategy_name=config_dict.get('strategy_name'),
        bot_type=config_dict.get('bot_type'),
        is_active=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(new_config)
    db.commit()
    db.refresh(new_config)
    
    return new_config


@router.put("/{config_id}", response_model=ConfigResponse)
async def update_config(
    config_id: int,
    config_data: ConfigUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update existing config
    
    Args:
        config_id: Config ID
        config_data: Updated config name and/or YAML
        
    Returns:
        Updated config
    """
    config = db.query(BotConfig).filter(
        BotConfig.id == config_id,
        BotConfig.user_id == current_user.id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Config not found"
        )
    
    # Update name if provided
    if config_data.name:
        config.name = config_data.name
    
    # Update YAML if provided
    if config_data.config_yaml:
        # Validate first
        is_valid, error, config_dict = ConfigLoader.validate_yaml_string(config_data.config_yaml)
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid config: {error}"
            )
        
        config.config_yaml = config_data.config_yaml
        config.config_version = config_dict.get('config_version', '2.0')
        config.strategy_name = config_dict.get('strategy_name')
        config.bot_type = config_dict.get('bot_type')
    
    config.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(config)
    
    return config


@router.delete("/{config_id}", response_model=SuccessResponse)
async def delete_config(
    config_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete user config
    
    Args:
        config_id: Config ID
        
    Returns:
        Success message
    """
    config = db.query(BotConfig).filter(
        BotConfig.id == config_id,
        BotConfig.user_id == current_user.id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Config not found"
        )
    
    name = config.name
    db.delete(config)
    db.commit()
    
    return SuccessResponse(
        success=True,
        message=f"Config '{name}' deleted successfully"
    )


@router.post("/{config_id}/activate", response_model=SuccessResponse)
async def activate_config(
    config_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Set config as active (deactivates others)
    
    Args:
        config_id: Config ID
        
    Returns:
        Success message
    """
    config = db.query(BotConfig).filter(
        BotConfig.id == config_id,
        BotConfig.user_id == current_user.id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Config not found"
        )
    
    # Deactivate all user's configs
    db.query(BotConfig).filter(
        BotConfig.user_id == current_user.id
    ).update({"is_active": False})
    
    # Activate selected config
    config.is_active = True
    config.last_used_at = datetime.utcnow()
    
    db.commit()
    
    return SuccessResponse(
        success=True,
        message=f"Config '{config.name}' activated"
    )


@router.get("/active", response_model=ConfigDetail)
async def get_active_config(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get currently active config for user
    
    Returns:
        Active config or error if none active
    """
    config = db.query(BotConfig).filter(
        BotConfig.user_id == current_user.id,
        BotConfig.is_active == True
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active config. Please activate a config first."
        )
    
    return config
