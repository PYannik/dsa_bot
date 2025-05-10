"""Dungeon master management cog for the DSA Bot."""

import discord
from discord.ext import commands
from discord import app_commands
from models.user import User
from views.dungeon_master_roll import DungeonMasterRollView
from utils.user_manager import get_users

class DungeonMasterCog(commands.Cog):
    """Cog for handling dungeon master-related commands."""

    def __init__(self, bot: commands.Bot):
        """Initialize the dungeon master cog.

        Args:
            bot (commands.Bot): The bot instance
        """
        self.bot = bot

    @app_commands.command(name="dm", description="Make a dungeon master roll")
    async def dm_command(self, interaction: discord.Interaction):
        """Make a dungeon master roll."""
        try:
            print(f"\n=== Dungeon Master Roll Command ===")
            print(f"User: {interaction.user.name} ({interaction.user.id})")
            users = get_users()
            print(f"Current users in memory: {[f'{u.id} ({u.char_name})' for u in users]}")
            
            if not users:
                print("No characters found")
                embed = discord.Embed(
                    title="❌ No Characters Found",
                    description="No characters have been created yet!",
                    color=discord.Color.red()
                )
                embed.add_field(
                    name="How to create a character",
                    value='Use `/char_setup` to create a character.',
                    inline=False
                )
                await interaction.response.send_message(embed=embed)
                return

            print(f"Found {len(users)} characters")
            view = DungeonMasterRollView(users)
            await interaction.response.send_message(
                "Select a character to roll for:",
                view=view,
                ephemeral=True
            )
            print("Sent dungeon master roll view to user")

        except Exception as e:
            print(f"Error in dm command: {str(e)}")
            if not interaction.response.is_done():
                await interaction.response.send_message(f'❌ An error occurred: {str(e)}', ephemeral=True)
            else:
                await interaction.followup.send(f'❌ An error occurred: {str(e)}', ephemeral=True)

    @app_commands.command(name="dm_debug", description="Make a debug dungeon master roll")
    @app_commands.describe(
        value="Debug value (1 for party effect, 20 for doom effect)"
    )
    async def dm_debug_command(self, interaction: discord.Interaction, value: int):
        """Make a debug dungeon master roll.

        Args:
            interaction (discord.Interaction): The interaction that triggered this command
            value (int): Debug value (1 for party effect, 20 for doom effect)
        """
        try:
            print(f"\n=== Debug Dungeon Master Roll Command ===")
            print(f"User: {interaction.user.name} ({interaction.user.id})")
            print(f"Debug value: {value}")
            users = get_users()
            print(f"Current users in memory: {[f'{u.id} ({u.char_name})' for u in users]}")
            
            if value not in [1, 20]:
                print(f"Invalid debug value: {value}")
                await interaction.response.send_message(
                    "Debug value must be either 1 (party effect) or 20 (doom effect)!",
                    ephemeral=True
                )
                return

            if not users:
                print("No characters found")
                embed = discord.Embed(
                    title="❌ No Characters Found",
                    description="No characters have been created yet!",
                    color=discord.Color.red()
                )
                embed.add_field(
                    name="How to create a character",
                    value='Use `/char_setup` to create a character.',
                    inline=False
                )
                await interaction.response.send_message(embed=embed)
                return

            print(f"Found {len(users)} characters")
            view = DungeonMasterRollView(users, debug=value)
            await interaction.response.send_message(
                "Select a character to roll for:",
                view=view,
                ephemeral=True
            )
            print("Sent debug dungeon master roll view to user")

        except Exception as e:
            print(f"Error in dm_debug command: {str(e)}")
            if not interaction.response.is_done():
                await interaction.response.send_message(f'❌ An error occurred: {str(e)}', ephemeral=True)
            else:
                await interaction.followup.send(f'❌ An error occurred: {str(e)}', ephemeral=True)

async def setup(bot: commands.Bot):
    """Set up the dungeon master cog.

    Args:
        bot (commands.Bot): The bot instance
    """
    await bot.add_cog(DungeonMasterCog(bot)) 