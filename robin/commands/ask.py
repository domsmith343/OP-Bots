import discord
from discord.ext import commands
from utils.error_handler import CommandCooldown, APIError
from utils.embeds import EmbedBuilder
from utils.conversation_memory import ConversationMemory
from utils.code_formatter import CodeFormatter
from utils.cooldown import cooldown
from utils.database import Database
import os

class AskCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database(os.path.join('robin', 'data', 'robin.db'))
        self.memory = ConversationMemory(self.db)

    @commands.command(name='ask')
    @cooldown(3)  # 3 second cooldown
    async def ask(self, ctx, *, question: str):
        """Ask a question to the LLM with conversation memory and code formatting"""
        try:
            # Add user's question to conversation history
            self.memory.add_message(ctx.author.id, "user", question)
            
            # Get conversation history
            history = self.memory.format_history_for_prompt(ctx.author.id)
            
            # Generate response using Ollama with conversation history
            response = await self.bot.ollama.generate_with_history(history)
            
            # Format code blocks in the response
            formatted_response = CodeFormatter.format_code_response(response)
            
            # Add bot's response to conversation history
            self.memory.add_message(ctx.author.id, "assistant", response)
            
            # Create and send embed
            embed = EmbedBuilder.create_success_embed(
                "🤖 Response",
                formatted_response
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(embed=EmbedBuilder.create_error_embed(
                "Error",
                f"Failed to generate response: {str(e)}"
            ))

    @commands.command(name='clear')
    @cooldown(5)  # 5 second cooldown for clear command
    async def clear_history(self, ctx):
        """Clear conversation history"""
        self.memory.clear_history(ctx.author.id)
        await ctx.send(embed=EmbedBuilder.create_success_embed(
            "History Cleared",
            "Your conversation history has been cleared."
        ))

    @commands.command(name='format')
    @cooldown(2)  # 2 second cooldown for format command
    async def format_code(self, ctx, language: str, *, code: str):
        """Format code with syntax highlighting"""
        try:
            formatted_code = CodeFormatter.create_code_embed(code, language)
            await ctx.send(formatted_code)
        except Exception as e:
            await ctx.send(embed=EmbedBuilder.create_error_embed(
                "Error",
                f"Failed to format code: {str(e)}"
            ))

async def setup(bot):
    await bot.add_cog(AskCommand(bot)) 