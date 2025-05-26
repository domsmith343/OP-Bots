import discord
from discord.ext import commands
from typing import List, Optional
from .embeds import EmbedBuilder

class PaginationView(discord.ui.View):
    def __init__(self, embeds: List[discord.Embed], timeout: int = 180):
        super().__init__(timeout=timeout)
        self.embeds = embeds
        self.current_page = 0
        self.total_pages = len(embeds)
        
        # Update button states
        self.update_buttons()
    
    def update_buttons(self):
        """Update button states based on current page"""
        self.first_page.disabled = self.current_page == 0
        self.prev_page.disabled = self.current_page == 0
        self.next_page.disabled = self.current_page == self.total_pages - 1
        self.last_page.disabled = self.current_page == self.total_pages - 1
    
    @discord.ui.button(
        emoji="⏮️",
        style=discord.ButtonStyle.grey,
        custom_id="first_page"
    )
    async def first_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Go to first page"""
        self.current_page = 0
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)
    
    @discord.ui.button(
        emoji="◀️",
        style=discord.ButtonStyle.grey,
        custom_id="prev_page"
    )
    async def prev_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Go to previous page"""
        self.current_page = max(0, self.current_page - 1)
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)
    
    @discord.ui.button(
        emoji="▶️",
        style=discord.ButtonStyle.grey,
        custom_id="next_page"
    )
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Go to next page"""
        self.current_page = min(self.total_pages - 1, self.current_page + 1)
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)
    
    @discord.ui.button(
        emoji="⏭️",
        style=discord.ButtonStyle.grey,
        custom_id="last_page"
    )
    async def last_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Go to last page"""
        self.current_page = self.total_pages - 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)
    
    @discord.ui.button(
        emoji="❌",
        style=discord.ButtonStyle.red,
        custom_id="stop"
    )
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Stop pagination"""
        await interaction.message.delete()
        self.stop()

class Paginator:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    async def paginate(self, ctx: commands.Context, embeds: List[discord.Embed], timeout: int = 180):
        """Start pagination with the given embeds"""
        if not embeds:
            await ctx.send(embed=EmbedBuilder.create_error_embed(
                "Error",
                "No content to paginate."
            ))
            return
        
        # Create pagination view
        view = PaginationView(embeds, timeout)
        
        # Send first page
        message = await ctx.send(embed=embeds[0], view=view)
        
        # Wait for view to timeout
        await view.wait()
        
        # Remove buttons after timeout
        try:
            await message.edit(view=None)
        except discord.NotFound:
            pass  # Message was deleted 