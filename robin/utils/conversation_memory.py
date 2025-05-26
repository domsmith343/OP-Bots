from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json
from utils.database import Database

class ConversationMemory:
    def __init__(self, db: Database, max_history: int = 10, ttl_hours: int = 24):
        self.db = db
        self.max_history = max_history
        self.ttl_hours = ttl_hours
        self._init_table()

    def _init_table(self):
        """Initialize conversation history table"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversation_history (
                    user_id INTEGER,
                    message_id INTEGER,
                    role TEXT,
                    content TEXT,
                    timestamp TIMESTAMP,
                    PRIMARY KEY (user_id, message_id)
                )
            ''')
            conn.commit()

    def add_message(self, user_id: int, role: str, content: str) -> None:
        """Add a message to the conversation history"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            timestamp = datetime.now()
            
            # Get the next message ID for this user
            cursor.execute('''
                SELECT COALESCE(MAX(message_id), 0) + 1
                FROM conversation_history
                WHERE user_id = ?
            ''', (user_id,))
            message_id = cursor.fetchone()[0]
            
            # Insert the new message
            cursor.execute('''
                INSERT INTO conversation_history (user_id, message_id, role, content, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, message_id, role, content, timestamp))
            
            # Clean up old messages
            self._cleanup_old_messages(user_id)
            
            conn.commit()

    def get_conversation_history(self, user_id: int) -> List[Dict[str, str]]:
        """Get the conversation history for a user"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT role, content
                FROM conversation_history
                WHERE user_id = ?
                ORDER BY message_id DESC
                LIMIT ?
            ''', (user_id, self.max_history))
            
            history = []
            for role, content in cursor.fetchall():
                history.append({"role": role, "content": content})
            
            return list(reversed(history))  # Return in chronological order

    def _cleanup_old_messages(self, user_id: int) -> None:
        """Remove old messages beyond max_history and expired messages"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Remove messages beyond max_history
            cursor.execute('''
                DELETE FROM conversation_history
                WHERE user_id = ? AND message_id NOT IN (
                    SELECT message_id
                    FROM conversation_history
                    WHERE user_id = ?
                    ORDER BY message_id DESC
                    LIMIT ?
                )
            ''', (user_id, user_id, self.max_history))
            
            # Remove expired messages
            expiry_time = datetime.now() - timedelta(hours=self.ttl_hours)
            cursor.execute('''
                DELETE FROM conversation_history
                WHERE timestamp < ?
            ''', (expiry_time,))
            
            conn.commit()

    def clear_history(self, user_id: int) -> None:
        """Clear conversation history for a user"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM conversation_history
                WHERE user_id = ?
            ''', (user_id,))
            conn.commit()

    def format_history_for_prompt(self, user_id: int) -> str:
        """Format conversation history for LLM prompt"""
        history = self.get_conversation_history(user_id)
        formatted = []
        
        for msg in history:
            role = "User" if msg["role"] == "user" else "Assistant"
            formatted.append(f"{role}: {msg['content']}")
        
        return "\n".join(formatted) 