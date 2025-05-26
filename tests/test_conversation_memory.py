import pytest
from utils.conversation_memory import ConversationMemory
from utils.database import Database
import os
import tempfile
from datetime import datetime, timedelta

@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    fd, path = tempfile.mkstemp()
    os.close(fd)
    db = Database(path)
    yield db
    os.unlink(path)

@pytest.fixture
def memory(temp_db):
    """Create a ConversationMemory instance with temp database"""
    return ConversationMemory(temp_db, max_history=3, ttl_hours=1)

def test_add_and_get_message(memory):
    """Test adding and retrieving messages"""
    user_id = 123
    memory.add_message(user_id, "user", "Hello")
    memory.add_message(user_id, "assistant", "Hi there!")
    
    history = memory.get_conversation_history(user_id)
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Hello"
    assert history[1]["role"] == "assistant"
    assert history[1]["content"] == "Hi there!"

def test_max_history_limit(memory):
    """Test that history is limited to max_history"""
    user_id = 123
    for i in range(5):  # Add 5 messages
        memory.add_message(user_id, "user", f"Message {i}")
    
    history = memory.get_conversation_history(user_id)
    assert len(history) == 3  # Should be limited to max_history=3

def test_clear_history(memory):
    """Test clearing conversation history"""
    user_id = 123
    memory.add_message(user_id, "user", "Hello")
    memory.add_message(user_id, "assistant", "Hi there!")
    
    memory.clear_history(user_id)
    history = memory.get_conversation_history(user_id)
    assert len(history) == 0

def test_format_history_for_prompt(memory):
    """Test formatting history for LLM prompt"""
    user_id = 123
    memory.add_message(user_id, "user", "Hello")
    memory.add_message(user_id, "assistant", "Hi there!")
    memory.add_message(user_id, "user", "How are you?")
    
    formatted = memory.format_history_for_prompt(user_id)
    expected = "User: Hello\nAssistant: Hi there!\nUser: How are you?"
    assert formatted == expected

def test_multiple_users(memory):
    """Test handling multiple users"""
    user1_id = 123
    user2_id = 456
    
    memory.add_message(user1_id, "user", "Hello from user 1")
    memory.add_message(user2_id, "user", "Hello from user 2")
    
    history1 = memory.get_conversation_history(user1_id)
    history2 = memory.get_conversation_history(user2_id)
    
    assert len(history1) == 1
    assert len(history2) == 1
    assert history1[0]["content"] == "Hello from user 1"
    assert history2[0]["content"] == "Hello from user 2" 