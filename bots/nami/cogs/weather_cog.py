import discord
from discord.ext import commands
from discord import app_commands, Interaction
import os
from api.weather import WeatherAPI

class WeatherCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.weather_api = WeatherAPI(os.getenv("WEATHER_API_KEY"))

    @app_commands.command(name="weather", description="Get current weather for a city")
    @app_commands.describe(city="City to get the weather for")
    async def weather(self, interaction: Interaction, city: str = None):
        city = city or os.getenv("DEFAULT_CITY", "los angeles")
        try:
            weather_data = await self.weather_api.get_current_weather(city)
            embed = discord.Embed(title=f"Weather in {city.title()}", color=discord.Color.blue())
            embed.add_field(name="Temperature", value=f"{weather_data['temperature']}°F", inline=True)
            embed.add_field(name="Description", value=weather_data['description'], inline=True)
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"Error fetching weather: {str(e)}")

async def setup(bot):
    await bot.add_cog(WeatherCog(bot))
