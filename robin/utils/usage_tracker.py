import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
import os
from .database import Database

class UsageTracker:
    def __init__(self, db: Database):
        self.db = db
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Ensure required database tables exist"""
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS command_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                command_name TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                guild_id INTEGER,
                channel_id INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN DEFAULT TRUE,
                error_message TEXT
            )
        """)
        
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS command_stats (
                command_name TEXT PRIMARY KEY,
                total_uses INTEGER DEFAULT 0,
                successful_uses INTEGER DEFAULT 0,
                failed_uses INTEGER DEFAULT 0,
                last_used DATETIME
            )
        """)
    
    def track_command(self, command_name: str, user_id: int, guild_id: Optional[int] = None,
                     channel_id: Optional[int] = None, success: bool = True,
                     error_message: Optional[str] = None):
        """Track a command usage"""
        # Record individual usage
        self.db.execute("""
            INSERT INTO command_usage 
            (command_name, user_id, guild_id, channel_id, success, error_message)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (command_name, user_id, guild_id, channel_id, success, error_message))
        
        # Update command stats
        self.db.execute("""
            INSERT INTO command_stats (command_name, total_uses, successful_uses, failed_uses, last_used)
            VALUES (?, 1, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(command_name) DO UPDATE SET
                total_uses = total_uses + 1,
                successful_uses = successful_uses + ?,
                failed_uses = failed_uses + ?,
                last_used = CURRENT_TIMESTAMP
        """, (command_name, int(success), int(not success), int(success), int(not success)))
    
    def get_command_stats(self, command_name: Optional[str] = None,
                         time_period: Optional[timedelta] = None) -> Dict:
        """Get usage statistics for a command or all commands"""
        if command_name:
            query = """
                SELECT 
                    command_name,
                    total_uses,
                    successful_uses,
                    failed_uses,
                    last_used
                FROM command_stats
                WHERE command_name = ?
            """
            params = (command_name,)
        else:
            query = """
                SELECT 
                    command_name,
                    total_uses,
                    successful_uses,
                    failed_uses,
                    last_used
                FROM command_stats
                ORDER BY total_uses DESC
            """
            params = ()
        
        if time_period:
            query = query.replace("FROM command_stats", 
                                "FROM command_stats WHERE last_used >= datetime('now', ?)")
            params = params + (f"-{time_period.total_seconds()} seconds",)
        
        results = self.db.fetch_all(query, params)
        
        if command_name and results:
            return results[0]
        return results
    
    def get_user_stats(self, user_id: int, time_period: Optional[timedelta] = None) -> List[Dict]:
        """Get usage statistics for a specific user"""
        query = """
            SELECT 
                command_name,
                COUNT(*) as total_uses,
                SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful_uses,
                SUM(CASE WHEN NOT success THEN 1 ELSE 0 END) as failed_uses,
                MAX(timestamp) as last_used
            FROM command_usage
            WHERE user_id = ?
        """
        params = (user_id,)
        
        if time_period:
            query += " AND timestamp >= datetime('now', ?)"
            params = params + (f"-{time_period.total_seconds()} seconds",)
        
        query += " GROUP BY command_name ORDER BY total_uses DESC"
        
        return self.db.fetch_all(query, params)
    
    def get_guild_stats(self, guild_id: int, time_period: Optional[timedelta] = None) -> List[Dict]:
        """Get usage statistics for a specific guild"""
        query = """
            SELECT 
                command_name,
                COUNT(*) as total_uses,
                SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful_uses,
                SUM(CASE WHEN NOT success THEN 1 ELSE 0 END) as failed_uses,
                MAX(timestamp) as last_used
            FROM command_usage
            WHERE guild_id = ?
        """
        params = (guild_id,)
        
        if time_period:
            query += " AND timestamp >= datetime('now', ?)"
            params = params + (f"-{time_period.total_seconds()} seconds",)
        
        query += " GROUP BY command_name ORDER BY total_uses DESC"
        
        return self.db.fetch_all(query, params)
    
    def get_error_stats(self, time_period: Optional[timedelta] = None) -> List[Dict]:
        """Get statistics about command errors"""
        query = """
            SELECT 
                command_name,
                error_message,
                COUNT(*) as error_count
            FROM command_usage
            WHERE NOT success
        """
        params = ()
        
        if time_period:
            query += " AND timestamp >= datetime('now', ?)"
            params = (f"-{time_period.total_seconds()} seconds",)
        
        query += " GROUP BY command_name, error_message ORDER BY error_count DESC"
        
        return self.db.fetch_all(query, params) 