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
    scheduled_briefs.start()

@tasks.loop(minutes=1)
async def scheduled_briefs():
    now = datetime.now().strftime('%H:%M')
    if now in ["08:00", "14:00", "20:00"]:
        channel = bot.get_channel(DAILYBRIEF_CHANNEL_ID)
        if channel:
            await channel.send("☀️ Here's your scheduled Daily Brief:")
            await news(channel)
            await weather(channel)
            await crypto(channel)

@bot.command(name="help")
async def help_command(ctx):
    embed = discord.Embed(title="Nami Bot Commands", color=discord.Color.green())
    embed.add_field(name="!news [keyword]", value="Get the latest US news headlines. Optional keyword search.", inline=False)
    embed.add_field(name="!weather <city>", value="Get current weather for a city.", inline=False)
    embed.add_field(name="!crypto <symbol>", value="Get current price for a crypto.", inline=False)
    embed.add_field(name="!dailybrief", value="Get top news, weather, and crypto update.", inline=False)
    embed.add_field(name="!setprefs", value="Configure your daily brief preferences.", inline=False)
    embed.add_field(name="!togglebrief", value="Toggle daily brief notifications.", inline=False)
    await ctx.send(embed=embed)

@bot.command(name="news")
async def news(ctx, *, keyword: str = None):
    """Get top news headlines with optional keyword search"""
    user_id = ctx.author.id
    preferences = db.get_user_preferences(user_id)
    
    # Check rate limit
    last_call = ctx.bot.last_news_call.get(user_id)
    if last_call and (datetime.now() - last_call).total_seconds() < RATE_LIMITS['news']:
        await ctx.send("Please wait a moment before requesting news again.")
        return
    ctx.bot.last_news_call[user_id] = datetime.now()

    try:
        # Use user's preferred sources if set and not "all"
        sources = preferences.get('preferred_sources')
        if sources and sources != "all":
            embeds, total_results = await news_api.get_article_by_source(sources, keyword=keyword)
        else:
            embeds, total_results = await news_api.get_top_headlines(keyword=keyword)

        if not embeds:
            await ctx.send("No news articles found.")
            return

        # Create pagination if more than 5 articles
        if total_results > 5:
            class NewsPagination(View):
                def __init__(self, embeds):
                    super().__init__(timeout=60)
                    self.embeds = embeds
                    self.current_page = 0
                    self.message = None

                @discord.ui.button(label="Previous", style=ButtonStyle.primary)
                async def previous(self, interaction: discord.Interaction, button: Button):
                    await interaction.response.defer()
                    if self.current_page > 0:
                        self.current_page -= 1
                        await self.message.edit(embed=self.embeds[self.current_page])

                @discord.ui.button(label="Next", style=ButtonStyle.primary)
                async def next(self, interaction: discord.Interaction, button: Button):
                    await interaction.response.defer()
                    if self.current_page < len(self.embeds) - 1:
                        self.current_page += 1
                        await self.message.edit(embed=self.embeds[self.current_page])

            view = NewsPagination(embeds)
            view.message = await ctx.send(embed=embeds[0], view=view)
            await ctx.send(f"Found {total_results} articles. Use buttons to navigate.")
        else:
            # Send articles as Discord embeds
            for embed in embeds:
                await ctx.send(embed=embed)

        # Log command usage
        analytics.log_command("news", user_id)
        
    except NewsAPIError as e:
        analytics.log_error("news", str(e), user_id)
        await ctx.send(f"Error fetching news: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in news command: {e}")
        analytics.log_error("news", str(e), user_id)
        await ctx.send("An unexpected error occurred while fetching news.")

@bot.command(name="weather")
async def weather(ctx, *, city: str = None):
    """Get current weather for a city"""
    user_id = ctx.author.id
    preferences = db.get_user_preferences(user_id)
    
    # Check rate limit
    last_call = ctx.bot.last_weather_call.get(user_id)
    if last_call and (datetime.now() - last_call).total_seconds() < RATE_LIMITS['weather']:
        await ctx.send("Please wait a moment before requesting weather again.")
        return
    ctx.bot.last_weather_call[user_id] = datetime.now()

    try:
        if not city:
            city = preferences.get('preferred_location', DEFAULT_CITY)
        weather_data = await weather_api.get_current_weather(city)
        
        embed = Embed(
            title=f"Weather in {weather_data['name']}",
            color=discord.Color.blue()
        )
        embed.add_field(name="Temperature", value=f"{weather_data['temperature']}°F", inline=True)
        embed.add_field(name="Description", value=weather_data['description'], inline=True)
        embed.add_field(name="Humidity", value=f"{weather_data['humidity']}%", inline=True)
        embed.add_field(name="Wind", value=f"{weather_data['wind_speed']} mph", inline=True)
        
        if 'icon' in weather_data:
            icon_url = f"http://openweathermap.org/img/wn/{weather_data['icon']}@2x.png"
            embed.set_thumbnail(url=icon_url)
        
        await ctx.send(embed=embed)
        
        # Log command usage
        analytics.log_command("weather", user_id)
        
    except Exception as e:
        logger.error(f"Weather error for user {user_id}: {str(e)}")
        analytics.log_error("weather", str(e), user_id)
        await ctx.send(f"Error fetching weather: {str(e)}")

