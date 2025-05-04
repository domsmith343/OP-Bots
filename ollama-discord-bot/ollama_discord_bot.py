#!/usr/bin/env python3
"""
Ollama Discord Bot - Dockerized Version
"""

import os
import discord
from discord.ext import commands
import requests
import asyncio
import logging
import json
from dotenv import load_dotenv

load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ollama_discord_bot')

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OLLAMA_API = os.getenv('OLLAMA_API', 'http://localhost:11434')
DEFAULT_MODEL = os.getenv('OLLAMA_DEFAULT_MODEL', 'llama3')
COMMAND_PREFIX = '!'

if not DISCORD_TOKEN:
    logger.error("DISCORD_TOKEN is not set.")
    exit(1)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents, help_command=None)

@bot.event
async def on_ready():
    logger.info(f'{bot.user.name} connected!')
    await bot.change_presence(activity=discord.Game(name=f"{COMMAND_PREFIX}help for commands"))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"Unknown command. Try `{COMMAND_PREFIX}help`.")
    else:
        logger.error(f"Error: {error}")
        await ctx.send(f"Error: {error}")

async def call_ollama_api(prompt, model=DEFAULT_MODEL):
    api_url = f"{OLLAMA_API}/api/generate"
    payload = {"model": model, "prompt": prompt, "stream": False}
    try:
        response = await asyncio.to_thread(requests.post, api_url, json=payload, timeout=120)
        if response.status_code == 200:
            return response.json().get('response', 'No response from model')
        else:
            return f"Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"Connection error: {str(e)}"

@bot.command(name="ask")
async def ask(ctx, *, question=None):
    if not question:
        await ctx.send("Usage: `!ask <question>`")
        return
    async with ctx.typing():
        response = await call_ollama_api(question)
        if len(response) > 2000:
            for i in range(0, len(response), 2000):
                await ctx.send(response[i:i+2000])
        else:
            await ctx.send(response)

@bot.command(name="models")
async def list_models(ctx):
    async with ctx.typing():
        try:
            response = await asyncio.to_thread(requests.get, f"{OLLAMA_API}/api/tags", timeout=30)
            if response.status_code == 200:
                models = [m['name'] for m in response.json().get('models', [])]
                if models:
                    await ctx.send("Available models:\n" + "\n".join(models))
                else:
                    await ctx.send("No models found.")
            else:
                await ctx.send(f"Error {response.status_code}: {response.text}")
        except Exception as e:
            await ctx.send(f"Error fetching models: {str(e)}")

@bot.command(name="help")
async def help_command(ctx, command=None):
    embed = discord.Embed(title="Bot Commands", color=discord.Color.blue())
    embed.add_field(name="!ask", value="Ask a question to the LLM.", inline=False)
    embed.add_field(name="!models", value="List available Ollama models.", inline=False)
    await ctx.send(embed=embed)

if __name__ == "__main__":
    try:
        bot.run(DISCORD_TOKEN)
    except Exception as e:
        logger.error(f"Bot error: {str(e)}")
        print(f"Bot error: {str(e)}")
