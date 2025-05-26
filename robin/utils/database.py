import sqlite3
from typing import Optional, List, Dict, Any

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS command_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                command_name TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                guild_id INTEGER,
                channel_id INTEGER,
                success BOOLEAN NOT NULL,
                error_message TEXT,
                execution_time REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()
    
    def execute(self, query: str, params: tuple = ()) -> None:
        """Execute a query"""
        self.cursor.execute(query, params)
        self.conn.commit()
    
    def fetch_one(self, query: str, params: tuple = ()) -> Optional[tuple]:
        """Fetch one row"""
        self.cursor.execute(query, params)
        return self.cursor.fetchone()
    
    def fetch_all(self, query: str, params: tuple = ()) -> List[tuple]:
        """Fetch all rows"""
        self.cursor.execute(query, params)
        return self.cursor.fetchall()
    
    def close(self):
        """Close database connection"""
        self.conn.close() 