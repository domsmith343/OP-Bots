import discord
from discord.ext import commands
from discord import app_commands, Interaction
from db.preferences import PreferencesDB

class PreferencesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = PreferencesDB()

    @app_commands.command(name="setprefs", description="Configure your daily brief preferences")
    async def set_preferences(self, interaction: Interaction):
        # Placeholder for actual preference logic
        await interaction.response.send_message("Preferences command coming soon!")

    @app_commands.command(name="togglebrief", description="Toggle daily brief notifications")
    async def toggle_daily_brief(self, interaction: Interaction):
        # Placeholder for toggle logic
        await interaction.response.send_message("Toggled daily brief notifications!")

async def setup(bot):
    await bot.add_cog(PreferencesCog(bot))
