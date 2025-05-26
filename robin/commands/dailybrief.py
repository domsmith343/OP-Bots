import discord
from discord.ext import commands
from ..utils.news_api import NewsAPI
from ..utils.weather_api import WeatherAPI
from ..utils.crypto_api import CryptoAPI

class DailyBriefCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.news_api = NewsAPI()
        self.weather_api = WeatherAPI()
        self.crypto_api = CryptoAPI()

    @commands.command(name="dailybrief")
    async def dailybrief(self, ctx, location: str = "New York"):
        """Get a daily briefing with news, weather, and crypto updates"""
        # Get news headlines
        headlines = await self.news_api.get_headlines()
        
        # Get weather
        weather = await self.weather_api.get_weather(location)
        
        # Get crypto prices
        btc = await self.crypto_api.get_price("bitcoin")
        eth = await self.crypto_api.get_price("ethereum")
        
        embed = discord.Embed(
            title="Daily Briefing",
            color=discord.Color.blue()
        )
        
        # Add news section
        news_text = "\n".join([f"• {h['title']}" for h in headlines[:3]])
        embed.add_field(name="📰 Top News", value=news_text, inline=False)
        
        # Add weather section
        weather_text = f"Temperature: {weather['temp']}°F\nConditions: {weather['description']}"
        embed.add_field(name="🌤️ Weather", value=weather_text, inline=True)
        
        # Add crypto section
        crypto_text = f"BTC: ${btc['price']:,.2f} ({btc['change_24h']:+.2f}%)\nETH: ${eth['price']:,.2f} ({eth['change_24h']:+.2f}%)"
        embed.add_field(name="💰 Crypto", value=crypto_text, inline=True)
        
        await ctx.send(embed=embed) 