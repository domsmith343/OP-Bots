import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import discord
from discord.ext import commands
from robin.utils.help_system import HelpSystem
from robin.utils.pagination import PaginationView, Paginator

@pytest.fixture
def mock_bot():
    bot = MagicMock()
    bot.command_prefix = "!"
    return bot

@pytest.fixture
def mock_context():
    context = AsyncMock()
    context.author = AsyncMock()
    context.author.id = 123456789
    context.guild = AsyncMock()
    context.guild.id = 987654321
    return context

@pytest.fixture
def help_system(mock_bot):
    return HelpSystem(mock_bot)

def test_get_command_help(help_system):
    """Test getting help for a specific command"""
    # Create a mock command
    command = MagicMock()
    command.name = "test"
    command.signature = "arg1 arg2"
    command.help = "Test command help"
    command.aliases = ["t", "testcmd"]
    command.examples = ["test arg1 arg2", "test -v"]
    command._buckets = MagicMock()
    command._buckets._cooldown = MagicMock()
    command._buckets._cooldown.per = 5
    
    # Get help embed
    embed = help_system.get_command_help(command)
    
    # Check embed content
    assert embed.title == "Command: test"
    assert "Test command help" in embed.description
    assert "Aliases: t, testcmd" in embed.description
    assert "Examples:" in embed.description
    assert "!test arg1 arg2" in embed.description
    assert "Cooldown: 5 seconds" in embed.description
    assert embed.fields[0].name == "Usage"
    assert embed.fields[0].value == "`!test arg1 arg2`"

def test_get_cog_help(help_system):
    """Test getting help for a cog"""
    # Create a mock cog with commands
    cog = MagicMock()
    cog.qualified_name = "TestCog"
    cog.description = "Test cog description"
    
    command1 = MagicMock()
    command1.name = "cmd1"
    command1.short_doc = "Command 1 help"
    command1.hidden = False
    
    command2 = MagicMock()
    command2.name = "cmd2"
    command2.short_doc = "Command 2 help"
    command2.hidden = False
    
    cog.get_commands.return_value = [command1, command2]
    
    # Get help embed
    embed = help_system.get_cog_help(cog)
    
    # Check embed content
    assert embed.title == "Category: TestCog"
    assert "Test cog description" in embed.description
    assert "Commands:" in embed.description
    assert "`cmd1` - Command 1 help" in embed.description
    assert "`cmd2` - Command 2 help" in embed.description

@pytest.mark.asyncio
async def test_get_all_commands_help(help_system, mock_context):
    """Test getting help for all commands"""
    # Create mock cogs and commands
    cog1 = MagicMock()
    cog1.get_commands.return_value = [
        MagicMock(name="cmd1", short_doc="Command 1", hidden=False, can_run=AsyncMock(return_value=True)),
        MagicMock(name="cmd2", short_doc="Command 2", hidden=False, can_run=AsyncMock(return_value=True))
    ]
    
    cog2 = MagicMock()
    cog2.get_commands.return_value = [
        MagicMock(name="cmd3", short_doc="Command 3", hidden=False, can_run=AsyncMock(return_value=True))
    ]
    
    help_system.bot.cogs = {
        "Cog1": cog1,
        "Cog2": cog2
    }
    
    # Get help embeds
    embeds = await help_system.get_all_commands_help(mock_context)
    
    # Check embeds
    assert len(embeds) > 0
    assert "Available Commands:" in embeds[0].description
    assert "`cmd1` - Command 1" in embeds[0].description
    assert "`cmd2` - Command 2" in embeds[0].description
    assert "`cmd3` - Command 3" in embeds[0].description

def test_get_command_categories(help_system):
    """Test getting command categories"""
    # Create mock cogs and commands
    cog1 = MagicMock()
    cog1.qualified_name = "Cog1"
    cog1.get_commands.return_value = [
        MagicMock(name="cmd1", hidden=False),
        MagicMock(name="cmd2", hidden=False)
    ]
    
    cog2 = MagicMock()
    cog2.qualified_name = "Cog2"
    cog2.get_commands.return_value = [
        MagicMock(name="cmd3", hidden=False)
    ]
    
    help_system.bot.cogs = {
        "Cog1": cog1,
        "Cog2": cog2
    }
    
    # Get categories
    categories = help_system.get_command_categories()
    
    # Check categories
    assert "Cog1" in categories
    assert "Cog2" in categories
    assert len(categories["Cog1"]) == 2
    assert len(categories["Cog2"]) == 1

@pytest.mark.asyncio
async def test_pagination_view():
    """Test pagination view functionality"""
    # Create mock embeds
    embeds = [
        discord.Embed(title=f"Page {i}", description=f"Content {i}")
        for i in range(3)
    ]
    
    # Create view
    view = PaginationView(embeds)
    
    # Check initial state
    assert view.current_page == 0
    assert view.total_pages == 3
    assert not view.first_page.disabled
    assert not view.prev_page.disabled
    assert not view.next_page.disabled
    assert not view.last_page.disabled
    
    # Test button states after moving to last page
    view.current_page = 2
    view.update_buttons()
    assert view.first_page.disabled
    assert view.prev_page.disabled
    assert view.next_page.disabled
    assert view.last_page.disabled

@pytest.mark.asyncio
async def test_paginator(mock_context):
    """Test paginator functionality"""
    # Create mock bot and paginator
    bot = MagicMock()
    paginator = Paginator(bot)
    
    # Create mock embeds
    embeds = [
        discord.Embed(title=f"Page {i}", description=f"Content {i}")
        for i in range(3)
    ]
    
    # Test pagination
    with patch('discord.ui.View.wait', new_callable=AsyncMock):
        await paginator.paginate(mock_context, embeds)
    
    # Check that message was sent
    mock_context.send.assert_called_once()
    assert isinstance(mock_context.send.call_args[1]['view'], PaginationView) 