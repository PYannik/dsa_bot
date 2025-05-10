"""Dice management cog for the DSA Bot."""

import discord
from discord.ext import commands
from discord import app_commands
from models.user import User
from views.dice_throw import ThrowTypeView
from utils.user_manager import get_users, set_users, save_all_users
import random

class DiceCog(commands.Cog):
    """Cog for handling dice-related commands."""

    def __init__(self, bot: commands.Bot):
        """Initialize the dice cog.

        Args:
            bot (commands.Bot): The bot instance
        """
        self.bot = bot

    @app_commands.command(name="throw", description="Make a dice throw")
    async def throw_command(self, interaction: discord.Interaction):
        """Make a dice throw.

        Args:
            interaction (discord.Interaction): The interaction that triggered this command
        """
        try:
            print(f"\n=== Dice Throw Command ===")
            print(f"User: {interaction.user.name} ({interaction.user.id})")
            users = get_users()
            print(f"Current users in memory: {[f'{u.id} ({u.char_name})' for u in users]}")
            
            current_user = next((user for user in users if str(user.id) == str(interaction.user.id)), None)
            
            if current_user is None:
                print(f"No character found for user {interaction.user.id}")
                embed = discord.Embed(
                    title="❌ No Character Found",
                    description=f"No character found for {interaction.user.name}",
                    color=discord.Color.red()
                )
                embed.add_field(
                    name="How to create a character",
                    value='Use `/char_setup` to create your character.',
                    inline=False
                )
                await interaction.response.send_message(embed=embed)
                return

            print(f"Found character: {current_user.char_name}")
            view = ThrowTypeView(current_user, is_dm=False)
            await interaction.response.send_message(
                "Choose your throw type:",
                view=view
            )
            print("Sent throw type selection view to user")

        except Exception as e:
            print(f"Error in throw command: {str(e)}")
            if not interaction.response.is_done():
                await interaction.response.send_message(f'❌ An error occurred: {str(e)}', ephemeral=True)
            else:
                await interaction.followup.send(f'❌ An error occurred: {str(e)}', ephemeral=True)

    @app_commands.command(name="throw_debug", description="Make a debug dice throw")
    @app_commands.describe(
        debug_value="The value to use for the first two dice (1 or 20)"
    )
    async def throw_debug_command(self, interaction: discord.Interaction, debug_value: int):
        """Make a debug dice throw.

        Args:
            interaction (discord.Interaction): The interaction that triggered this command
            debug_value (int): The value to use for the first two dice (1 or 20)
        """
        try:
            print(f"\n=== Debug Dice Throw Command ===")
            print(f"User: {interaction.user.name} ({interaction.user.id})")
            print(f"Debug value: {debug_value}")
            users = get_users()
            print(f"Current users in memory: {[f'{u.id} ({u.char_name})' for u in users]}")
            
            current_user = next((user for user in users if str(user.id) == str(interaction.user.id)), None)
            
            if current_user is None:
                print(f"No character found for user {interaction.user.id}")
                embed = discord.Embed(
                    title="❌ No Character Found",
                    description=f"No character found for {interaction.user.name}",
                    color=discord.Color.red()
                )
                embed.add_field(
                    name="How to create a character",
                    value='Use `/char_setup` to create your character.',
                    inline=False
                )
                await interaction.response.send_message(embed=embed)
                return

            print(f"Found character: {current_user.char_name}")
            view = ThrowTypeView(current_user, debug=debug_value, is_dm=False)
            await interaction.response.send_message(
                "Choose your throw type:",
                view=view
            )
            print("Sent debug throw type selection view to user")

        except Exception as e:
            print(f"Error in throw_debug command: {str(e)}")
            if not interaction.response.is_done():
                await interaction.response.send_message(f'❌ An error occurred: {str(e)}', ephemeral=True)
            else:
                await interaction.followup.send(f'❌ An error occurred: {str(e)}', ephemeral=True)

async def setup(bot: commands.Bot):
    """Set up the dice cog.

    Args:
        bot (commands.Bot): The bot instance
    """
    await bot.add_cog(DiceCog(bot)) 