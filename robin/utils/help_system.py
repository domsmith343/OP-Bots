import discord
from discord.ext import commands
from typing import List, Dict, Optional
from .embeds import EmbedBuilder
import math

class HelpSystem:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.commands_per_page = 5
    
    def get_command_help(self, command: commands.Command) -> discord.Embed:
        """Create a help embed for a specific command"""
        # Get command signature
        signature = f"{command.name} {command.signature}" if command.signature else command.name
        
        # Build description
        description = command.help or "No description available."
        
        # Add aliases if any
        if command.aliases:
            description += f"\n\n**Aliases:** {', '.join(command.aliases)}"
        
        # Add usage examples if available
        if hasattr(command, 'examples'):
            description += "\n\n**Examples:**"
            for example in command.examples:
                description += f"\n`{self.bot.command_prefix}{example}`"
        
        # Add cooldown info if any
        if hasattr(command, '_buckets'):
            cooldown = command._buckets._cooldown
            if cooldown:
                description += f"\n\n**Cooldown:** {cooldown.per} seconds"
        
        return EmbedBuilder.create_success_embed(
            f"Command: {command.name}",
            description,
            fields=[
                ("Usage", f"`{self.bot.command_prefix}{signature}`", False)
            ]
        )
    
    def get_cog_help(self, cog: commands.Cog) -> discord.Embed:
        """Create a help embed for a cog"""
        # Get all commands in the cog
        commands_list = [cmd for cmd in cog.get_commands() if not cmd.hidden]
        
        if not commands_list:
            return EmbedBuilder.create_error_embed(
                "Error",
                "No commands found in this category."
            )
        
        # Build description
        description = cog.description or "No description available."
        
        # Add command list
        command_list = "\n\n**Commands:**"
        for cmd in commands_list:
            command_list += f"\n`{cmd.name}` - {cmd.short_doc or 'No description'}"
        
        return EmbedBuilder.create_success_embed(
            f"Category: {cog.qualified_name}",
            description + command_list
        )
    
    async def get_all_commands_help(self, ctx: commands.Context) -> List[discord.Embed]:
        """Create paginated help embeds for all commands"""
        # Get all commands
        commands_list = []
        for cog in self.bot.cogs.values():
            for cmd in cog.get_commands():
                if not cmd.hidden and await cmd.can_run(ctx):
                    commands_list.append(cmd)
        
        # Sort commands by name
        commands_list.sort(key=lambda x: x.name)
        
        # Create pages
        pages = []
        total_pages = math.ceil(len(commands_list) / self.commands_per_page)
        
        for i in range(total_pages):
            start_idx = i * self.commands_per_page
            end_idx = start_idx + self.commands_per_page
            page_commands = commands_list[start_idx:end_idx]
            
            description = "**Available Commands:**\n\n"
            for cmd in page_commands:
                description += f"`{cmd.name}` - {cmd.short_doc or 'No description'}\n"
            
            description += f"\nPage {i + 1}/{total_pages}"
            
            embed = EmbedBuilder.create_success_embed(
                "Command Help",
                description,
                footer=f"Use {self.bot.command_prefix}help <command> for detailed help"
            )
            pages.append(embed)
        
        return pages
    
    def get_command_categories(self) -> Dict[str, List[commands.Command]]:
        """Get commands grouped by category"""
        categories = {}
        
        for cog in self.bot.cogs.values():
            category_name = cog.qualified_name
            commands_list = [cmd for cmd in cog.get_commands() if not cmd.hidden]
            if commands_list:
                categories[category_name] = commands_list
        
        return categories
    
    async def get_category_help(self, ctx: commands.Context) -> List[discord.Embed]:
        """Create paginated help embeds for command categories"""
        categories = self.get_command_categories()
        
        # Create pages
        pages = []
        total_pages = math.ceil(len(categories) / self.commands_per_page)
        
        for i in range(total_pages):
            start_idx = i * self.commands_per_page
            end_idx = start_idx + self.commands_per_page
            page_categories = list(categories.items())[start_idx:end_idx]
            
            description = "**Command Categories:**\n\n"
            for category_name, commands_list in page_categories:
                description += f"**{category_name}**\n"
                for cmd in commands_list:
                    if await cmd.can_run(ctx):
                        description += f"`{cmd.name}` - {cmd.short_doc or 'No description'}\n"
                description += "\n"
            
            description += f"\nPage {i + 1}/{total_pages}"
            
            embed = EmbedBuilder.create_success_embed(
                "Command Categories",
                description,
                footer=f"Use {self.bot.command_prefix}help <category> for category details"
            )
            pages.append(embed)
        
        return pages 