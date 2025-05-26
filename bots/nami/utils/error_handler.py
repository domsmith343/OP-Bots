import discord
from functools import wraps
import asyncio
from typing import Callable, Any

class CommandError(Exception):
    """Base exception for command errors"""
    pass

class RateLimitError(CommandError):
    """Raised when a user hits rate limit"""
    pass

class APIError(CommandError):
    """Raised when an API call fails"""
    pass

class CommandCooldown:
    def __init__(self, seconds: int):
        self.seconds = seconds
        self.last_used = {}

    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(ctx, *args, **kwargs):
            user_id = ctx.author.id
            current_time = asyncio.get_event_loop().time()
            
            if user_id in self.last_used:
                time_passed = current_time - self.last_used[user_id]
                if time_passed < self.seconds:
                    remaining = round(self.seconds - time_passed, 1)
                    raise RateLimitError(f"Please wait {remaining} seconds before using this command again.")
            
            self.last_used[user_id] = current_time
            return await func(ctx, *args, **kwargs)
        return wrapper

async def handle_error(ctx, error: Exception) -> None:
    """Handle different types of errors and send appropriate messages"""
    if isinstance(error, RateLimitError):
        await ctx.send(f"⏰ {error}")
    elif isinstance(error, APIError):
        await ctx.send(f"🔧 API Error: {error}")
    else:
        await ctx.send(f"❌ An error occurred: {str(error)}")

def create_error_embed(title: str, description: str) -> discord.Embed:
    """Create a formatted error embed"""
    embed = discord.Embed(
        title=f"❌ {title}",
        description=description,
        color=discord.Color.red()
    )
    return embed 