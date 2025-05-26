import discord
from typing import List, Dict, Any, Optional
from datetime import datetime

class EmbedBuilder:
    @staticmethod
    def create_news_embed(articles: List[Dict[str, Any]]) -> discord.Embed:
        """Create a rich embed for news articles"""
        embed = discord.Embed(
            title="📰 Latest News",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        for article in articles[:5]:  # Limit to 5 articles
            embed.add_field(
                name=article['title'],
                value=f"[Read More]({article['url']})",
                inline=False
            )
        
        return embed

    @staticmethod
    def create_weather_embed(weather_data: Dict[str, Any]) -> discord.Embed:
        """Create a rich embed for weather information"""
        embed = discord.Embed(
            title=f"🌤 Weather in {weather_data['city']}",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="Temperature",
            value=f"{weather_data['temp']}°C",
            inline=True
        )
        embed.add_field(
            name="Conditions",
            value=weather_data['description'],
            inline=True
        )
        embed.add_field(
            name="Humidity",
            value=f"{weather_data['humidity']}%",
            inline=True
        )
        
        return embed

    @staticmethod
    def create_crypto_embed(crypto_data: Dict[str, Any]) -> discord.Embed:
        """Create a rich embed for cryptocurrency information"""
        embed = discord.Embed(
            title=f"💰 {crypto_data['name']} ({crypto_data['symbol'].upper()})",
            color=discord.Color.gold(),
            timestamp=datetime.now()
        )
        
        price_change = crypto_data['change_24h']
        color = discord.Color.green() if price_change >= 0 else discord.Color.red()
        embed.color = color
        
        embed.add_field(
            name="Price",
            value=f"${crypto_data['price']:,.2f}",
            inline=True
        )
        embed.add_field(
            name="24h Change",
            value=f"{price_change:+.2f}%",
            inline=True
        )
        
        return embed

    @staticmethod
    def create_help_embed(commands: List[Dict[str, str]]) -> discord.Embed:
        """Create a rich embed for command help"""
        embed = discord.Embed(
            title="🤖 Bot Commands",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        for cmd in commands:
            embed.add_field(
                name=cmd['name'],
                value=cmd['description'],
                inline=False
            )
        
        return embed

    @staticmethod
    def create_error_embed(title: str, description: str) -> discord.Embed:
        """Create a rich embed for error messages"""
        return discord.Embed(
            title=f"❌ {title}",
            description=description,
            color=discord.Color.red(),
            timestamp=datetime.now()
        )

    @staticmethod
    def create_success_embed(title: str, description: str) -> discord.Embed:
        """Create a rich embed for success messages"""
        return discord.Embed(
            title=f"✅ {title}",
            description=description,
            color=discord.Color.green(),
            timestamp=datetime.now()
        ) 