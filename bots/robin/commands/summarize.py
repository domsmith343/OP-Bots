import discord
from discord.ext import commands
from ..utils.ollama_api import OllamaAPI

class SummarizeCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ollama_api = OllamaAPI()

    @commands.command(name="summarize")
    async def summarize(self, ctx, *, text: str):
        """Summarize the given text"""
        prompt = f"Please provide a concise summary of the following text:\n\n{text}"
        summary = await self.ollama_api.generate(prompt, model="mistral")
        
        embed = discord.Embed(
            title="Text Summary",
            description=summary,
            color=discord.Color.blue()
        )
        
        await ctx.send(embed=embed) 