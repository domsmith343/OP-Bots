import discord
from discord.ext import commands
from discord import app_commands
from utils.dm_session import DMSessionManager
from utils.embeds import EmbedBuilder
from typing import Optional

class DMCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session_manager = DMSessionManager()
        
        # Register DM command handlers
        self.session_manager.register_handler('help', self._handle_help)
        self.session_manager.register_handler('stats', self._handle_stats)
        self.session_manager.register_handler('end', self._handle_end)
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Handle incoming messages for DM sessions"""
        await self.session_manager.handle_message(message)
    
    async def _handle_help(self, message: discord.Message, session):
        """Handle !help command in DMs"""
        help_text = """
**Available DM Commands:**
`!help` - Show this help message
`!stats` - Show your command usage statistics
`!end` - End your DM session

You can also use any server command here, and I'll respond privately.
        """
        await message.channel.send(embed=EmbedBuilder.create_success_embed(
            "DM Session Help",
            help_text
        ))
    
    async def _handle_stats(self, message: discord.Message, session):
        """Handle !stats command in DMs"""
        # Get user's command usage stats
        stats = self.bot.usage_tracker.get_user_stats(message.author.id)
        
        if not stats:
            await message.channel.send(embed=EmbedBuilder.create_error_embed(
                "No Statistics",
                "You haven't used any commands yet."
            ))
            return
        
        # Create stats embed
        embed = EmbedBuilder.create_success_embed(
            "Your Command Statistics",
            "Here's your command usage summary:"
        )
        
        # Add command stats
        for cmd, data in stats.items():
            embed.add_field(
                name=cmd,
                value=f"Uses: {data['total_uses']}\nSuccess Rate: {data['success_rate']:.1f}%",
                inline=True
            )
        
        await message.channel.send(embed=embed)
    
    async def _handle_end(self, message: discord.Message, session):
        """Handle !end command in DMs"""
        self.session_manager.end_session(message.author.id)
        await message.channel.send(embed=EmbedBuilder.create_success_embed(
            "Session Ended",
            "Your DM session has been ended. Start a new one by sending me a message!"
        ))
    
    @app_commands.command(name='dm', description='Start a private DM session with the bot')
    async def dm(self, interaction: discord.Interaction):
        """Start a private DM session with the bot"""
        try:
            # Create DM channel if it doesn't exist
            if not interaction.user.dm_channel:
                await interaction.user.create_dm()
            
            # Create new session
            self.session_manager.create_session(interaction.user)
            
            # Send welcome message
            embed = EmbedBuilder.create_success_embed(
                "DM Session Started",
                "I've started a private DM session with you! Use `!help` to see available commands."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Send DM
            await interaction.user.dm_channel.send(embed=EmbedBuilder.create_success_embed(
                "Welcome to DM Session",
                "You can now interact with me privately! Use `!help` to see available commands."
            ))
            
        except Exception as e:
            await interaction.response.send_message(embed=EmbedBuilder.create_error_embed(
                "Error",
                f"Failed to start DM session: {str(e)}"
            ), ephemeral=True)

async def setup(bot):
    await bot.add_cog(DMCommand(bot)) 