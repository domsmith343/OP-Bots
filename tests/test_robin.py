import pytest
from unittest.mock import patch, AsyncMock
import discord

@pytest.mark.asyncio
async def test_ask_command(mock_context):
    from robin.commands.ask import AskCommand
    
    with patch('robin.commands.ask.OllamaAPI') as mock_ollama:
        mock_ollama.return_value.generate.return_value = "Test response"
        command = AskCommand()
        await command.execute(mock_context, "What is Python?")
        
        mock_context.send.assert_called_once()
        assert "Test response" in mock_context.send.call_args[0][0]

@pytest.mark.asyncio
async def test_models_command(mock_context):
    from robin.commands.models import ModelsCommand
    
    with patch('robin.commands.models.OllamaAPI') as mock_ollama:
        mock_ollama.return_value.list_models.return_value = ["llama2", "mistral"]
        command = ModelsCommand()
        await command.execute(mock_context)
        
        mock_context.send.assert_called_once()
        assert "Available models" in mock_context.send.call_args[0][0]

@pytest.mark.asyncio
async def test_summarize_command(mock_context):
    from robin.commands.summarize import SummarizeCommand
    
    with patch('robin.commands.summarize.OllamaAPI') as mock_ollama:
        mock_ollama.return_value.generate.return_value = "Summary of text"
        command = SummarizeCommand()
        await command.execute(mock_context, "Long text to summarize")
        
        mock_context.send.assert_called_once()
        assert "Summary" in mock_context.send.call_args[0][0]

@pytest.mark.asyncio
async def test_format_code_command(mock_context):
    from robin.commands.ask import AskCommand
    
    command = AskCommand()
    code = "def hello():\n    print('Hello, World!')"
    await command.format_code(mock_context, "python", code=code)
    
    mock_context.send.assert_called_once()
    response = mock_context.send.call_args[0][0]
    assert "```python" in response
    assert "def hello()" in response
    assert "print('Hello, World!')" in response

@pytest.mark.asyncio
async def test_format_code_command_invalid_language(mock_context):
    from robin.commands.ask import AskCommand
    
    command = AskCommand()
    code = "print('Hello, World!')"
    await command.format_code(mock_context, "invalid_language", code=code)
    
    mock_context.send.assert_called_once()
    response = mock_context.send.call_args[0][0]
    assert "Error" in response
    assert "Failed to format code" in response

@pytest.mark.asyncio
async def test_format_code_command_empty_code(mock_context):
    from robin.commands.ask import AskCommand
    
    command = AskCommand()
    await command.format_code(mock_context, "python", code="")
    
    mock_context.send.assert_called_once()
    response = mock_context.send.call_args[0][0]
    assert "```python" in response
    assert "```" in response 