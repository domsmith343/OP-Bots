import discord
from discord.ext import commands
from discord import app_commands, Interaction
import os
from api.crypto import CryptoAPI

class CryptoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.crypto_api = CryptoAPI()

    @app_commands.command(name="crypto", description="Get current cryptocurrency price")
    @app_commands.describe(symbol="Cryptocurrency symbol (e.g., btc, eth, sol)")
    async def crypto(self, interaction: Interaction, symbol: str = None):
        symbol = symbol or os.getenv("DEFAULT_CRYPTO", "btc")
        try:
            price_data = await self.crypto_api.get_price(symbol)
            if not price_data or not isinstance(price_data, dict):
                await interaction.response.send_message(f"Unable to fetch price data for {symbol.upper()}.")
                return
            price = price_data.get('price')
            change = price_data.get('change_24h')
            embed = discord.Embed(title=f"{symbol.upper()} Price", color=discord.Color.gold())
            if price is not None:
                embed.add_field(name="Price", value=f"${price:,.2f}", inline=True)
            if change is not None:
                embed.add_field(name="24h Change", value=f"{change:.2f}%", inline=True)
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"Error fetching crypto price: {str(e)}")

async def setup(bot):
    await bot.add_cog(CryptoCog(bot))
