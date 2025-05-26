import discord

class EmbedBuilder:
    @staticmethod
    def create_error_embed(title: str, description: str) -> discord.Embed:
        """Create an error embed"""
        return discord.Embed(
            title=title,
            description=description,
            color=discord.Color.red()
        )
    
    @staticmethod
    def create_success_embed(title: str, description: str) -> discord.Embed:
        """Create a success embed"""
        return discord.Embed(
            title=title,
            description=description,
            color=discord.Color.green()
        )
    
    @staticmethod
    def create_info_embed(title: str, description: str) -> discord.Embed:
        """Create an info embed"""
        return discord.Embed(
            title=title,
            description=description,
            color=discord.Color.blue()
        ) 