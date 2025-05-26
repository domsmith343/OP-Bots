import discord
from discord.ext import commands
from discord import app_commands
from utils.sports_tracker import SportsTracker
from utils.embeds import EmbedBuilder
from utils.scheduler import Scheduler
from typing import Optional
import os

class SportsCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sports_tracker = SportsTracker()
        self.scheduler = Scheduler(bot)
        
        # Set API key from environment
        api_key = os.getenv('ODDS_API_KEY')
        if api_key:
            self.sports_tracker.set_api_key(api_key)
        
        # Start live score updates
        self.update_live_scores.start()
    
    def cog_unload(self):
        """Clean up when cog is unloaded"""
        self.update_live_scores.cancel()
    
    @tasks.loop(minutes=5)
    async def update_live_scores(self):
        """Update live scores every 5 minutes"""
        if not self.sports_tracker.api_key:
            return
        
        try:
            # Get all subscribed channels
            for channel_id, sub in self.sports_tracker.get_subscriptions().items():
                channel = self.bot.get_channel(channel_id)
                if channel:
                    await self.sports_tracker.check_live_scores(channel)
        except Exception as e:
            print(f"Error updating live scores: {str(e)}")
    
    @app_commands.command(name='games', description='Show upcoming games')
    @app_commands.describe(
        league='League to show games for (NBA, NFL, MLB, NHL)',
        days='Number of days to look ahead (default: 1)'
    )
    async def games(self, interaction: discord.Interaction, 
                   league: str = 'nba',
                   days: Optional[int] = 1):
        """Show upcoming games for a league"""
        try:
            if not self.sports_tracker.api_key:
                await interaction.response.send_message(embed=EmbedBuilder.create_error_embed(
                    "Error",
                    "Sports API key not configured"
                ))
                return
            
            # Get upcoming games
            games = await self.sports_tracker.get_upcoming_games(league.lower(), days)
            
            if not games:
                await interaction.response.send_message(embed=EmbedBuilder.create_error_embed(
                    "No Games",
                    f"No upcoming games found for {league.upper()}"
                ))
                return
            
            # Create embed
            embed = EmbedBuilder.create_success_embed(
                f"Upcoming {league.upper()} Games",
                f"Showing games for the next {days} day(s):"
            )
            
            # Add games to embed
            for game in games:
                game_text = self.sports_tracker.format_game_alert(game)
                odds_text = self.sports_tracker.format_odds(game)
                embed.add_field(
                    name=game_text,
                    value=odds_text,
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(embed=EmbedBuilder.create_error_embed(
                "Error",
                f"Failed to get games: {str(e)}"
            ))
    
    @app_commands.command(name='scores', description='Show live scores')
    @app_commands.describe(league='League to show scores for (NBA, NFL, MLB, NHL)')
    async def scores(self, interaction: discord.Interaction, league: str = 'nba'):
        """Show live scores for a league"""
        try:
            if not self.sports_tracker.api_key:
                await interaction.response.send_message(embed=EmbedBuilder.create_error_embed(
                    "Error",
                    "Sports API key not configured"
                ))
                return
            
            # Get live scores
            games = await self.sports_tracker.get_live_scores(league.lower())
            
            if not games:
                await interaction.response.send_message(embed=EmbedBuilder.create_error_embed(
                    "No Games",
                    f"No live games found for {league.upper()}"
                ))
                return
            
            # Create embed
            embed = EmbedBuilder.create_success_embed(
                f"Live {league.upper()} Scores",
                "Current game scores:"
            )
            
            # Add games to embed
            for game in games:
                game_text = self.sports_tracker.format_game_alert(game)
                embed.add_field(
                    name=game_text,
                    value="",
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(embed=EmbedBuilder.create_error_embed(
                "Error",
                f"Failed to get scores: {str(e)}"
            ))
    
    @app_commands.command(name='subscribe', description='Subscribe to game alerts')
    @app_commands.describe(
        league='League to subscribe to (NBA, NFL, MLB, NHL)',
        team='Team to follow (optional)'
    )
    async def subscribe(self, interaction: discord.Interaction, 
                       league: str,
                       team: Optional[str] = None):
        """Subscribe to game alerts for a league or team"""
        try:
            if not self.sports_tracker.api_key:
                await interaction.response.send_message(embed=EmbedBuilder.create_error_embed(
                    "Error",
                    "Sports API key not configured"
                ))
                return
            
            # Add subscription
            self.sports_tracker.add_subscription(interaction.channel_id, league.lower(), team)
            
            # Send confirmation
            if team:
                message = f"Subscribed to {team} games in {league.upper()}"
            else:
                message = f"Subscribed to all {league.upper()} games"
            
            await interaction.response.send_message(embed=EmbedBuilder.create_success_embed(
                "Subscription Added",
                message
            ))
            
            # Check for immediate updates
            await self.sports_tracker.check_upcoming_games(interaction.channel)
            
        except Exception as e:
            await interaction.response.send_message(embed=EmbedBuilder.create_error_embed(
                "Error",
                f"Failed to subscribe: {str(e)}"
            ))
    
    @app_commands.command(name='unsubscribe', description='Unsubscribe from game alerts')
    @app_commands.describe(
        team='Team to unsubscribe from (leave empty to unsubscribe from all)'
    )
    async def unsubscribe(self, interaction: discord.Interaction, team: Optional[str] = None):
        """Unsubscribe from game alerts"""
        try:
            # Remove subscription
            self.sports_tracker.remove_subscription(interaction.channel_id, team)
            
            # Send confirmation
            if team:
                message = f"Unsubscribed from {team} games"
            else:
                message = "Unsubscribed from all game alerts"
            
            await interaction.response.send_message(embed=EmbedBuilder.create_success_embed(
                "Subscription Removed",
                message
            ))
            
        except Exception as e:
            await interaction.response.send_message(embed=EmbedBuilder.create_error_embed(
                "Error",
                f"Failed to unsubscribe: {str(e)}"
            ))
    
    @app_commands.command(name='subscriptions', description='List current game subscriptions')
    async def subscriptions(self, interaction: discord.Interaction):
        """List current game subscriptions"""
        try:
            # Get subscriptions for this channel
            sub = self.sports_tracker.get_subscriptions(interaction.channel_id)
            
            if not sub:
                await interaction.response.send_message(embed=EmbedBuilder.create_error_embed(
                    "No Subscriptions",
                    "This channel has no active game subscriptions"
                ))
                return
            
            # Create embed
            embed = EmbedBuilder.create_success_embed(
                "Game Subscriptions",
                f"League: {sub['league'].upper()}"
            )
            
            if sub['teams']:
                teams_text = "\n".join(f"• {team}" for team in sub['teams'])
                embed.add_field(name="Teams", value=teams_text, inline=False)
            else:
                embed.add_field(name="Teams", value="All teams", inline=False)
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(embed=EmbedBuilder.create_error_embed(
                "Error",
                f"Failed to list subscriptions: {str(e)}"
            ))

async def setup(bot):
    await bot.add_cog(SportsCommand(bot)) 