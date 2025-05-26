from typing import List, Dict, Optional
from datetime import datetime, timedelta
from .database import Database

class ConversationMemory:
    def __init__(self, db: Database, max_history: int = 10, ttl_hours: int = 24):
        self.db = db
        self.max_history = max_history
        self.ttl_hours = ttl_hours
        self._init_db()

    def _init_db(self):
        """Initialize conversation history table"""
        self.db.execute('''
            CREATE TABLE IF NOT EXISTS conversation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

    def add_message(self, user_id: int, role: str, content: str):
        """Add a message to conversation history"""
        self.db.execute(
            'INSERT INTO conversation_history (user_id, role, content) VALUES (?, ?, ?)',
            (user_id, role, content)
        )
        self._cleanup_old_messages(user_id)

    def get_conversation_history(self, user_id: int) -> List[Dict]:
        """Get conversation history for a user"""
        rows = self.db.fetch_all(
            'SELECT role, content FROM conversation_history WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?',
            (user_id, self.max_history)
        )
        return [{"role": role, "content": content} for role, content in reversed(rows)]

    def clear_history(self, user_id: int):
        """Clear conversation history for a user"""
        self.db.execute('DELETE FROM conversation_history WHERE user_id = ?', (user_id,))

    def format_history_for_prompt(self, user_id: int) -> str:
        """Format conversation history for LLM prompt"""
        history = self.get_conversation_history(user_id)
        return "\n".join(f"{msg['role'].capitalize()}: {msg['content']}" for msg in history)

    def _cleanup_old_messages(self, user_id: int):
        """Remove messages older than TTL"""
        cutoff = datetime.now() - timedelta(hours=self.ttl_hours)
        self.db.execute(
            'DELETE FROM conversation_history WHERE user_id = ? AND timestamp < ?',
            (user_id, cutoff)
        ) 