@bot.command(name="crypto")
async def crypto(ctx, symbol: str = None):
    """Get current cryptocurrency price"""
    user_id = ctx.author.id
    preferences = db.get_user_preferences(user_id)
    
    # Check rate limit
    last_call = ctx.bot.last_crypto_call.get(user_id)
    if last_call and (datetime.now() - last_call).total_seconds() < RATE_LIMITS['crypto']:
        await ctx.send("Please wait a moment before requesting crypto prices again.")
        return
    ctx.bot.last_crypto_call[user_id] = datetime.now()

    try:
        if not symbol:
            symbol = preferences.get('preferred_crypto', DEFAULT_CRYPTO)
        symbol = symbol.lower()
        
        price_data = await crypto_api.get_price(symbol)
        if not price_data:
            await ctx.send(f"Unknown cryptocurrency symbol: {symbol}")
            return
            
        embed = Embed(
            title=f"{symbol.upper()} Price",
            color=discord.Color.gold()
        )
        embed.add_field(name="Price", value=f"${price_data['usd']:,.2f}", inline=True)
        embed.add_field(name="24h Change", value=f"{price_data['usd_24h_change']:.2f}%", inline=True)
        embed.set_footer(text="Data from CoinGecko")
        
        await ctx.send(embed=embed)
        
        # Log command usage
        analytics.log_command("crypto", user_id)
        
    except Exception as e:
        logger.error(f"Crypto error for user {user_id}: {str(e)}")
        analytics.log_error("crypto", str(e), user_id)
        await ctx.send(f"Error fetching crypto data: {str(e)}")

@bot.command(name="dailybrief")
async def dailybrief(ctx):
    """Get a comprehensive daily update with news, weather, and crypto"""
    user_id = ctx.author.id
    preferences = db.get_user_preferences(user_id)
    
    # Check rate limit
    last_call = ctx.bot.last_dailybrief_call.get(user_id)
    if last_call and (datetime.now() - last_call).total_seconds() < RATE_LIMITS['dailybrief']:
        await ctx.send("Please wait a few minutes before requesting another daily brief.")
        return
    ctx.bot.last_dailybrief_call[user_id] = datetime.now()

    try:
        # Get news
        sources = preferences.get('preferred_sources')
        embeds, _ = await news_api.get_top_headlines() if not sources else await news_api.get_article_by_source(sources)
        await ctx.send("📰 **Top News:**", embeds=embeds)
        
        # Get weather
        city = preferences.get('preferred_location', DEFAULT_CITY)
        weather_data = await weather_api.get_current_weather(city)
        weather_embed = Embed(
            title=f"Weather in {city}",
            color=discord.Color.blue()
        )
        weather_embed.add_field(name="Temperature", value=f"{weather_data['temperature']}°F", inline=True)
        weather_embed.add_field(name="Description", value=weather_data['description'], inline=True)
        await ctx.send("🌤 **Weather Update:**", embed=weather_embed)
        
        # Get crypto
        crypto = preferences.get('preferred_crypto', DEFAULT_CRYPTO)
        crypto_data = await crypto_api.get_price(crypto)
        crypto_embed = Embed(
            title=f"{crypto.upper()} Price",
            color=discord.Color.gold()
        )
        crypto_embed.add_field(name="Price", value=f"${crypto_data['usd']:,.2f}", inline=True)
        crypto_embed.add_field(name="24h Change", value=f"{crypto_data['usd_24h_change']:.2f}%", inline=True)
        await ctx.send("💰 **Crypto Update:**", embed=crypto_embed)
        
        # Log command usage
        analytics.log_command("dailybrief", user_id)
        
    except Exception as e:
        logger.error(f"Daily brief error for user {user_id}: {str(e)}")
        analytics.log_error("dailybrief", str(e), user_id)
        await ctx.send(f"Error generating daily brief: {str(e)}")

@bot.command(name="stats")
@commands.is_owner()
async def stats(ctx):
    """Get bot analytics and statistics"""
    try:
        report = await analytics.generate_report()
        
        embed = Embed(
            title="📊 Bot Statistics",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="Total Commands Used", value=str(report['total_commands']), inline=True)
        embed.add_field(name="Total Errors", value=str(report['total_errors']), inline=True)
        embed.add_field(name="Active Users", value=str(report['user_count']), inline=True)
        
        top_commands = "\n".join([f"{cmd}: {count}" for cmd, count in report['top_commands'].items()])
        embed.add_field(name="Top Commands", value=top_commands, inline=False)
        
        error_rates = "\n".join([f"{cmd}: {rate}" for cmd, rate in report['error_rates'].items()])
        embed.add_field(name="Error Rates", value=error_rates, inline=False)
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        logger.error(f"Stats error: {str(e)}")
        await ctx.send("Error generating statistics report.")

