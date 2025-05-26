import time
from typing import Dict, Optional
import discord
from discord.ext import commands

class CooldownManager:
    def __init__(self):
        self._cooldowns: Dict[str, Dict[int, float]] = {}
    
    def get_remaining_time(self, command_name: str, user_id: int, cooldown_seconds: int) -> Optional[float]:
        """Get remaining cooldown time for a user's command"""
        if command_name not in self._cooldowns:
            self._cooldowns[command_name] = {}
        
        last_used = self._cooldowns[command_name].get(user_id, 0)
        current_time = time.time()
        remaining = cooldown_seconds - (current_time - last_used)
        
        if remaining <= 0:
            return None
        return remaining
    
    def update_cooldown(self, command_name: str, user_id: int):
        """Update the cooldown timestamp for a user's command"""
        if command_name not in self._cooldowns:
            self._cooldowns[command_name] = {}
        self._cooldowns[command_name][user_id] = time.time()
    
    def format_cooldown_message(self, remaining_time: float) -> str:
        """Format the remaining cooldown time into a user-friendly message"""
        if remaining_time < 1:
            return f"Please wait {remaining_time:.1f} seconds before using this command again."
        return f"Please wait {int(remaining_time)} seconds before using this command again."

class CooldownError(commands.CommandError):
    """Custom error for command cooldowns"""
    def __init__(self, remaining_time: float):
        self.remaining_time = remaining_time
        super().__init__(f"Command is on cooldown. {CooldownManager.format_cooldown_message(remaining_time)}")

def cooldown(seconds: int):
    """Decorator to add cooldown to a command"""
    def decorator(func):
        async def wrapper(self, ctx, *args, **kwargs):
            if not hasattr(self, 'cooldown_manager'):
                self.cooldown_manager = CooldownManager()
            
            remaining = self.cooldown_manager.get_remaining_time(
                func.__name__,
                ctx.author.id,
                seconds
            )
            
            if remaining is not None:
                raise CooldownError(remaining)
            
            self.cooldown_manager.update_cooldown(func.__name__, ctx.author.id)
            return await func(self, ctx, *args, **kwargs)
        return wrapper
    return decorator 