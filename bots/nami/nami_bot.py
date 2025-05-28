#!/usr/bin/env python3
"""
Nami Bot - News, Weather, Crypto, and Daily Brief
"""

import os
import discord
from discord.ext import commands, tasks
from discord import Embed, ButtonStyle, SelectOption
from discord.ui import View, Button, Select
import logging
from dotenv import load_dotenv
import json
import asyncio
from datetime import datetime
from api.news import NewsAPI, NewsAPIError
from api.weather import WeatherAPI
from api.crypto import CryptoAPI
from api.sports import get_upcoming_games, get_live_scores
from db.preferences import PreferencesDB
from analytics import analytics
from typing import List

load_dotenv()

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("nami_bot")

# Load environment variables
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
DEFAULT_CITY = os.getenv("DEFAULT_CITY", "los angeles")
DEFAULT_CRYPTO = os.getenv("DEFAULT_CRYPTO", "btc")
DAILYBRIEF_CHANNEL_ID = int(os.getenv("DAILYBRIEF_CHANNEL_ID", 0))

# Rate limiting
RATE_LIMITS = {
    'news': 10,  # seconds
    'weather': 10,
    'crypto': 5,
    'dailybrief': 300  # 5 minutes
}

# Initialize API clients
news_api = NewsAPI(NEWS_API_KEY)
weather_api = WeatherAPI(WEATHER_API_KEY)
crypto_api = CryptoAPI()
db = PreferencesDB()

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# Initialize rate limiting dictionaries
bot.last_news_call = {}
bot.last_weather_call = {}
bot.last_crypto_call = {}
bot.last_dailybrief_call = {}

# Health check
@tasks.loop(minutes=5)
async def health_check():
    """Periodic health check for API endpoints"""
    try:
        # Check news API
        await news_api.get_top_headlines()
        
        # Check weather API
        await weather_api.get_weather(DEFAULT_CITY)
        
        # Check crypto API
        await crypto_api.get_price(DEFAULT_CRYPTO)
        
        logger.info("All API endpoints are healthy")
    except Exception as e:
        logger.error(f"Health check failed: {e}")

# Command error handler
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found. Use !help for available commands.")
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"Please wait {error.retry_after:.2f}s before using this command again.")
    else:
        logger.error(f"Command error in {ctx.command}: {error}")
        await ctx.send("An unexpected error occurred. Please try again later.")

COINGECKO_IDS = {
    "btc": "bitcoin",
    "eth": "ethereum",
    "sol": "solana",
    "doge": "dogecoin",
    "ada": "cardano",
    "dot": "polkadot",
    "ltc": "litecoin"
}

@bot.event
async def on_ready():
    logger.info(f"{bot.user.name} is online!")
    await bot.change_presence(activity=discord.Game(name="!help for Nami's commands"))
    try:
        synced = await bot.tree.sync()
        logger.info(f"Slash commands synced: {len(synced)} commands registered.")
    except Exception as e:
        logger.error(f"Failed to sync slash commands: {e}")
    scheduled_briefs.start()

@tasks.loop(minutes=1)
async def scheduled_briefs():
    now = datetime.now().strftime('%H:%M')
    if now in ["16:00", "22:00", "04:00"]:  # 8am, 2pm, 8pm PST
        channel = bot.get_channel(DAILYBRIEF_CHANNEL_ID)
        if channel:
            try:
                # Get news
                embeds, _ = await news_api.get_top_headlines()
                await channel.send("☀️ Here's your scheduled Daily Brief:")
                await channel.send("📰 **Top News:**", embeds=embeds)
                
                # Get weather
                weather_data = await weather_api.get_current_weather(DEFAULT_CITY)
                weather_embed = Embed(
                    title=f"Weather in {DEFAULT_CITY}",
                    color=discord.Color.blue()
                )
                weather_embed.add_field(name="Temperature", value=f"{weather_data['temperature']}°F", inline=True)
                weather_embed.add_field(name="Description", value=weather_data['description'], inline=True)
                await channel.send("🌤 **Weather Update:**", embed=weather_embed)
                
                # Get crypto (always BTC)
                btc_data = await crypto_api.get_price('btc')
                if btc_data and isinstance(btc_data, dict):
                    logger.info(f"Crypto data for BTC: {btc_data}")
                    price = btc_data.get('price')
                    change = btc_data.get('change_24h')
                    if price is not None and change is not None:
                        crypto_embed = Embed(
                            title="BTC Price",
                            color=discord.Color.gold()
                        )
                        crypto_embed.add_field(name="Price", value=f"${price:,.2f}", inline=True)
                        crypto_embed.add_field(name="24h Change", value=f"{change:.2f}%", inline=True)
                        await channel.send("💰 **Crypto Update:**", embed=crypto_embed)
                    else:
                        await channel.send(f"Unable to fetch full BTC price data (missing 'price' or 'change_24h'). Raw data: {btc_data}")
                else:
                    await channel.send(f"Unable to fetch BTC price data at the moment. Raw data: {btc_data}")
                
            except Exception as e:
                logger.error(f"Error in scheduled brief: {str(e)}")
                await channel.send(f"Error generating daily brief: {str(e)}")


            if category and category.lower() not in valid_categories:
                await ctx.send(f"Invalid category. Valid categories are: {', '.join(valid_categories)}")
                return
                
            embeds, total_results = await news_api.get_top_headlines(
                category=category.lower() if category else 'general',
                keyword=keyword
            )

        if not embeds:
            await ctx.send("No news articles found.")
            return

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        logger.error("DISCORD_TOKEN is not set.")
        exit(1)
    asyncio.run(load_cogs())
    try:
        bot.run(DISCORD_TOKEN)
    except Exception as e:
        logger.error(f"Bot error: {e}")
        print(f"Bot error: {e}")
