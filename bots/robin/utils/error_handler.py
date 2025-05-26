import discord
from discord.ext import commands
from typing import Optional, Union
from .embeds import EmbedBuilder

class CommandError(commands.CommandError):
    """Base class for custom command errors"""
    pass

class APIError(CommandError):
    """Error raised when API calls fail"""
    pass

class CommandCooldown(CommandError):
    """Error raised when command is on cooldown"""
    pass

async def handle_error(ctx: commands.Context, error: Union[Exception, CommandError]) -> None:
    """Handle different types of errors and send appropriate responses"""
    # Track command usage
    if hasattr(ctx.command, 'cog') and hasattr(ctx.command.cog, 'tracker'):
        success = False
        error_message = str(error)
        
        if isinstance(error, commands.CommandOnCooldown):
            embed = EmbedBuilder.create_error_embed(
                "Command on Cooldown",
                f"Please wait {error.retry_after:.1f} seconds before using this command again."
            )
            await ctx.send(embed=embed)
            ctx.command.cog.tracker.track_command(
                ctx.command.name,
                ctx.author.id,
                ctx.guild.id if ctx.guild else None,
                ctx.channel.id,
                success,
                error_message
            )
            return

        if isinstance(error, commands.MissingRequiredArgument):
            embed = EmbedBuilder.create_error_embed(
                "Missing Argument",
                f"Missing required argument: {error.param.name}"
            )
            await ctx.send(embed=embed)
            ctx.command.cog.tracker.track_command(
                ctx.command.name,
                ctx.author.id,
                ctx.guild.id if ctx.guild else None,
                ctx.channel.id,
                success,
                error_message
            )
            return

        if isinstance(error, commands.BadArgument):
            embed = EmbedBuilder.create_error_embed(
                "Invalid Argument",
                "One or more arguments were invalid. Please check your input and try again."
            )
            await ctx.send(embed=embed)
            ctx.command.cog.tracker.track_command(
                ctx.command.name,
                ctx.author.id,
                ctx.guild.id if ctx.guild else None,
                ctx.channel.id,
                success,
                error_message
            )
            return

        if isinstance(error, commands.CommandNotFound):
            embed = EmbedBuilder.create_error_embed(
                "Command Not Found",
                "The command you're looking for doesn't exist."
            )
            await ctx.send(embed=embed)
            return

        if isinstance(error, APIError):
            embed = EmbedBuilder.create_error_embed(
                "API Error",
                str(error)
            )
            await ctx.send(embed=embed)
            ctx.command.cog.tracker.track_command(
                ctx.command.name,
                ctx.author.id,
                ctx.guild.id if ctx.guild else None,
                ctx.channel.id,
                success,
                error_message
            )
            return

        if isinstance(error, CommandCooldown):
            embed = EmbedBuilder.create_error_embed(
                "Command on Cooldown",
                str(error)
            )
            await ctx.send(embed=embed)
            ctx.command.cog.tracker.track_command(
                ctx.command.name,
                ctx.author.id,
                ctx.guild.id if ctx.guild else None,
                ctx.channel.id,
                success,
                error_message
            )
            return

        # Handle any other errors
        embed = EmbedBuilder.create_error_embed(
            "Error",
            "An unexpected error occurred. Please try again later."
        )
        await ctx.send(embed=embed)
        ctx.command.cog.tracker.track_command(
            ctx.command.name,
            ctx.author.id,
            ctx.guild.id if ctx.guild else None,
            ctx.channel.id,
            success,
            error_message
        ) 