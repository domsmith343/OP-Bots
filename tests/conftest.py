import pytest
import discord
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture
def mock_discord_client():
    client = MagicMock(spec=discord.Client)
    client.user = MagicMock()
    client.user.id = 123456789
    return client

@pytest.fixture
def mock_message():
    message = AsyncMock(spec=discord.Message)
    message.author = MagicMock()
    message.author.id = 987654321
    message.author.name = "TestUser"
    message.channel = AsyncMock()
    message.guild = MagicMock()
    return message

@pytest.fixture
def mock_context():
    context = AsyncMock()
    context.message = mock_message()
    context.send = AsyncMock()
    return context 