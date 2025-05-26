import pytest
from datetime import datetime, timedelta
from robin.utils.usage_tracker import UsageTracker
from robin.utils.database import Database
import os

@pytest.fixture
def db():
    # Use an in-memory database for testing
    db = Database(":memory:")
    return db

@pytest.fixture
def tracker(db):
    return UsageTracker(db)

def test_track_command(tracker):
    """Test tracking a successful command usage"""
    tracker.track_command("test_command", 123456789, 987654321, 456789123)
    
    stats = tracker.get_command_stats("test_command")
    assert stats["command_name"] == "test_command"
    assert stats["total_uses"] == 1
    assert stats["successful_uses"] == 1
    assert stats["failed_uses"] == 0

def test_track_failed_command(tracker):
    """Test tracking a failed command usage"""
    tracker.track_command(
        "test_command",
        123456789,
        987654321,
        456789123,
        success=False,
        error_message="Test error"
    )
    
    stats = tracker.get_command_stats("test_command")
    assert stats["command_name"] == "test_command"
    assert stats["total_uses"] == 1
    assert stats["successful_uses"] == 0
    assert stats["failed_uses"] == 1

def test_get_command_stats_time_period(tracker):
    """Test getting command stats for a specific time period"""
    # Track command usage
    tracker.track_command("test_command", 123456789)
    
    # Get stats for last hour
    stats = tracker.get_command_stats("test_command", timedelta(hours=1))
    assert stats["total_uses"] == 1
    
    # Get stats for last second (should be 0)
    stats = tracker.get_command_stats("test_command", timedelta(seconds=1))
    assert stats["total_uses"] == 0

def test_get_user_stats(tracker):
    """Test getting user statistics"""
    # Track multiple commands for a user
    tracker.track_command("command1", 123456789)
    tracker.track_command("command2", 123456789)
    tracker.track_command("command1", 123456789, success=False)
    
    stats = tracker.get_user_stats(123456789)
    assert len(stats) == 2
    
    # Check command1 stats
    command1_stats = next(stat for stat in stats if stat["command_name"] == "command1")
    assert command1_stats["total_uses"] == 2
    assert command1_stats["successful_uses"] == 1
    assert command1_stats["failed_uses"] == 1
    
    # Check command2 stats
    command2_stats = next(stat for stat in stats if stat["command_name"] == "command2")
    assert command2_stats["total_uses"] == 1
    assert command2_stats["successful_uses"] == 1
    assert command2_stats["failed_uses"] == 0

def test_get_guild_stats(tracker):
    """Test getting guild statistics"""
    # Track commands in a guild
    tracker.track_command("command1", 123456789, guild_id=987654321)
    tracker.track_command("command2", 123456789, guild_id=987654321)
    tracker.track_command("command1", 123456789, guild_id=987654321, success=False)
    
    stats = tracker.get_guild_stats(987654321)
    assert len(stats) == 2
    
    # Check command1 stats
    command1_stats = next(stat for stat in stats if stat["command_name"] == "command1")
    assert command1_stats["total_uses"] == 2
    assert command1_stats["successful_uses"] == 1
    assert command1_stats["failed_uses"] == 1
    
    # Check command2 stats
    command2_stats = next(stat for stat in stats if stat["command_name"] == "command2")
    assert command2_stats["total_uses"] == 1
    assert command2_stats["successful_uses"] == 1
    assert command2_stats["failed_uses"] == 0

def test_get_error_stats(tracker):
    """Test getting error statistics"""
    # Track commands with errors
    tracker.track_command("command1", 123456789, success=False, error_message="Error 1")
    tracker.track_command("command1", 123456789, success=False, error_message="Error 1")
    tracker.track_command("command2", 123456789, success=False, error_message="Error 2")
    
    stats = tracker.get_error_stats()
    assert len(stats) == 2
    
    # Check error counts
    error1_stats = next(stat for stat in stats if stat["error_message"] == "Error 1")
    assert error1_stats["error_count"] == 2
    
    error2_stats = next(stat for stat in stats if stat["error_message"] == "Error 2")
    assert error2_stats["error_count"] == 1

def test_multiple_users(tracker):
    """Test tracking commands from multiple users"""
    # Track commands from different users
    tracker.track_command("command1", 123456789)
    tracker.track_command("command1", 987654321)
    tracker.track_command("command2", 123456789)
    
    # Check user1 stats
    user1_stats = tracker.get_user_stats(123456789)
    assert len(user1_stats) == 2
    assert sum(stat["total_uses"] for stat in user1_stats) == 2
    
    # Check user2 stats
    user2_stats = tracker.get_user_stats(987654321)
    assert len(user2_stats) == 1
    assert sum(stat["total_uses"] for stat in user2_stats) == 1 