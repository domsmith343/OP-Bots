import sqlite3
import json
from typing import Any, Dict, Optional
import os
from datetime import datetime, timedelta
from contextlib import contextmanager

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def get_connection(self):
        """Get a database connection with automatic closing"""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        """Initialize database tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # User preferences table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_preferences (
                    user_id INTEGER PRIMARY KEY,
                    default_city TEXT,
                    default_crypto TEXT,
                    news_categories TEXT,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP
                )
            ''')
            
            # Cache table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    expires_at TIMESTAMP
                )
            ''')
            
            conn.commit()

    def set_user_preference(self, user_id: int, key: str, value: Any) -> None:
        """Set a user preference"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if user exists
            cursor.execute('SELECT user_id FROM user_preferences WHERE user_id = ?', (user_id,))
            exists = cursor.fetchone()
            
            if exists:
                cursor.execute(f'''
                    UPDATE user_preferences 
                    SET {key} = ?, updated_at = ?
                    WHERE user_id = ?
                ''', (json.dumps(value), datetime.now(), user_id))
            else:
                cursor.execute('''
                    INSERT INTO user_preferences (user_id, created_at, updated_at)
                    VALUES (?, ?, ?)
                ''', (user_id, datetime.now(), datetime.now()))
                
                # Update the specific preference
                cursor.execute(f'''
                    UPDATE user_preferences 
                    SET {key} = ?
                    WHERE user_id = ?
                ''', (json.dumps(value), user_id))
            
            conn.commit()

    def get_user_preference(self, user_id: int, key: str) -> Optional[Any]:
        """Get a user preference"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'SELECT {key} FROM user_preferences WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            
            if result and result[0]:
                return json.loads(result[0])
            return None

    def set_cache(self, key: str, value: Any, ttl_seconds: int = 3600) -> None:
        """Set a cache value with TTL"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            expires_at = datetime.now() + timedelta(seconds=ttl_seconds)
            
            cursor.execute('''
                INSERT OR REPLACE INTO cache (key, value, expires_at)
                VALUES (?, ?, ?)
            ''', (key, json.dumps(value), expires_at))
            
            conn.commit()

    def get_cache(self, key: str) -> Optional[Any]:
        """Get a cache value if not expired"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT value FROM cache 
                WHERE key = ? AND expires_at > ?
            ''', (key, datetime.now()))
            
            result = cursor.fetchone()
            if result:
                return json.loads(result[0])
            return None

    def clear_expired_cache(self) -> None:
        """Clear expired cache entries"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM cache WHERE expires_at <= ?', (datetime.now(),))
            conn.commit() 