@bot.command(name="setprefs")
async def set_preferences(ctx):
    """Configure your daily brief preferences"""
    user_id = ctx.author.id
    
    class PreferencesView(View):
        def __init__(self):
            super().__init__(timeout=300)
            self.user_id = user_id
            self.preferences = db.get_user_preferences(user_id)

        @discord.ui.select(
            placeholder="Select your preferred news sources",
            options=[
                SelectOption(label="BBC", value="bbc-news"),
                SelectOption(label="CNN", value="cnn"),
                SelectOption(label="The New York Times", value="the-new-york-times"),
                SelectOption(label="Reuters", value="reuters"),
                SelectOption(label="All Sources", value="all")
            ]
        )
        async def select_sources(self, interaction: discord.Interaction, select: Select):
            # Store the first selected value directly, not as JSON
            self.preferences['preferred_sources'] = select.values[0]
            db.set_user_preferences(self.user_id, self.preferences)
            await interaction.response.send_message("News sources updated!", ephemeral=True)

        @discord.ui.select(
            placeholder="Select your preferred crypto",
            options=[
                SelectOption(label="Bitcoin", value="btc"),
                SelectOption(label="Ethereum", value="eth"),
                SelectOption(label="Solana", value="sol"),
                SelectOption(label="Dogecoin", value="doge")
            ]
        )
        async def select_crypto(self, interaction: discord.Interaction, select: Select):
            self.preferences['preferred_crypto'] = select.values[0]
            db.set_user_preferences(self.user_id, self.preferences)
            await interaction.response.send_message("Crypto preference updated!", ephemeral=True)

        @discord.ui.select(
            placeholder="Select your preferred location",
            options=[
                SelectOption(label="Los Angeles", value="los angeles"),
                SelectOption(label="New York", value="new york"),
                SelectOption(label="London", value="london"),
                SelectOption(label="Tokyo", value="tokyo"),
                SelectOption(label="Custom", value="custom")
            ]
        )
        async def select_location(self, interaction: discord.Interaction, select: Select):
            if select.values[0] == "custom":
                await interaction.response.send_message("Please enter your custom location:")
                try:
                    msg = await bot.wait_for('message', 
                                          check=lambda m: m.author == ctx.author,
                                          timeout=30)
                    self.preferences['preferred_location'] = msg.content
                    db.set_user_preferences(self.user_id, self.preferences)
                    await msg.reply("Location preference updated!")
                except asyncio.TimeoutError:
                    await interaction.followup.send("Timeout! Please try again.")
            else:
                self.preferences['preferred_location'] = select.values[0]
                db.set_user_preferences(self.user_id, self.preferences)
                await interaction.response.send_message("Location preference updated!", ephemeral=True)

    view = PreferencesView()
    embed = Embed(
        title="⚙️ Configure Your Preferences",
        description="Select your preferences for daily brief updates",
        color=discord.Color.blurple()
    )
    await ctx.send(embed=embed, view=view)

@bot.command(name="togglebrief")
async def toggle_daily_brief(ctx):
    """Toggle daily brief notifications"""
    user_id = ctx.author.id
    current_status = db.get_user_preferences(user_id).get('brief_enabled', True)
    new_status = not current_status
    db.toggle_daily_brief(user_id, new_status)
    
    status_text = "enabled" if new_status else "disabled"
    await ctx.send(f"Daily brief notifications have been {status_text}.")

class NewsPagination(discord.ui.View):
    def __init__(self, embeds: List[discord.Embed], timeout: int = 180):
        super().__init__(timeout=timeout)
        self.embeds = embeds
        self.current_page = 0
        self.total_pages = len(embeds)
        
        # Update button states
        self.update_buttons()
    
    def update_buttons(self):
        """Update button states based on current page"""
        self.previous_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page == self.total_pages - 1
    
    @discord.ui.button(label="Previous", style=ButtonStyle.primary)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.defer()
            if self.current_page > 0:
                self.current_page -= 1
                self.update_buttons()
                await interaction.message.edit(embed=self.embeds[self.current_page], view=self)
        except Exception as e:
            logger.error(f"Error in previous button: {e}")
            await interaction.followup.send("Failed to load previous article. Please try again.", ephemeral=True)
    
    @discord.ui.button(label="Next", style=ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.defer()
            if self.current_page < self.total_pages - 1:
                self.current_page += 1
                self.update_buttons()
                await interaction.message.edit(embed=self.embeds[self.current_page], view=self)
        except Exception as e:
            logger.error(f"Error in next button: {e}")
            await interaction.followup.send("Failed to load next article. Please try again.", ephemeral=True)

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        logger.error("DISCORD_TOKEN is not set.")
        exit(1)
    try:
        bot.run(DISCORD_TOKEN)
    except Exception as e:
        logger.error(f"Bot error: {e}")
        print(f"Bot error: {e}")
