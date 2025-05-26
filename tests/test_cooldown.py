import pytest
from unittest.mock import AsyncMock, patch
import time
from robin.utils.cooldown import CooldownManager, CooldownError, cooldown

@pytest.fixture
def mock_context():
    context = AsyncMock()
    context.author.id = 123456789
    return context

def test_cooldown_manager_initialization():
    manager = CooldownManager()
    assert manager._cooldowns == {}

def test_get_remaining_time_no_cooldown():
    manager = CooldownManager()
    remaining = manager.get_remaining_time("test_command", 123456789, 3)
    assert remaining is None

def test_get_remaining_time_with_cooldown():
    manager = CooldownManager()
    manager.update_cooldown("test_command", 123456789)
    remaining = manager.get_remaining_time("test_command", 123456789, 3)
    assert remaining is not None
    assert remaining <= 3

def test_update_cooldown():
    manager = CooldownManager()
    manager.update_cooldown("test_command", 123456789)
    assert "test_command" in manager._cooldowns
    assert 123456789 in manager._cooldowns["test_command"]

def test_format_cooldown_message():
    manager = CooldownManager()
    message = manager.format_cooldown_message(2.5)
    assert "2 seconds" in message
    
    message = manager.format_cooldown_message(0.5)
    assert "0.5 seconds" in message

@pytest.mark.asyncio
async def test_cooldown_decorator(mock_context):
    class TestCog:
        @cooldown(2)
        async def test_command(self, ctx):
            return "Success"
    
    cog = TestCog()
    
    # First call should succeed
    result = await cog.test_command(mock_context)
    assert result == "Success"
    
    # Second call should raise CooldownError
    with pytest.raises(CooldownError):
        await cog.test_command(mock_context)

@pytest.mark.asyncio
async def test_cooldown_error_message(mock_context):
    class TestCog:
        @cooldown(2)
        async def test_command(self, ctx):
            return "Success"
    
    cog = TestCog()
    
    # First call
    await cog.test_command(mock_context)
    
    # Second call should raise error with proper message
    with pytest.raises(CooldownError) as exc_info:
        await cog.test_command(mock_context)
    
    assert "Command is on cooldown" in str(exc_info.value)
    assert "seconds" in str(exc_info.value)

@pytest.mark.asyncio
async def test_cooldown_expiration(mock_context):
    class TestCog:
        @cooldown(1)
        async def test_command(self, ctx):
            return "Success"
    
    cog = TestCog()
    
    # First call
    await cog.test_command(mock_context)
    
    # Wait for cooldown to expire
    time.sleep(1.1)
    
    # Should succeed after cooldown expires
    result = await cog.test_command(mock_context)
    assert result == "Success" 