import discord
from discord.ext import commands
from ..utils.news_api import NewsAPI

class NewsCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.news_api = NewsAPI()

    @commands.command(name="news")
    async def news(self, ctx):
        """Get the latest news headlines"""
        headlines = await self.news_api.get_headlines()
        
        embed = discord.Embed(
            title="Latest News",
            color=discord.Color.blue()
        )
        
        for article in headlines[:5]:  # Show top 5 headlines
            embed.add_field(
                name=article["title"],
                value=f"[Read more]({article['url']})",
                inline=False
            )
        
        await ctx.send(embed=embed) 