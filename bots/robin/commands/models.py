import discord
from discord.ext import commands
from ..utils.ollama_api import OllamaAPI

class ModelsCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ollama_api = OllamaAPI()

    @commands.command(name="models")
    async def models(self, ctx):
        """List available Ollama models"""
        models = await self.ollama_api.list_models()
        
        embed = discord.Embed(
            title="Available Models",
            color=discord.Color.blue()
        )
        
        for model in models:
            embed.add_field(
                name=model,
                value="Ready to use",
                inline=True
            )
        
        await ctx.send(embed=embed) 