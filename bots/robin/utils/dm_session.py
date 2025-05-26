import discord
from typing import Dict, Optional, Callable, Awaitable
import asyncio
import time

class DMSession:
    def __init__(self, user: discord.User, timeout: int = 300):
        self.user = user
        self.timeout = timeout
        self.last_activity = time.time()
        self.active = True
        self.context = {}
    
    def is_expired(self) -> bool:
        """Check if the session has expired due to inactivity"""
        return time.time() - self.last_activity > self.timeout
    
    def update_activity(self):
        """Update the last activity timestamp"""
        self.last_activity = time.time()

class DMSessionManager:
    def __init__(self):
        self.sessions: Dict[int, DMSession] = {}
        self.handlers: Dict[str, Callable[[discord.Message, DMSession], Awaitable[None]]] = {}
    
    def create_session(self, user: discord.User, timeout: int = 300) -> DMSession:
        """Create a new DM session for a user"""
        session = DMSession(user, timeout)
        self.sessions[user.id] = session
        return session
    
    def get_session(self, user_id: int) -> Optional[DMSession]:
        """Get an active session for a user"""
        session = self.sessions.get(user_id)
        if session and not session.is_expired():
            session.update_activity()
            return session
        return None
    
    def end_session(self, user_id: int):
        """End a user's DM session"""
        if user_id in self.sessions:
            del self.sessions[user_id]
    
    def register_handler(self, command: str, handler: Callable[[discord.Message, DMSession], Awaitable[None]]):
        """Register a command handler for DM sessions"""
        self.handlers[command.lower()] = handler
    
    async def handle_message(self, message: discord.Message):
        """Handle an incoming DM message"""
        if not message.guild is None:  # Only handle DMs
            return
        
        session = self.get_session(message.author.id)
        if not session:
            session = self.create_session(message.author)
        
        # Check for command
        content = message.content.lower().strip()
        if content.startswith('!'):
            command = content[1:].split()[0]
            if command in self.handlers:
                try:
                    await self.handlers[command](message, session)
                except Exception as e:
                    await message.channel.send(f"Error processing command: {str(e)}")
                return
        
        # Update session activity
        session.update_activity() 