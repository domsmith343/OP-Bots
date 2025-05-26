import sqlite3
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import os
from .database import Database

class UsageTracker:
    def __init__(self, db_path: str = "data/usage.db"):
        """Initialize the usage tracker with database connection"""
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize the database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS command_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command_name TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    guild_id INTEGER,
                    channel_id INTEGER,
                    timestamp INTEGER NOT NULL,
                    success BOOLEAN NOT NULL,
                    error_message TEXT,
                    execution_time REAL
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_command_usage_timestamp 
                ON command_usage(timestamp)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_command_usage_command 
                ON command_usage(command_name)
            """)
            conn.commit()
    
    def log_command(self, command_name: str, user_id: int, guild_id: Optional[int], 
                   channel_id: Optional[int], success: bool, error_message: Optional[str] = None,
                   execution_time: Optional[float] = None):
        """Log a command usage"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO command_usage 
                (command_name, user_id, guild_id, channel_id, timestamp, success, error_message, execution_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (command_name, user_id, guild_id, channel_id, int(time.time()), 
                 success, error_message, execution_time))
            conn.commit()
    
    def get_command_stats(self, time_period: Optional[int] = None) -> Dict:
        """Get command usage statistics for a time period (in seconds)"""
        with sqlite3.connect(self.db_path) as conn:
            query = """
                SELECT 
                    command_name,
                    COUNT(*) as total_uses,
                    SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful_uses,
                    AVG(execution_time) as avg_execution_time
                FROM command_usage
            """
            params = []
            
            if time_period:
                query += " WHERE timestamp >= ?"
                params.append(int(time.time()) - time_period)
            
            query += " GROUP BY command_name ORDER BY total_uses DESC"
            
            cursor = conn.execute(query, params)
            stats = {}
            for row in cursor:
                stats[row[0]] = {
                    'total_uses': row[1],
                    'successful_uses': row[2],
                    'success_rate': (row[2] / row[1]) * 100 if row[1] > 0 else 0,
                    'avg_execution_time': row[3] if row[3] is not None else 0
                }
            return stats
    
    def get_user_stats(self, user_id: int, time_period: Optional[int] = None) -> Dict:
        """Get command usage statistics for a specific user"""
        with sqlite3.connect(self.db_path) as conn:
            query = """
                SELECT 
                    command_name,
                    COUNT(*) as total_uses,
                    SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful_uses,
                    AVG(execution_time) as avg_execution_time
                FROM command_usage
                WHERE user_id = ?
            """
            params = [user_id]
            
            if time_period:
                query += " AND timestamp >= ?"
                params.append(int(time.time()) - time_period)
            
            query += " GROUP BY command_name ORDER BY total_uses DESC"
            
            cursor = conn.execute(query, params)
            stats = {}
            for row in cursor:
                stats[row[0]] = {
                    'total_uses': row[1],
                    'successful_uses': row[2],
                    'success_rate': (row[2] / row[1]) * 100 if row[1] > 0 else 0,
                    'avg_execution_time': row[3] if row[3] is not None else 0
                }
            return stats
    
    def get_error_stats(self, time_period: Optional[int] = None) -> Dict:
        """Get error statistics for commands"""
        with sqlite3.connect(self.db_path) as conn:
            query = """
                SELECT 
                    command_name,
                    error_message,
                    COUNT(*) as error_count
                FROM command_usage
                WHERE success = 0
            """
            params = []
            
            if time_period:
                query += " AND timestamp >= ?"
                params.append(int(time.time()) - time_period)
            
            query += " GROUP BY command_name, error_message ORDER BY error_count DESC"
            
            cursor = conn.execute(query, params)
            stats = {}
            for row in cursor:
                if row[0] not in stats:
                    stats[row[0]] = {}
                stats[row[0]][row[1]] = row[2]
            return stats
    
    def get_usage_trends(self, time_period: int = 86400) -> Dict:
        """Get command usage trends over time (default: last 24 hours)"""
        with sqlite3.connect(self.db_path) as conn:
            query = """
                SELECT 
                    command_name,
                    strftime('%H', datetime(timestamp, 'unixepoch')) as hour,
                    COUNT(*) as use_count
                FROM command_usage
                WHERE timestamp >= ?
                GROUP BY command_name, hour
                ORDER BY hour
            """
            cursor = conn.execute(query, (int(time.time()) - time_period,))
            
            trends = {}
            for row in cursor:
                if row[0] not in trends:
                    trends[row[0]] = {}
                trends[row[0]][row[1]] = row[2]
            return trends

    def track_command(self, command_name: str, user_id: int, guild_id: Optional[int] = None,
                     channel_id: Optional[int] = None, success: bool = True,
                     error_message: Optional[str] = None):
        """Track a command usage"""
        # Record individual usage
        self.log_command(command_name, user_id, guild_id, channel_id, success, error_message)
        
        # Update command stats
        self.log_command(command_name, user_id, guild_id, channel_id, success, None, 0.0)
    
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
    
    def get_guild_stats(self, guild_id: int, time_period: Optional[int] = None) -> List[Dict]:
        """Get command usage statistics for a specific guild
        
        Args:
            guild_id: The ID of the guild to get stats for
            time_period: Optional time period in seconds to filter stats
            
        Returns:
            List of dictionaries containing command usage statistics
        """
        try:
            query = """
                SELECT 
                    command_name,
                    user_id,
                    channel_id,
                    COUNT(*) as total_uses,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_uses,
                    SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failed_uses,
                    AVG(execution_time) as avg_execution_time,
                    MAX(timestamp) as last_used
                FROM command_usage
                WHERE guild_id = ?
            """
            params = [guild_id]
            
            if time_period:
                query += " AND timestamp >= datetime('now', ?)"
                params.append(f'-{time_period} seconds')
            
            query += " GROUP BY command_name, user_id, channel_id"
            
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            
            stats = []
            for row in cursor.fetchall():
                stats.append({
                    'command_name': row[0],
                    'user_id': row[1],
                    'channel_id': row[2],
                    'total_uses': row[3],
                    'successful_uses': row[4],
                    'failed_uses': row[5],
                    'avg_execution_time': row[6],
                    'last_used': row[7]
                })
            
            return stats
            
        except Exception as e:
            print(f"Error getting guild stats: {str(e)}")
            return []
    
    def get_time_of_day_stats(self, time_period: Optional[int] = None) -> Dict:
        """Get command usage statistics by time of day
        
        Args:
            time_period: Optional time period in seconds to filter stats
            
        Returns:
            Dictionary containing usage counts by hour of day
        """
        try:
            query = """
                SELECT 
                    strftime('%H', datetime(timestamp, 'unixepoch')) as hour,
                    COUNT(*) as use_count
                FROM command_usage
            """
            params = []
            
            if time_period:
                query += " WHERE timestamp >= ?"
                params.append(int(time.time()) - time_period)
            
            query += " GROUP BY hour ORDER BY hour"
            
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            
            # Initialize all hours with 0
            stats = {f"{i:02d}": 0 for i in range(24)}
            
            # Update with actual counts
            for row in cursor.fetchall():
                stats[row[0]] = row[1]
            
            return stats
            
        except Exception as e:
            print(f"Error getting time of day stats: {str(e)}")
            return {} 