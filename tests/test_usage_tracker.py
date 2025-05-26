import pytest
from datetime import datetime, timedelta
from robin.utils.usage_tracker import UsageTracker
from robin.utils.database import Database
import os
import time

@pytest.fixture
def db():
    # Use an in-memory database for testing
    db = Database(":memory:")
    return db

@pytest.fixture
def tracker(db):
    return UsageTracker(db)

@pytest.fixture
def usage_tracker():
    # Use a test database
    db_path = "test_usage.db"
    tracker = UsageTracker(db_path)
    yield tracker
    # Clean up after tests
    if os.path.exists(db_path):
        os.remove(db_path)

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

def test_log_command(usage_tracker):
    """Test logging command usage"""
    # Log a successful command
    usage_tracker.log_command(
        "test_command",
        user_id=123,
        guild_id=456,
        channel_id=789,
        success=True,
        execution_time=0.5
    )
    
    # Log a failed command
    usage_tracker.log_command(
        "test_command",
        user_id=123,
        guild_id=456,
        channel_id=789,
        success=False,
        error_message="Test error",
        execution_time=0.3
    )
    
    # Get stats
    stats = usage_tracker.get_command_stats()
    
    # Check stats
    assert "test_command" in stats
    assert stats["test_command"]["total_uses"] == 2
    assert stats["test_command"]["successful_uses"] == 1
    assert stats["test_command"]["success_rate"] == 50.0
    assert 0.3 <= stats["test_command"]["avg_execution_time"] <= 0.5

def test_get_command_stats_time_period(usage_tracker):
    """Test getting command stats with time period"""
    # Log commands at different times
    current_time = int(time.time())
    
    # Log command 1 hour ago
    usage_tracker.log_command(
        "old_command",
        user_id=123,
        guild_id=456,
        channel_id=789,
        success=True,
        execution_time=0.5
    )
    
    # Log command now
    usage_tracker.log_command(
        "new_command",
        user_id=123,
        guild_id=456,
        channel_id=789,
        success=True,
        execution_time=0.3
    )
    
    # Get stats for last 30 minutes
    stats = usage_tracker.get_command_stats(time_period=1800)
    
    # Check that only new command is included
    assert "new_command" in stats
    assert "old_command" not in stats

def test_get_user_stats(usage_tracker):
    """Test getting user-specific stats"""
    # Log commands for different users
    usage_tracker.log_command(
        "test_command",
        user_id=123,
        guild_id=456,
        channel_id=789,
        success=True,
        execution_time=0.5
    )
    
    usage_tracker.log_command(
        "test_command",
        user_id=456,
        guild_id=456,
        channel_id=789,
        success=True,
        execution_time=0.3
    )
    
    # Get stats for user 123
    stats = usage_tracker.get_user_stats(123)
    
    # Check stats
    assert "test_command" in stats
    assert stats["test_command"]["total_uses"] == 1
    assert stats["test_command"]["success_rate"] == 100.0

def test_get_error_stats(usage_tracker):
    """Test getting error statistics"""
    # Log commands with different errors
    usage_tracker.log_command(
        "test_command",
        user_id=123,
        guild_id=456,
        channel_id=789,
        success=False,
        error_message="Error 1",
        execution_time=0.5
    )
    
    usage_tracker.log_command(
        "test_command",
        user_id=123,
        guild_id=456,
        channel_id=789,
        success=False,
        error_message="Error 1",
        execution_time=0.3
    )
    
    usage_tracker.log_command(
        "test_command",
        user_id=123,
        guild_id=456,
        channel_id=789,
        success=False,
        error_message="Error 2",
        execution_time=0.4
    )
    
    # Get error stats
    stats = usage_tracker.get_error_stats()
    
    # Check stats
    assert "test_command" in stats
    assert "Error 1" in stats["test_command"]
    assert "Error 2" in stats["test_command"]
    assert stats["test_command"]["Error 1"] == 2
    assert stats["test_command"]["Error 2"] == 1

def test_get_usage_trends(usage_tracker):
    """Test getting usage trends"""
    # Log commands
    usage_tracker.log_command(
        "test_command",
        user_id=123,
        guild_id=456,
        channel_id=789,
        success=True,
        execution_time=0.5
    )
    
    usage_tracker.log_command(
        "test_command",
        user_id=123,
        guild_id=456,
        channel_id=789,
        success=True,
        execution_time=0.3
    )
    
    # Get trends for last 24 hours
    trends = usage_tracker.get_usage_trends()
    
    # Check trends
    assert "test_command" in trends
    current_hour = time.strftime("%H")
    assert current_hour in trends["test_command"]
    assert trends["test_command"][current_hour] == 2 