import discord
from discord.ext import commands
from utils.help_system import HelpSystem
from utils.pagination import Paginator
from utils.embeds import EmbedBuilder
from utils.cooldown import cooldown

class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.help_system = HelpSystem(bot)
        self.paginator = Paginator(bot)
    
    @commands.command(name='help')
    @cooldown(3)
    async def help(self, ctx, *, query: str = None):
        """Show help for commands and categories
        
        Parameters:
        query: Optional. Command or category name to get help for
        """
        try:
            if query:
                # Check if query is a command
                command = self.bot.get_command(query)
                if command:
                    embed = self.help_system.get_command_help(command)
                    await ctx.send(embed=embed)
                    return
                
                # Check if query is a cog
                cog = self.bot.get_cog(query)
                if cog:
                    embed = self.help_system.get_cog_help(cog)
                    await ctx.send(embed=embed)
                    return
                
                # Query not found
                await ctx.send(embed=EmbedBuilder.create_error_embed(
                    "Error",
                    f"Command or category '{query}' not found."
                ))
                return
            
            # Show category help by default
            embeds = await self.help_system.get_category_help(ctx)
            await self.paginator.paginate(ctx, embeds)
            
        except Exception as e:
            await ctx.send(embed=EmbedBuilder.create_error_embed(
                "Error",
                f"Failed to show help: {str(e)}"
            ))
    
    @commands.command(name='commands')
    @cooldown(3)
    async def commands(self, ctx):
        """Show all available commands"""
        try:
            embeds = await self.help_system.get_all_commands_help(ctx)
            await self.paginator.paginate(ctx, embeds)
        except Exception as e:
            await ctx.send(embed=EmbedBuilder.create_error_embed(
                "Error",
                f"Failed to show commands: {str(e)}"
            ))

async def setup(bot):
    await bot.add_cog(HelpCommand(bot)) 