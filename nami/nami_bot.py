#!/usr/bin/env python3
"""
Nami Bot - News, Weather, Crypto, and Daily Brief
"""

import os
import discord
from discord.ext import commands
import requests
import logging
from dotenv import load_dotenv

load_dotenv()

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nami_bot")

# Load environment variables
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
DEFAULT_CITY = os.getenv("DEFAULT_CITY", "los angeles")
DEFAULT_CRYPTO = os.getenv("DEFAULT_CRYPTO", "btc")

COINGECKO_IDS = {
    "btc": "bitcoin",
    "eth": "ethereum",
    "sol": "solana",
    "doge": "dogecoin",
    "ada": "cardano",
    "dot": "polkadot",
    "ltc": "litecoin"
}

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

@bot.event
async def on_ready():
    logger.info(f"{bot.user.name} is online!")
    await bot.change_presence(activity=discord.Game(name="!help for Nami's commands"))

@bot.command(name="help")
async def help_command(ctx):
    embed = discord.Embed(title="Nami Bot Commands", color=discord.Color.green())
    embed.add_field(name="!news", value="Get the latest US news headlines.", inline=False)
    embed.add_field(name="!weather <city>", value="Get current weather for a city.", inline=False)
    embed.add_field(name="!crypto <symbol>", value="Get current price for a crypto.", inline=False)
    embed.add_field(name="!dailybrief", value="Get top news, weather, and crypto update.", inline=False)
    await ctx.send(embed=embed)

@bot.command(name="news")
async def news(ctx):
    if not NEWS_API_KEY:
        return await ctx.send("News API key not set.")
    url = f"https://newsapi.org/v2/top-headlines?country=us&category=general&apiKey={NEWS_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            articles = response.json().get("articles", [])[:5]
            if not articles:
                return await ctx.send("No news found.")
            headlines = "\n\n".join([f"**{a['title']}**\n{a['url']}" for a in articles])
            await ctx.send(f"📰 **Top News:**\n\n{headlines}")
        else:
            await ctx.send(f"News fetch error: {response.status_code}")
    except Exception as e:
        await ctx.send(f"News error: {e}")

@bot.command(name="weather")
async def weather(ctx, *, city: str = None):
    if not WEATHER_API_KEY:
        return await ctx.send("Weather API key not set.")
    if not city:
        city = DEFAULT_CITY
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=imperial"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            data = res.json()
            name = data['name']
            temp = data['main']['temp']
            desc = data['weather'][0]['description'].capitalize()
            await ctx.send(f"🌤 **{name}**: {temp}°F, {desc}")
        else:
            await ctx.send(f"Weather fetch error: {res.status_code}")
    except Exception as e:
        await ctx.send(f"Weather error: {e}")

@bot.command(name="crypto")
async def crypto(ctx, symbol: str = None):
    if not symbol:
        symbol = DEFAULT_CRYPTO
    symbol = symbol.lower()
    coingecko_id = COINGECKO_IDS.get(symbol)

    if not coingecko_id:
        return await ctx.send(f"❌ Unknown crypto symbol: `{symbol}`")

    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id}&vs_currencies=usd"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            data = res.json()
            price = data.get(coingecko_id, {}).get("usd")
            if price is not None:
                await ctx.send(f"📈 **{symbol.upper()}**: ${price:,.2f}")
            else:
                await ctx.send(f"Symbol '{symbol}' not found.")
        else:
            await ctx.send(f"Crypto fetch error: {res.status_code}")
    except Exception as e:
        await ctx.send(f"Crypto error: {e}")

@bot.command(name="dailybrief")
async def dailybrief(ctx):
    await ctx.send("☀️ Here's your Daily Brief...")
    await news(ctx)
    await weather(ctx)
    await crypto(ctx)

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        logger.error("DISCORD_TOKEN is not set.")
        exit(1)
    try:
        bot.run(DISCORD_TOKEN)
    except Exception as e:
        logger.error(f"Bot error: {e}")
        print(f"Bot error: {e}")
