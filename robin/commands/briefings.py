import discord
from discord.ext import commands
from discord import app_commands
from utils.scheduler import Scheduler
from utils.embeds import EmbedBuilder
from utils.usage_tracker import UsageTracker
from typing import Optional
import datetime
import pytz

class BriefingsCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.scheduler = Scheduler(bot)
        self.usage_tracker = UsageTracker()
    
    async def send_daily_briefing(self, channel: discord.TextChannel):
        """Send a daily briefing to the specified channel"""
        try:
            # Get command usage stats for the last 24 hours
            stats = self.usage_tracker.get_command_stats(86400)
            
            # Get top commands
            top_commands = sorted(stats.items(), key=lambda x: x[1]['total_uses'], reverse=True)[:5]
            
            # Get error stats
            error_stats = self.usage_tracker.get_error_stats(86400)
            
            # Create briefing embed
            embed = EmbedBuilder.create_success_embed(
                "Daily Command Usage Briefing",
                "Here's your daily command usage summary:"
            )
            
            # Add top commands
            top_commands_text = "\n".join([
                f"**{cmd}**: {data['total_uses']} uses ({data['success_rate']:.1f}% success)"
                for cmd, data in top_commands
            ])
            embed.add_field(name="Top Commands", value=top_commands_text or "No commands used", inline=False)
            
            # Add error summary
            if error_stats:
                error_text = "\n".join([
                    f"**{cmd}**: {sum(errors.values())} errors"
                    for cmd, errors in error_stats.items()
                ])
                embed.add_field(name="Command Errors", value=error_text, inline=False)
            
            # Add total usage
            total_commands = sum(data['total_uses'] for data in stats.values())
            total_successful = sum(data['successful_uses'] for data in stats.values())
            success_rate = (total_successful / total_commands * 100) if total_commands > 0 else 0
            
            embed.add_field(
                name="Overall Statistics",
                value=f"Total Commands: {total_commands}\nSuccess Rate: {success_rate:.1f}%",
                inline=False
            )
            
            await channel.send(embed=embed)
            
        except Exception as e:
            print(f"Error sending daily briefing: {str(e)}")
    
    async def send_weekly_briefing(self, channel: discord.TextChannel):
        """Send a weekly briefing to the specified channel"""
        try:
            # Get command usage stats for the last 7 days
            stats = self.usage_tracker.get_command_stats(604800)
            
            # Get top commands
            top_commands = sorted(stats.items(), key=lambda x: x[1]['total_uses'], reverse=True)[:10]
            
            # Get error stats
            error_stats = self.usage_tracker.get_error_stats(604800)
            
            # Get usage trends
            trends = self.usage_tracker.get_usage_trends(604800)
            
            # Create briefing embed
            embed = EmbedBuilder.create_success_embed(
                "Weekly Command Usage Briefing",
                "Here's your weekly command usage summary:"
            )
            
            # Add top commands
            top_commands_text = "\n".join([
                f"**{cmd}**: {data['total_uses']} uses ({data['success_rate']:.1f}% success)"
                for cmd, data in top_commands
            ])
            embed.add_field(name="Top Commands", value=top_commands_text or "No commands used", inline=False)
            
            # Add error summary
            if error_stats:
                error_text = "\n".join([
                    f"**{cmd}**: {sum(errors.values())} errors"
                    for cmd, errors in error_stats.items()
                ])
                embed.add_field(name="Command Errors", value=error_text, inline=False)
            
            # Add total usage
            total_commands = sum(data['total_uses'] for data in stats.values())
            total_successful = sum(data['successful_uses'] for data in stats.values())
            success_rate = (total_successful / total_commands * 100) if total_commands > 0 else 0
            
            embed.add_field(
                name="Overall Statistics",
                value=f"Total Commands: {total_commands}\nSuccess Rate: {success_rate:.1f}%",
                inline=False
            )
            
            # Add usage trends
            if trends:
                trend_text = "\n".join([
                    f"**{cmd}**: {sum(data.values())} uses this week"
                    for cmd, data in trends.items()
                ])
                embed.add_field(name="Weekly Trends", value=trend_text, inline=False)
            
            await channel.send(embed=embed)
            
        except Exception as e:
            print(f"Error sending weekly briefing: {str(e)}")
    
    async def send_monthly_briefing(self, channel: discord.TextChannel):
        """Send a monthly briefing to the specified channel"""
        try:
            # Get command usage stats for the last 30 days
            stats = self.usage_tracker.get_command_stats(2592000)
            
            # Get top commands
            top_commands = sorted(stats.items(), key=lambda x: x[1]['total_uses'], reverse=True)[:15]
            
            # Get error stats
            error_stats = self.usage_tracker.get_error_stats(2592000)
            
            # Get usage trends
            trends = self.usage_tracker.get_usage_trends(2592000)
            
            # Create briefing embed
            embed = EmbedBuilder.create_success_embed(
                "Monthly Command Usage Briefing",
                "Here's your monthly command usage summary:"
            )
            
            # Add top commands
            top_commands_text = "\n".join([
                f"**{cmd}**: {data['total_uses']} uses ({data['success_rate']:.1f}% success)"
                for cmd, data in top_commands
            ])
            embed.add_field(name="Top Commands", value=top_commands_text or "No commands used", inline=False)
            
            # Add error summary
            if error_stats:
                error_text = "\n".join([
                    f"**{cmd}**: {sum(errors.values())} errors"
                    for cmd, errors in error_stats.items()
                ])
                embed.add_field(name="Command Errors", value=error_text, inline=False)
            
            # Add total usage
            total_commands = sum(data['total_uses'] for data in stats.values())
            total_successful = sum(data['successful_uses'] for data in stats.values())
            success_rate = (total_successful / total_commands * 100) if total_commands > 0 else 0
            
            embed.add_field(
                name="Overall Statistics",
                value=f"Total Commands: {total_commands}\nSuccess Rate: {success_rate:.1f}%",
                inline=False
            )
            
            # Add usage trends
            if trends:
                trend_text = "\n".join([
                    f"**{cmd}**: {sum(data.values())} uses this month"
                    for cmd, data in trends.items()
                ])
                embed.add_field(name="Monthly Trends", value=trend_text, inline=False)
            
            await channel.send(embed=embed)
            
        except Exception as e:
            print(f"Error sending monthly briefing: {str(e)}")
    
    @app_commands.command(name='schedule', description='Schedule a briefing')
    @app_commands.describe(
        channel='Channel to send briefings to',
        time='Time to send briefings (HH:MM, 24-hour format)',
        type='Type of briefing (daily, weekly, monthly)',
        timezone='Timezone for the briefing time (default: UTC)'
    )
    async def schedule(self, interaction: discord.Interaction, 
                      channel: discord.TextChannel,
                      time: str,
                      type: str = 'daily',
                      timezone: Optional[str] = 'UTC'):
        """Schedule a briefing"""
        try:
            # Parse time
            try:
                hour, minute = map(int, time.split(':'))
                briefing_time = datetime.time(hour, minute)
            except ValueError:
                await interaction.response.send_message(embed=EmbedBuilder.create_error_embed(
                    "Error",
                    "Invalid time format. Use HH:MM (24-hour format)"
                ))
                return
            
            # Set timezone
            try:
                self.scheduler.set_timezone(timezone)
            except ValueError as e:
                await interaction.response.send_message(embed=EmbedBuilder.create_error_embed(
                    "Error",
                    str(e)
                ))
                return
            
            # Create briefing task
            async def briefing_task():
                if type == 'daily':
                    await self.send_daily_briefing(channel)
                elif type == 'weekly':
                    await self.send_weekly_briefing(channel)
                elif type == 'monthly':
                    await self.send_monthly_briefing(channel)
            
            # Set interval based on type
            if type == 'daily':
                interval = 86400  # 24 hours
            elif type == 'weekly':
                interval = 604800  # 7 days
            elif type == 'monthly':
                interval = 2592000  # 30 days
            else:
                await interaction.response.send_message(embed=EmbedBuilder.create_error_embed(
                    "Error",
                    "Invalid briefing type. Use: daily, weekly, or monthly"
                ))
                return
            
            # Add task to scheduler
            self.scheduler.add_task(
                name=f"briefing_{type}_{channel.id}",
                callback=briefing_task,
                interval=interval,
                start_time=briefing_time
            )
            
            # Send confirmation
            embed = EmbedBuilder.create_success_embed(
                "Briefing Scheduled",
                f"{type.capitalize()} briefings will be sent to {channel.mention} at {time} {timezone}"
            )
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(embed=EmbedBuilder.create_error_embed(
                "Error",
                f"Failed to schedule briefing: {str(e)}"
            ))
    
    @app_commands.command(name='unschedule', description='Remove a scheduled briefing')
    @app_commands.describe(channel='Channel to remove briefing from')
    async def unschedule(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Remove a scheduled briefing"""
        try:
            task_name = f"briefing_{channel.id}"
            if task_name in self.scheduler.tasks:
                self.scheduler.remove_task(task_name)
                await interaction.response.send_message(embed=EmbedBuilder.create_success_embed(
                    "Briefing Removed",
                    f"Daily briefings have been removed from {channel.mention}"
                ))
            else:
                await interaction.response.send_message(embed=EmbedBuilder.create_error_embed(
                    "Error",
                    f"No briefing scheduled for {channel.mention}"
                ))
        except Exception as e:
            await interaction.response.send_message(embed=EmbedBuilder.create_error_embed(
                "Error",
                f"Failed to remove briefing: {str(e)}"
            ))
    
    @app_commands.command(name='briefings', description='List all scheduled briefings')
    async def briefings(self, interaction: discord.Interaction):
        """List all scheduled briefings"""
        try:
            tasks = self.scheduler.get_all_tasks()
            briefing_tasks = [t for t in tasks if t['name'].startswith('briefing_')]
            
            if not briefing_tasks:
                await interaction.response.send_message(embed=EmbedBuilder.create_error_embed(
                    "No Briefings",
                    "No briefings are currently scheduled"
                ))
                return
            
            description = "**Scheduled Briefings**\n\n"
            for task in briefing_tasks:
                channel_id = int(task['name'].split('_')[1])
                channel = self.bot.get_channel(channel_id)
                if channel:
                    next_time = task['next_iteration'].astimezone(self.scheduler.timezone)
                    description += f"**{channel.mention}**\n"
                    description += f"Next Briefing: {next_time.strftime('%Y-%m-%d %H:%M %Z')}\n\n"
            
            embed = EmbedBuilder.create_success_embed(
                "Scheduled Briefings",
                description
            )
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(embed=EmbedBuilder.create_error_embed(
                "Error",
                f"Failed to list briefings: {str(e)}"
            ))

async def setup(bot):
    await bot.add_cog(BriefingsCommand(bot)) 