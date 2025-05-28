import discord
from discord.ext import commands
from discord import app_commands, Interaction
import os
from api.sports import get_upcoming_games, get_live_scores

class SportsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="scores", description="Show recent scores for a league (NBA, EPL, NFL, etc.)")
    @app_commands.describe(league="League to show scores for (e.g., nba, epl, nfl)")
    async def scores(self, interaction: Interaction, league: str = None):
        league = league or "nba"
        try:
            games = await get_live_scores(league)
            if not games:
                await interaction.response.send_message(f"No live games found for {league.upper()}.")
                return
            embed = discord.Embed(title=f"Live {league.upper()} Scores", color=discord.Color.green())
            for game in games:
                embed.add_field(name=game['matchup'], value=game['score'], inline=False)
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"Error fetching scores: {str(e)}")

    @app_commands.command(name="games", description="Show upcoming games for a league (NBA, EPL, NFL, etc.)")
    @app_commands.describe(league="League to show games for (e.g., nba, epl, nfl)", days="Number of days to look ahead (default 3)")
    async def games(self, interaction: Interaction, league: str = None, days: int = 3):
        league = league or "nba"
        try:
            games = await get_upcoming_games(league, days)
            if not games:
                await interaction.response.send_message(f"No upcoming games found for {league.upper()}.")
                return
            embed = discord.Embed(title=f"Upcoming {league.upper()} Games", color=discord.Color.blue())
            for game in games:
                embed.add_field(name=game['matchup'], value=game['time'], inline=False)
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"Error fetching games: {str(e)}")

async def setup(bot):
    await bot.add_cog(SportsCog(bot))
