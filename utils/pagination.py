import discord
from typing import List, Any, Callable, Optional
from discord.ext import commands

class Paginator:
    def __init__(self, items: List[Any], items_per_page: int = 5):
        self.items = items
        self.items_per_page = items_per_page
        self.current_page = 0
        self.total_pages = (len(items) + items_per_page - 1) // items_per_page

    def get_page(self, page: int) -> List[Any]:
        """Get items for a specific page"""
        start = page * self.items_per_page
        end = start + self.items_per_page
        return self.items[start:end]

    def get_current_page(self) -> List[Any]:
        """Get items for current page"""
        return self.get_page(self.current_page)

class PaginatedView(discord.ui.View):
    def __init__(self, paginator: Paginator, format_func: Callable[[List[Any]], discord.Embed]):
        super().__init__(timeout=180)  # 3 minutes timeout
        self.paginator = paginator
        self.format_func = format_func
        self.message: Optional[discord.Message] = None

    async def start(self, ctx: commands.Context):
        """Start the pagination"""
        self.message = await ctx.send(
            embed=self.format_func(self.paginator.get_current_page()),
            view=self
        )

    @discord.ui.button(label="◀️", style=discord.ButtonStyle.grey)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Go to previous page"""
        if self.paginator.current_page > 0:
            self.paginator.current_page -= 1
            await interaction.response.edit_message(
                embed=self.format_func(self.paginator.get_current_page())
            )

    @discord.ui.button(label="▶️", style=discord.ButtonStyle.grey)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Go to next page"""
        if self.paginator.current_page < self.paginator.total_pages - 1:
            self.paginator.current_page += 1
            await interaction.response.edit_message(
                embed=self.format_func(self.paginator.get_current_page())
            )

    async def on_timeout(self):
        """Handle timeout"""
        if self.message:
            await self.message.edit(view=None)

class PaginatedEmbed:
    def __init__(self, items: List[Any], items_per_page: int = 5):
        self.paginator = Paginator(items, items_per_page)

    async def send(self, ctx: commands.Context, format_func: Callable[[List[Any]], discord.Embed]):
        """Send paginated embed"""
        view = PaginatedView(self.paginator, format_func)
        await view.start(ctx) 