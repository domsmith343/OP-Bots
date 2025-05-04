#!/usr/bin/env python3
"""
Ollama Discord Bot - Dockerized Version
"""

import os
import discord
from discord.ext import commands, tasks
import requests
import asyncio
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ollama_discord_bot')

# Bot configuration
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OLLAMA_API = os.getenv('OLLAMA_API', 'http://localhost:11434')
DEFAULT_MODEL = os.getenv('OLLAMA_DEFAULT_MODEL', 'llama3')
COMMAND_PREFIX = os.getenv('COMMAND_PREFIX', '.')

if not DISCORD_TOKEN:
    logger.error("DISCORD_TOKEN is not set.")
    exit(1)

# Intent and Bot initialization
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents, help_command=None)

# In-memory schedule storage
SCHEDULE = []

def call_ollama_api(prompt: str, model: str = DEFAULT_MODEL) -> str:
    return asyncio.get_event_loop().run_until_complete(_async_call(prompt, model))

async def _async_call(prompt: str, model: str = DEFAULT_MODEL) -> str:
    api_url = f"{OLLAMA_API}/api/generate"
    payload = {"model": model, "prompt": prompt, "stream": False}
    try:
        response = await asyncio.to_thread(requests.post, api_url, json=payload, timeout=120)
        if response.status_code == 200:
            return response.json().get('response', 'No response from model')
        return f"Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"Connection error: {e}"

@bot.event
async def on_ready():
    logger.info(f"{bot.user.name} connected!")
    await bot.change_presence(activity=discord.Game(name=f"{COMMAND_PREFIX}help for commands"))
    update_status.start()

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return  # Quietly ignore unknown commands
    else:
        logger.error(f"Error: {error}")
        await ctx.send(f"Error: {error}")

@tasks.loop(seconds=60)
async def update_status():
    await bot.change_presence(
        activity=discord.Game(name=f"{COMMAND_PREFIX}help | {len(SCHEDULE)} scheduled")
    )

# --- Core Commands ---
@bot.command(name="ask")
async def ask(ctx, *, question: str = None):
    if not question:
        return await ctx.send("Usage: `.ask <question>`")
    async with ctx.typing():
        response = await _async_call(question)
    if len(response) > 2000:
        for i in range(0, len(response), 2000):
            msg = await ctx.send(response[i:i+2000])
            await msg.add_reaction("🤖")
    else:
        msg = await ctx.send(response)
        await msg.add_reaction("🤖")

@bot.command(name="models")
async def list_models(ctx):
    async with ctx.typing():
        try:
            resp = await asyncio.to_thread(requests.get, f"{OLLAMA_API}/api/tags", timeout=30)
            if resp.status_code == 200:
                models = [m['name'] for m in resp.json().get('models', [])]
                text = "Available models:\n" + "\n".join(models) if models else "No models found."
            else:
                text = f"Error {resp.status_code}: {resp.text}"
        except Exception as e:
            text = f"Error fetching models: {e}"
    await ctx.send(text)

@bot.command(name="help")
async def help_command(ctx, command: str = None):
    embed = discord.Embed(title="Robin Bot Commands", color=discord.Color.blue())
    embed.add_field(name=".ask", value="Ask the LLM a question.", inline=False)
    embed.add_field(name=".models", value="List available Ollama models.", inline=False)
    embed.add_field(name=".summarize", value="Summarize provided text.", inline=False)
    embed.add_field(name=".define", value="Define a term.", inline=False)
    embed.add_field(name=".anime", value="Lookup anime info.", inline=False)
    embed.add_field(name=".schedule", value="View or add schedule entries.", inline=False)
    await ctx.send(embed=embed)

# --- New Commands ---
@bot.command(name="summarize")
async def summarize(ctx, *, text: str = None):
    if not text:
        return await ctx.send("Usage: `.summarize <text>`")
    prompt = f"Summarize this:\n\n{text}"
    response = await _async_call(prompt)
    msg = await ctx.send(response)
    await msg.add_reaction("📝")

@bot.command(name="define")
async def define(ctx, *, term: str = None):
    if not term:
        return await ctx.send("Usage: `.define <term>`")
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{term}"
    try:
        res = await asyncio.to_thread(requests.get, url, timeout=10)
        if res.status_code == 200:
            definition = res.json()[0]["meanings"][0]["definitions"][0]["definition"]
            msg = await ctx.send(f"**{term}**: {definition}")
            await msg.add_reaction("📖")
        else:
            await ctx.send(f"No definition found for **{term}**.")
    except Exception as e:
        await ctx.send(f"Error: {e}")

@bot.command(name="anime")
async def anime(ctx, *, query: str = None):
    if not query:
        return await ctx.send("Usage: `.anime <title>`")
    url = f"https://api.jikan.moe/v4/anime?q={query}"
    try:
        resp = await asyncio.to_thread(requests.get, url, timeout=10)
        data = resp.json().get("data", [])
        if data:
            a = data[0]
            synopsis = (a.get("synopsis") or "No synopsis")[:400] + "..."
            msg = await ctx.send(f"**{a['title']}**\n{synopsis}\n<{a['url']}>")
            await msg.add_reaction("🍥")
        else:
            await ctx.send("No anime found.")
    except Exception as e:
        await ctx.send(f"Error: {e}")

@bot.command(name="schedule")
async def schedule(ctx, *, entry: str = None):
    global SCHEDULE
    if not entry:
        if not SCHEDULE:
            return await ctx.send("No events scheduled.")
        return await ctx.send("📅 **Your schedule:**\n" + "\n".join(f"- {e}" for e in SCHEDULE))
    SCHEDULE.append(entry)
    await ctx.send(f"Added to schedule: {entry}")

@bot.command(name="news")
async def news(ctx):
    return await ctx.send("Robin does not handle news. Please use Nami with `!news`.")

if __name__ == "__main__":
    try:
        bot.run(DISCORD_TOKEN)
    except Exception as e:
        logger.error(f"Bot error: {e}")
        print(f"Bot error: {e}")
