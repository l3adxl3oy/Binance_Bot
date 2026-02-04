"""
Bot Control Router - Multi-User Bot Management
Endpoints for starting, stopping, and monitoring trading bots
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
import logging

from database.db import get_db
from database.models import User, BotConfig
from api.auth import get_current_user
from managers.bot_manager import bot_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/bots", tags=["Bot Control"])


@router.post("/start")
async def start_bot(
    config_id: Optional[int] = None,
    bot_type: str = "aggressive",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Start trading bot for current user
    
    - **config_id**: Optional config ID to use (defaults to active config)
    - **bot_type**: "aggressive" or "scalping"
    """
    # Get bot configuration
    if config_id:
        config = db.query(BotConfig).filter(
            BotConfig.id == config_id,
            BotConfig.user_id == current_user.id
        ).first()
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Configuration not found"
            )
    else:
        # Use active config
        config = db.query(BotConfig).filter(
            BotConfig.user_id == current_user.id,
            BotConfig.is_active == True
        ).first()
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active configuration found. Please activate a config first."
            )
    
    # Parse YAML config to dict
    import yaml
    try:
        config_dict = yaml.safe_load(config.config_yaml)
        config_dict['name'] = config.name
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid YAML configuration: {str(e)}"
        )
    
    # Start bot via manager
    result = await bot_manager.start_bot(
        user_id=current_user.id,
        config_dict=config_dict,
        bot_type=bot_type
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return result


@router.post("/stop")
async def stop_bot(
    current_user: User = Depends(get_current_user)
):
    """Stop trading bot for current user"""
    result = await bot_manager.stop_bot(current_user.id)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return result


@router.post("/restart")
async def restart_bot(
    config_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Restart trading bot with optional new configuration"""
    config_dict = None
    
    if config_id:
        config = db.query(BotConfig).filter(
            BotConfig.id == config_id,
            BotConfig.user_id == current_user.id
        ).first()
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Configuration not found"
            )
        
        import yaml
        try:
            config_dict = yaml.safe_load(config.config_yaml)
            config_dict['name'] = config.name
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid YAML configuration: {str(e)}"
            )
    
    result = await bot_manager.restart_bot(
        user_id=current_user.id,
        config_dict=config_dict
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return result


@router.get("/status")
async def get_bot_status(
    current_user: User = Depends(get_current_user)
):
    """Get current bot status for user"""
    status_info = bot_manager.get_bot_status(current_user.id)
    
    if status_info is None:
        return {
            "running": False,
            "status": "stopped",
            "message": "No bot instance found"
        }
    
    return {
        "running": status_info["status"] == "running",
        **status_info
    }


@router.get("/logs")
async def get_bot_logs(
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    """
    Get recent bot logs for current user
    
    - **limit**: Maximum number of log entries to return
    """
    # TODO: Implement log storage and retrieval
    # For now, return placeholder
    return {
        "logs": [],
        "message": "Log retrieval not yet implemented"
    }
