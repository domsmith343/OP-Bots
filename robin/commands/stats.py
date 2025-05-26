import discord
from discord.ext import commands
from utils.usage_tracker import UsageTracker
from utils.embeds import EmbedBuilder
from utils.cooldown import cooldown
from datetime import timedelta
import os

class StatsCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tracker = UsageTracker(bot.db)
    
    @commands.command(name='stats')
    @cooldown(5)  # 5 second cooldown
    async def stats(self, ctx, command_name: str = None, time_period: str = None):
        """View command usage statistics
        
        Parameters:
        command_name: Optional. Specific command to view stats for
        time_period: Optional. Time period to view stats for (e.g., '1d', '7d', '30d')
        """
        try:
            # Parse time period
            period = None
            if time_period:
                if time_period.endswith('d'):
                    days = int(time_period[:-1])
                    period = timedelta(days=days)
                elif time_period.endswith('h'):
                    hours = int(time_period[:-1])
                    period = timedelta(hours=hours)
            
            if command_name:
                # Get stats for specific command
                stats = self.tracker.get_command_stats(command_name, period)
                if not stats:
                    await ctx.send(embed=EmbedBuilder.create_error_embed(
                        "Error",
                        f"No statistics found for command '{command_name}'"
                    ))
                    return
                
                embed = EmbedBuilder.create_success_embed(
                    f"📊 Statistics for {command_name}",
                    f"Total Uses: {stats['total_uses']}\n"
                    f"Successful: {stats['successful_uses']}\n"
                    f"Failed: {stats['failed_uses']}\n"
                    f"Last Used: {stats['last_used']}"
                )
            else:
                # Get stats for all commands
                stats = self.tracker.get_command_stats(time_period=period)
                if not stats:
                    await ctx.send(embed=EmbedBuilder.create_error_embed(
                        "Error",
                        "No command statistics found"
                    ))
                    return
                
                # Create paginated embed for all commands
                description = "Command Usage Statistics:\n\n"
                for stat in stats:
                    description += (
                        f"**{stat['command_name']}**\n"
                        f"Total: {stat['total_uses']} | "
                        f"Success: {stat['successful_uses']} | "
                        f"Failed: {stat['failed_uses']}\n"
                        f"Last Used: {stat['last_used']}\n\n"
                    )
                
                embed = EmbedBuilder.create_success_embed(
                    "📊 Command Statistics",
                    description
                )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(embed=EmbedBuilder.create_error_embed(
                "Error",
                f"Failed to retrieve statistics: {str(e)}"
            ))
    
    @commands.command(name='userstats')
    @cooldown(5)
    async def user_stats(self, ctx, user: discord.Member = None, time_period: str = None):
        """View command usage statistics for a user
        
        Parameters:
        user: Optional. User to view stats for (defaults to command user)
        time_period: Optional. Time period to view stats for (e.g., '1d', '7d', '30d')
        """
        try:
            target_user = user or ctx.author
            
            # Parse time period
            period = None
            if time_period:
                if time_period.endswith('d'):
                    days = int(time_period[:-1])
                    period = timedelta(days=days)
                elif time_period.endswith('h'):
                    hours = int(time_period[:-1])
                    period = timedelta(hours=hours)
            
            stats = self.tracker.get_user_stats(target_user.id, period)
            if not stats:
                await ctx.send(embed=EmbedBuilder.create_error_embed(
                    "Error",
                    f"No statistics found for user {target_user.name}"
                ))
                return
            
            description = f"Command Usage Statistics for {target_user.name}:\n\n"
            for stat in stats:
                description += (
                    f"**{stat['command_name']}**\n"
                    f"Total: {stat['total_uses']} | "
                    f"Success: {stat['successful_uses']} | "
                    f"Failed: {stat['failed_uses']}\n"
                    f"Last Used: {stat['last_used']}\n\n"
                )
            
            embed = EmbedBuilder.create_success_embed(
                "📊 User Statistics",
                description
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(embed=EmbedBuilder.create_error_embed(
                "Error",
                f"Failed to retrieve user statistics: {str(e)}"
            ))
    
    @commands.command(name='errorstats')
    @cooldown(5)
    async def error_stats(self, ctx, time_period: str = None):
        """View command error statistics
        
        Parameters:
        time_period: Optional. Time period to view stats for (e.g., '1d', '7d', '30d')
        """
        try:
            # Parse time period
            period = None
            if time_period:
                if time_period.endswith('d'):
                    days = int(time_period[:-1])
                    period = timedelta(days=days)
                elif time_period.endswith('h'):
                    hours = int(time_period[:-1])
                    period = timedelta(hours=hours)
            
            stats = self.tracker.get_error_stats(period)
            if not stats:
                await ctx.send(embed=EmbedBuilder.create_success_embed(
                    "Error Statistics",
                    "No errors recorded in the specified time period."
                ))
                return
            
            description = "Command Error Statistics:\n\n"
            for stat in stats:
                description += (
                    f"**{stat['command_name']}**\n"
                    f"Error: {stat['error_message']}\n"
                    f"Count: {stat['error_count']}\n\n"
                )
            
            embed = EmbedBuilder.create_success_embed(
                "📊 Error Statistics",
                description
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(embed=EmbedBuilder.create_error_embed(
                "Error",
                f"Failed to retrieve error statistics: {str(e)}"
            ))

async def setup(bot):
    await bot.add_cog(StatsCommand(bot)) 