import discord
from discord.ext import commands
from discord import app_commands
from utils.usage_tracker import UsageTracker
from utils.embeds import EmbedBuilder
from utils.cooldown import cooldown
from typing import Optional
import matplotlib.pyplot as plt
import io
import time

class StatsCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.usage_tracker = UsageTracker()
    
    @app_commands.command(name='stats', description='Show command usage statistics')
    @app_commands.describe(time_period='Time period to show stats for (1h, 1d, 1w, 1m)')
    async def stats(self, interaction: discord.Interaction, time_period: Optional[str] = None):
        """Show command usage statistics"""
        try:
            # Convert time period to seconds
            seconds = None
            if time_period:
                unit = time_period[-1].lower()
                value = int(time_period[:-1])
                if unit == 'h':
                    seconds = value * 3600
                elif unit == 'd':
                    seconds = value * 86400
                elif unit == 'w':
                    seconds = value * 604800
                elif unit == 'm':
                    seconds = value * 2592000
                else:
                    await interaction.response.send_message(embed=EmbedBuilder.create_error_embed(
                        "Error",
                        "Invalid time period. Use format: 1h, 1d, 1w, 1m"
                    ))
                    return
            
            # Get command stats
            stats = self.usage_tracker.get_command_stats(seconds)
            
            if not stats:
                await interaction.response.send_message(embed=EmbedBuilder.create_error_embed(
                    "Error",
                    "No command usage data available for the specified time period."
                ))
                return
            
            # Create embed
            description = "**Command Usage Statistics**\n\n"
            for cmd, data in stats.items():
                description += f"**{cmd}**\n"
                description += f"Total Uses: {data['total_uses']}\n"
                description += f"Success Rate: {data['success_rate']:.1f}%\n"
                description += f"Avg. Execution Time: {data['avg_execution_time']:.2f}s\n\n"
            
            time_str = ""
            if seconds:
                if seconds < 3600:
                    time_str = f"Last {seconds//60} minutes"
                elif seconds < 86400:
                    time_str = f"Last {seconds//3600} hours"
                elif seconds < 604800:
                    time_str = f"Last {seconds//86400} days"
                else:
                    time_str = f"Last {seconds//604800} weeks"
            
            embed = EmbedBuilder.create_success_embed(
                "Command Statistics",
                description,
                footer=time_str if time_str else "All time"
            )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(embed=EmbedBuilder.create_error_embed(
                "Error",
                f"Failed to show statistics: {str(e)}"
            ))
    
    @app_commands.command(name='userstats', description='Show command usage statistics for a user')
    @app_commands.describe(
        member='The user to show stats for',
        time_period='Time period to show stats for (1h, 1d, 1w, 1m)'
    )
    async def userstats(self, interaction: discord.Interaction, member: Optional[discord.Member] = None, time_period: Optional[str] = None):
        """Show command usage statistics for a user"""
        try:
            # Use command user if no member specified
            if not member:
                member = interaction.user
            
            # Convert time period to seconds
            seconds = None
            if time_period:
                unit = time_period[-1].lower()
                value = int(time_period[:-1])
                if unit == 'h':
                    seconds = value * 3600
                elif unit == 'd':
                    seconds = value * 86400
                elif unit == 'w':
                    seconds = value * 604800
                elif unit == 'm':
                    seconds = value * 2592000
                else:
                    await interaction.response.send_message(embed=EmbedBuilder.create_error_embed(
                        "Error",
                        "Invalid time period. Use format: 1h, 1d, 1w, 1m"
                    ))
                    return
            
            # Get user stats
            stats = self.usage_tracker.get_user_stats(member.id, seconds)
            
            if not stats:
                await interaction.response.send_message(embed=EmbedBuilder.create_error_embed(
                    "Error",
                    f"No command usage data available for {member.display_name}."
                ))
                return
            
            # Create embed
            description = f"**Command Usage Statistics for {member.display_name}**\n\n"
            for cmd, data in stats.items():
                description += f"**{cmd}**\n"
                description += f"Total Uses: {data['total_uses']}\n"
                description += f"Success Rate: {data['success_rate']:.1f}%\n"
                description += f"Avg. Execution Time: {data['avg_execution_time']:.2f}s\n\n"
            
            time_str = ""
            if seconds:
                if seconds < 3600:
                    time_str = f"Last {seconds//60} minutes"
                elif seconds < 86400:
                    time_str = f"Last {seconds//3600} hours"
                elif seconds < 604800:
                    time_str = f"Last {seconds//86400} days"
                else:
                    time_str = f"Last {seconds//604800} weeks"
            
            embed = EmbedBuilder.create_success_embed(
                "User Statistics",
                description,
                footer=time_str if time_str else "All time"
            )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(embed=EmbedBuilder.create_error_embed(
                "Error",
                f"Failed to show user statistics: {str(e)}"
            ))
    
    @app_commands.command(name='errorstats', description='Show command error statistics')
    @app_commands.describe(time_period='Time period to show stats for (1h, 1d, 1w, 1m)')
    async def errorstats(self, interaction: discord.Interaction, time_period: Optional[str] = None):
        """Show command error statistics"""
        try:
            # Convert time period to seconds
            seconds = None
            if time_period:
                unit = time_period[-1].lower()
                value = int(time_period[:-1])
                if unit == 'h':
                    seconds = value * 3600
                elif unit == 'd':
                    seconds = value * 86400
                elif unit == 'w':
                    seconds = value * 604800
                elif unit == 'm':
                    seconds = value * 2592000
                else:
                    await interaction.response.send_message(embed=EmbedBuilder.create_error_embed(
                        "Error",
                        "Invalid time period. Use format: 1h, 1d, 1w, 1m"
                    ))
                    return
            
            # Get error stats
            stats = self.usage_tracker.get_error_stats(seconds)
            
            if not stats:
                await interaction.response.send_message(embed=EmbedBuilder.create_error_embed(
                    "Error",
                    "No error data available for the specified time period."
                ))
                return
            
            # Create embed
            description = "**Command Error Statistics**\n\n"
            for cmd, errors in stats.items():
                description += f"**{cmd}**\n"
                for error, count in errors.items():
                    description += f"- {error}: {count} times\n"
                description += "\n"
            
            time_str = ""
            if seconds:
                if seconds < 3600:
                    time_str = f"Last {seconds//60} minutes"
                elif seconds < 86400:
                    time_str = f"Last {seconds//3600} hours"
                elif seconds < 604800:
                    time_str = f"Last {seconds//86400} days"
                else:
                    time_str = f"Last {seconds//604800} weeks"
            
            embed = EmbedBuilder.create_success_embed(
                "Error Statistics",
                description,
                footer=time_str if time_str else "All time"
            )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(embed=EmbedBuilder.create_error_embed(
                "Error",
                f"Failed to show error statistics: {str(e)}"
            ))
    
    @app_commands.command(name='trends', description='Show command usage trends with graphs')
    @app_commands.describe(
        time_period='Time period to show trends for (1h, 1d, 1w, 1m)',
        command='Specific command to show trends for'
    )
    async def trends(self, interaction: discord.Interaction, time_period: Optional[str] = None, command: Optional[str] = None):
        """Show command usage trends with graphs"""
        try:
            # Convert time period to seconds
            seconds = 86400  # Default to 24 hours
            if time_period:
                unit = time_period[-1].lower()
                value = int(time_period[:-1])
                if unit == 'h':
                    seconds = value * 3600
                elif unit == 'd':
                    seconds = value * 86400
                elif unit == 'w':
                    seconds = value * 604800
                elif unit == 'm':
                    seconds = value * 2592000
                else:
                    await interaction.response.send_message(embed=EmbedBuilder.create_error_embed(
                        "Error",
                        "Invalid time period. Use format: 1h, 1d, 1w, 1m"
                    ))
                    return
            
            # Get usage trends
            trends = self.usage_tracker.get_usage_trends(seconds)
            
            if not trends:
                await interaction.response.send_message(embed=EmbedBuilder.create_error_embed(
                    "Error",
                    "No usage data available for the specified time period."
                ))
                return
            
            # Filter for specific command if provided
            if command and command in trends:
                trends = {command: trends[command]}
            elif command:
                await interaction.response.send_message(embed=EmbedBuilder.create_error_embed(
                    "Error",
                    f"No data available for command '{command}'."
                ))
                return
            
            # Create graph
            plt.figure(figsize=(10, 6))
            for cmd, data in trends.items():
                hours = sorted(data.keys())
                counts = [data[h] for h in hours]
                plt.plot(hours, counts, label=cmd, marker='o')
            
            plt.title('Command Usage Trends')
            plt.xlabel('Hour')
            plt.ylabel('Usage Count')
            plt.legend()
            plt.grid(True)
            
            # Save plot to bytes
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            plt.close()
            
            # Create embed
            time_str = ""
            if seconds < 3600:
                time_str = f"Last {seconds//60} minutes"
            elif seconds < 86400:
                time_str = f"Last {seconds//3600} hours"
            elif seconds < 604800:
                time_str = f"Last {seconds//86400} days"
            else:
                time_str = f"Last {seconds//604800} weeks"
            
            embed = EmbedBuilder.create_success_embed(
                "Usage Trends",
                f"Showing command usage trends over {time_str}",
                footer="Hourly usage data"
            )
            
            # Send graph
            await interaction.response.send_message(embed=embed, file=discord.File(buf, 'trends.png'))
            
        except Exception as e:
            await interaction.response.send_message(embed=EmbedBuilder.create_error_embed(
                "Error",
                f"Failed to show trends: {str(e)}"
            ))
    
    @app_commands.command(name='serverstats', description='Show server-wide command usage statistics')
    @app_commands.describe(
        time_period='Time period to show stats for (1h, 1d, 1w, 1m)',
        category='Category to show stats for (commands, users, channels)'
    )
    async def serverstats(self, interaction: discord.Interaction, time_period: Optional[str] = None, category: Optional[str] = None):
        """Show server-wide command usage statistics"""
        try:
            if not interaction.guild:
                await interaction.response.send_message(embed=EmbedBuilder.create_error_embed(
                    "Error",
                    "This command can only be used in a server."
                ))
                return
            
            # Convert time period to seconds
            seconds = None
            if time_period:
                unit = time_period[-1].lower()
                value = int(time_period[:-1])
                if unit == 'h':
                    seconds = value * 3600
                elif unit == 'd':
                    seconds = value * 86400
                elif unit == 'w':
                    seconds = value * 604800
                elif unit == 'm':
                    seconds = value * 2592000
                else:
                    await interaction.response.send_message(embed=EmbedBuilder.create_error_embed(
                        "Error",
                        "Invalid time period. Use format: 1h, 1d, 1w, 1m"
                    ))
                    return
            
            # Get server stats
            stats = self.usage_tracker.get_guild_stats(interaction.guild.id, seconds)
            
            if not stats:
                await interaction.response.send_message(embed=EmbedBuilder.create_error_embed(
                    "Error",
                    "No command usage data available for this server."
                ))
                return
            
            # Create embed based on category
            if category == "commands":
                description = "**Command Usage Statistics**\n\n"
                for stat in stats:
                    description += f"**{stat['command_name']}**\n"
                    description += f"Total Uses: {stat['total_uses']}\n"
                    description += f"Success Rate: {(stat['successful_uses'] / stat['total_uses'] * 100):.1f}%\n"
                    description += f"Last Used: {stat['last_used']}\n\n"
            
            elif category == "users":
                # Get top users
                user_stats = {}
                for stat in stats:
                    if stat['user_id'] not in user_stats:
                        user_stats[stat['user_id']] = 0
                    user_stats[stat['user_id']] += stat['total_uses']
                
                description = "**Top Command Users**\n\n"
                for user_id, total_uses in sorted(user_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
                    user = interaction.guild.get_member(user_id)
                    if user:
                        description += f"**{user.display_name}**: {total_uses} commands\n"
            
            elif category == "channels":
                # Get channel stats
                channel_stats = {}
                for stat in stats:
                    if stat['channel_id'] not in channel_stats:
                        channel_stats[stat['channel_id']] = 0
                    channel_stats[stat['channel_id']] += stat['total_uses']
                
                description = "**Channel Usage Statistics**\n\n"
                for channel_id, total_uses in sorted(channel_stats.items(), key=lambda x: x[1], reverse=True):
                    channel = interaction.guild.get_channel(channel_id)
                    if channel:
                        description += f"**#{channel.name}**: {total_uses} commands\n"
            
            else:
                # Show overall stats
                total_commands = sum(stat['total_uses'] for stat in stats)
                total_successful = sum(stat['successful_uses'] for stat in stats)
                total_failed = sum(stat['failed_uses'] for stat in stats)
                unique_users = len(set(stat['user_id'] for stat in stats))
                unique_channels = len(set(stat['channel_id'] for stat in stats))
                
                description = "**Server Statistics Overview**\n\n"
                description += f"Total Commands: {total_commands}\n"
                description += f"Successful: {total_successful}\n"
                description += f"Failed: {total_failed}\n"
                description += f"Success Rate: {(total_successful / total_commands * 100):.1f}%\n"
                description += f"Unique Users: {unique_users}\n"
                description += f"Active Channels: {unique_channels}\n\n"
                
                # Add top commands
                description += "**Top Commands**\n"
                for stat in sorted(stats, key=lambda x: x['total_uses'], reverse=True)[:5]:
                    description += f"**{stat['command_name']}**: {stat['total_uses']} uses\n"
            
            time_str = ""
            if seconds:
                if seconds < 3600:
                    time_str = f"Last {seconds//60} minutes"
                elif seconds < 86400:
                    time_str = f"Last {seconds//3600} hours"
                elif seconds < 604800:
                    time_str = f"Last {seconds//86400} days"
                else:
                    time_str = f"Last {seconds//604800} weeks"
            
            embed = EmbedBuilder.create_success_embed(
                f"Server Statistics - {interaction.guild.name}",
                description,
                footer=time_str if time_str else "All time"
            )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(embed=EmbedBuilder.create_error_embed(
                "Error",
                f"Failed to show server statistics: {str(e)}"
            ))
    
    @app_commands.command(name='timeofday', description='Show command usage by time of day')
    @app_commands.describe(time_period='Time period to show stats for (1h, 1d, 1w, 1m)')
    async def timeofday(self, interaction: discord.Interaction, time_period: Optional[str] = None):
        """Show command usage by time of day"""
        try:
            # Convert time period to seconds
            seconds = None
            if time_period:
                unit = time_period[-1].lower()
                value = int(time_period[:-1])
                if unit == 'h':
                    seconds = value * 3600
                elif unit == 'd':
                    seconds = value * 86400
                elif unit == 'w':
                    seconds = value * 604800
                elif unit == 'm':
                    seconds = value * 2592000
                else:
                    await interaction.response.send_message(embed=EmbedBuilder.create_error_embed(
                        "Error",
                        "Invalid time period. Use format: 1h, 1d, 1w, 1m"
                    ))
                    return
            
            # Get time of day stats
            stats = self.usage_tracker.get_time_of_day_stats(seconds)
            
            if not stats:
                await interaction.response.send_message(embed=EmbedBuilder.create_error_embed(
                    "Error",
                    "No usage data available for the specified time period."
                ))
                return
            
            # Create graph
            plt.figure(figsize=(12, 6))
            hours = list(stats.keys())
            counts = list(stats.values())
            
            # Create bar chart
            plt.bar(hours, counts)
            plt.title('Command Usage by Time of Day')
            plt.xlabel('Hour of Day (UTC)')
            plt.ylabel('Usage Count')
            plt.xticks(rotation=45)
            plt.grid(True, axis='y')
            
            # Save plot to bytes
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight')
            buf.seek(0)
            plt.close()
            
            # Create embed
            time_str = ""
            if seconds:
                if seconds < 3600:
                    time_str = f"Last {seconds//60} minutes"
                elif seconds < 86400:
                    time_str = f"Last {seconds//3600} hours"
                elif seconds < 604800:
                    time_str = f"Last {seconds//86400} days"
                else:
                    time_str = f"Last {seconds//604800} weeks"
            
            # Find peak hours
            peak_hours = sorted(stats.items(), key=lambda x: x[1], reverse=True)[:3]
            peak_text = "\n".join([f"{hour}:00 UTC: {count} uses" for hour, count in peak_hours])
            
            embed = EmbedBuilder.create_success_embed(
                "Time of Day Statistics",
                f"**Peak Usage Hours**\n{peak_text}",
                footer=time_str if time_str else "All time"
            )
            
            # Send graph
            await interaction.response.send_message(embed=embed, file=discord.File(buf, 'timeofday.png'))
            
        except Exception as e:
            await interaction.response.send_message(embed=EmbedBuilder.create_error_embed(
                "Error",
                f"Failed to show time of day statistics: {str(e)}"
            ))

async def setup(bot):
    await bot.add_cog(StatsCommand(bot)) 