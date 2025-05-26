import discord
from discord.ext import commands
from ..utils.crypto_api import CryptoAPI

class CryptoCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.crypto_api = CryptoAPI()

    @commands.command(name="crypto")
    async def crypto(self, ctx, symbol: str):
        """Get current price for a cryptocurrency"""
        price_data = await self.crypto_api.get_price(symbol.upper())
        
        embed = discord.Embed(
            title=f"{symbol.upper()} Price",
            color=discord.Color.gold()
        )
        
        embed.add_field(name="Price", value=f"${price_data['price']:,.2f}", inline=True)
        embed.add_field(name="24h Change", value=f"{price_data['change_24h']:+.2f}%", inline=True)
        
        await ctx.send(embed=embed) 