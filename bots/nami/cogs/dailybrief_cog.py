import discord
from discord.ext import commands
from discord import app_commands, Interaction
import os
from api.news import NewsAPI
from api.weather import WeatherAPI
from api.crypto import CryptoAPI

class DailyBriefCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.news_api = NewsAPI(os.getenv("NEWS_API_KEY"))
        self.weather_api = WeatherAPI(os.getenv("WEATHER_API_KEY"))
        self.crypto_api = CryptoAPI()

    @app_commands.command(name="dailybrief", description="Get a comprehensive daily update with news, weather, and crypto")
    async def dailybrief(self, interaction: Interaction):
        try:
            # News
            embeds, _ = await self.news_api.get_top_headlines()
            # Weather
            city = os.getenv("DEFAULT_CITY", "los angeles")
            weather_data = await self.weather_api.get_current_weather(city)
            weather_embed = discord.Embed(
                title=f"Weather in {city.title()}", color=discord.Color.blue()
            )
            weather_embed.add_field(name="Temperature", value=f"{weather_data['temperature']}°F", inline=True)
            weather_embed.add_field(name="Description", value=weather_data['description'], inline=True)
            # Crypto
            btc_data = await self.crypto_api.get_price('btc')
            crypto_embed = discord.Embed(title="BTC Price", color=discord.Color.gold())
            if btc_data and isinstance(btc_data, dict):
                price = btc_data.get('price')
                change = btc_data.get('change_24h')
                if price is not None:
                    crypto_embed.add_field(name="Price", value=f"${price:,.2f}", inline=True)
                if change is not None:
                    crypto_embed.add_field(name="24h Change", value=f"{change:.2f}%", inline=True)
            await interaction.response.send_message("☀️ Here's your Daily Brief:")
            await interaction.followup.send("📰 **Top News:**", embeds=embeds)
            await interaction.followup.send("🌤 **Weather Update:**", embed=weather_embed)
            await interaction.followup.send("💰 **Crypto Update:**", embed=crypto_embed)
        except Exception as e:
            await interaction.response.send_message(f"Error generating daily brief: {str(e)}")

async def setup(bot):
    await bot.add_cog(DailyBriefCog(bot))
