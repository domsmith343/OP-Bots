import discord
from discord.ext import commands
from ..utils.weather_api import WeatherAPI

class WeatherCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.weather_api = WeatherAPI()

    @commands.command(name="weather")
    async def weather(self, ctx, location: str):
        """Get current weather for a location"""
        weather_data = await self.weather_api.get_weather(location)
        
        embed = discord.Embed(
            title=f"Weather in {location}",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="Temperature", value=f"{weather_data['temp']}°F", inline=True)
        embed.add_field(name="Conditions", value=weather_data['description'], inline=True)
        
        await ctx.send(embed=embed) 