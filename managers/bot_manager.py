"""
Bot Manager - Multi-User Bot Instance Management
Manages bot lifecycle, state, and isolation per user
"""

import asyncio
import logging
from typing import Dict, Optional, List
from datetime import datetime
from enum import Enum
import json
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class BotStatus(str, Enum):
    """Bot status states"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


class BotInstance:
    """Individual bot instance for a user"""
    
    def __init__(self, user_id: int, config_dict: dict, bot_type: str):
        self.user_id = user_id
        self.config_dict = config_dict
        self.bot_type = bot_type
        self.status = BotStatus.STOPPED
        self.task: Optional[asyncio.Task] = None
        self.bot_object = None
        self.start_time: Optional[datetime] = None
        self.error_message: Optional[str] = None
        self.state_file = f"bot_state_user{user_id}.json"
        
    def get_info(self) -> dict:
        """Get bot instance information"""
        uptime = None
        if self.start_time:
            uptime = (datetime.now() - self.start_time).total_seconds()
            
        return {
            "user_id": self.user_id,
            "bot_type": self.bot_type,
            "status": self.status.value,
            "config_name": self.config_dict.get("name", "Unknown"),
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "uptime_seconds": uptime,
            "error": self.error_message
        }


class BotManager:
    """
    Manages bot instances for multiple users
    Ensures isolation between users and prevents conflicts
    """
    
    def __init__(self):
        self.instances: Dict[int, BotInstance] = {}
        self.lock = asyncio.Lock()
        logger.info("🤖 Bot Manager initialized")
        
    async def start_bot(self, user_id: int, config_dict: dict, bot_type: str = "aggressive") -> dict:
        """
        Start bot for a specific user
        
        Args:
            user_id: User ID
            config_dict: Bot configuration as dictionary
            bot_type: "aggressive" or "scalping"
            
        Returns:
            Bot status information
        """
        async with self.lock:
            # Check if user already has a running bot
            if user_id in self.instances:
                instance = self.instances[user_id]
                if instance.status == BotStatus.RUNNING:
                    logger.warning(f"❌ User {user_id} already has a running bot")
                    return {
                        "success": False,
                        "message": "Bot is already running for this user",
                        "status": instance.get_info()
                    }
                    
            # Create new instance
            logger.info(f"🚀 Starting {bot_type} bot for user {user_id}")
            instance = BotInstance(user_id, config_dict, bot_type)
            instance.status = BotStatus.STARTING
            self.instances[user_id] = instance
            
            try:
                # Import bot class based on type
                if bot_type == "aggressive":
                    from bots.aggressive_recovery_bot import AggressiveRecoveryBot
                    bot_class = AggressiveRecoveryBot
                elif bot_type == "scalping":
                    from bots.daily_scalping_bot import DailyScalpingBot
                    bot_class = DailyScalpingBot
                else:
                    raise ValueError(f"Unknown bot type: {bot_type}")
                
                # Create bot instance with user-specific config
                instance.bot_object = bot_class(
                    user_id=user_id,
                    config_dict=config_dict
                )
                
                # Start bot in background task
                instance.task = asyncio.create_task(
                    self._run_bot(instance)
                )
                
                instance.status = BotStatus.RUNNING
                instance.start_time = datetime.now()
                
                logger.info(f"✅ Bot started successfully for user {user_id}")
                return {
                    "success": True,
                    "message": f"{bot_type.capitalize()} bot started successfully",
                    "status": instance.get_info()
                }
                
            except Exception as e:
                logger.error(f"❌ Failed to start bot for user {user_id}: {str(e)}")
                instance.status = BotStatus.ERROR
                instance.error_message = str(e)
                return {
                    "success": False,
                    "message": f"Failed to start bot: {str(e)}",
                    "status": instance.get_info()
                }
    
    async def _run_bot(self, instance: BotInstance):
        """Run bot in background task"""
        try:
            logger.info(f"🤖 Bot thread started for user {instance.user_id}")
            # Run bot's main method
            if hasattr(instance.bot_object, 'run'):
                await asyncio.to_thread(instance.bot_object.run)
            else:
                logger.error(f"❌ Bot object has no 'run' method for user {instance.user_id}")
                instance.status = BotStatus.ERROR
                instance.error_message = "Bot has no run method"
        except Exception as e:
            logger.error(f"❌ Bot error for user {instance.user_id}: {str(e)}")
            instance.status = BotStatus.ERROR
            instance.error_message = str(e)
        finally:
            logger.info(f"🛑 Bot stopped for user {instance.user_id}")
            if instance.status != BotStatus.ERROR:
                instance.status = BotStatus.STOPPED
    
    async def stop_bot(self, user_id: int) -> dict:
        """
        Stop bot for a specific user
        
        Args:
            user_id: User ID
            
        Returns:
            Bot status information
        """
        async with self.lock:
            if user_id not in self.instances:
                return {
                    "success": False,
                    "message": "No bot running for this user",
                    "status": None
                }
            
            instance = self.instances[user_id]
            
            if instance.status == BotStatus.STOPPED:
                return {
                    "success": False,
                    "message": "Bot is already stopped",
                    "status": instance.get_info()
                }
            
            logger.info(f"🛑 Stopping bot for user {user_id}")
            instance.status = BotStatus.STOPPING
            
            try:
                # Stop the bot object
                if hasattr(instance.bot_object, 'stop'):
                    instance.bot_object.stop()
                
                # Cancel the background task
                if instance.task and not instance.task.done():
                    instance.task.cancel()
                    try:
                        await instance.task
                    except asyncio.CancelledError:
                        pass
                
                instance.status = BotStatus.STOPPED
                instance.start_time = None
                
                logger.info(f"✅ Bot stopped successfully for user {user_id}")
                return {
                    "success": True,
                    "message": "Bot stopped successfully",
                    "status": instance.get_info()
                }
                
            except Exception as e:
                logger.error(f"❌ Error stopping bot for user {user_id}: {str(e)}")
                instance.status = BotStatus.ERROR
                instance.error_message = str(e)
                return {
                    "success": False,
                    "message": f"Error stopping bot: {str(e)}",
                    "status": instance.get_info()
                }
    
    async def restart_bot(self, user_id: int, config_dict: Optional[dict] = None) -> dict:
        """
        Restart bot for a specific user
        
        Args:
            user_id: User ID
            config_dict: Optional new configuration
            
        Returns:
            Bot status information
        """
        # Stop existing bot
        stop_result = await self.stop_bot(user_id)
        
        # Wait a bit for cleanup
        await asyncio.sleep(1)
        
        # Get bot type and config
        if user_id in self.instances:
            bot_type = self.instances[user_id].bot_type
            if config_dict is None:
                config_dict = self.instances[user_id].config_dict
        else:
            return {
                "success": False,
                "message": "Cannot restart: no previous bot instance found",
                "status": None
            }
        
        # Start with new or existing config
        return await self.start_bot(user_id, config_dict, bot_type)
    
    def get_bot_status(self, user_id: int) -> Optional[dict]:
        """
        Get status of bot for a specific user
        
        Args:
            user_id: User ID
            
        Returns:
            Bot status information or None
        """
        if user_id not in self.instances:
            return None
        
        return self.instances[user_id].get_info()
    
    def get_all_bots(self) -> List[dict]:
        """Get status of all running bots"""
        return [instance.get_info() for instance in self.instances.values()]
    
    async def stop_all_bots(self):
        """Stop all running bots (for shutdown)"""
        logger.info("🛑 Stopping all bots...")
        tasks = []
        for user_id in list(self.instances.keys()):
            tasks.append(self.stop_bot(user_id))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        logger.info("✅ All bots stopped")


# Global bot manager instance
bot_manager = BotManager()
