import pytest
from unittest.mock import patch, AsyncMock
import discord

@pytest.mark.asyncio
async def test_news_command(mock_context):
    from robin.commands.news import NewsCommand
    
    with patch('robin.commands.news.NewsAPI') as mock_news:
        mock_news.return_value.get_headlines.return_value = [
            {"title": "Test News", "url": "http://test.com"}
        ]
        command = NewsCommand()
        await command.execute(mock_context)
        
        mock_context.send.assert_called_once()
        assert "Latest News" in mock_context.send.call_args[0][0]

@pytest.mark.asyncio
async def test_weather_command(mock_context):
    from robin.commands.weather import WeatherCommand
    
    with patch('robin.commands.weather.WeatherAPI') as mock_weather:
        mock_weather.return_value.get_weather.return_value = {
            "temp": 72,
            "description": "Sunny"
        }
        command = WeatherCommand()
        await command.execute(mock_context, "Los Angeles")
        
        mock_context.send.assert_called_once()
        assert "Weather" in mock_context.send.call_args[0][0]

@pytest.mark.asyncio
async def test_crypto_command(mock_context):
    from robin.commands.crypto import CryptoCommand
    
    with patch('robin.commands.crypto.CryptoAPI') as mock_crypto:
        mock_crypto.return_value.get_price.return_value = {
            "price": 50000,
            "change_24h": 2.5
        }
        command = CryptoCommand()
        await command.execute(mock_context, "BTC")
        
        mock_context.send.assert_called_once()
        assert "Bitcoin" in mock_context.send.call_args[0][0]

@pytest.mark.asyncio
async def test_dailybrief_command(mock_context):
    from robin.commands.dailybrief import DailyBriefCommand
    
    with patch('robin.commands.dailybrief.NewsAPI') as mock_news, \
         patch('robin.commands.dailybrief.WeatherAPI') as mock_weather, \
         patch('robin.commands.dailybrief.CryptoAPI') as mock_crypto:
        
        mock_news.return_value.get_headlines.return_value = [{"title": "Test News"}]
        mock_weather.return_value.get_weather.return_value = {"temp": 72}
        mock_crypto.return_value.get_price.return_value = {"price": 50000}
        
        command = DailyBriefCommand()
        await command.execute(mock_context)
        
        mock_context.send.assert_called_once()
        assert "Daily Briefing" in mock_context.send.call_args[0][0] 