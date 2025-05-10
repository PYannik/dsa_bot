"""Initiative management cog for the DSA Bot."""

import discord
from discord.ext import commands
from discord import app_commands
from models.user import User
from utils.user_manager import get_users, set_users, save_all_users
import random

class InitiativeView(discord.ui.View):
    """View for handling initiative rolls."""

    def __init__(self, user: User, timeout: int = 180):
        """Initialize the initiative view.

        Args:
            user (User): The user making the throw
            timeout (int, optional): View timeout in seconds. Defaults to 180.
        """
        super().__init__(timeout=timeout)
        self.user = user
        self.modifier = 0
        self.add_modifier_buttons()
        self.add_confirm_button()

    def add_modifier_buttons(self) -> None:
        """Add buttons for modifier adjustment."""
        print("Adding modifier buttons...")
        minus_button = discord.ui.Button(
            label="-1",
            custom_id="mod_minus",
            style=discord.ButtonStyle.danger,
            row=0
        )
        plus_button = discord.ui.Button(
            label="+1",
            custom_id="mod_plus",
            style=discord.ButtonStyle.success,
            row=0
        )
        minus_button.callback = self.modifier_callback
        plus_button.callback = self.modifier_callback
        self.add_item(minus_button)
        self.add_item(plus_button)
        print("Modifier buttons added")

    def add_confirm_button(self) -> None:
        """Add the confirm button."""
        print("Adding confirm button...")
        confirm_button = discord.ui.Button(
            label="Roll Initiative",
            custom_id="confirm_throw",
            style=discord.ButtonStyle.primary,
            row=0
        )
        confirm_button.callback = self.confirm_callback
        self.add_item(confirm_button)
        print("Confirm button added")

    async def modifier_callback(self, interaction: discord.Interaction) -> None:
        """Handle modifier button clicks.

        Args:
            interaction (discord.Interaction): The interaction that triggered this callback
        """
        print(f"\n=== Modifier Adjustment ===")
        print(f"User: {interaction.user.name} ({interaction.user.id})")
        print(f"Expected user: {self.user.name} ({self.user.id})")
        
        if str(interaction.user.id) != str(self.user.id):
            print("Wrong user tried to use the throw")
            await interaction.response.send_message("This is not your throw!", ephemeral=True)
            return

        button = interaction.data.get("custom_id")
        if not button:
            print("Could not identify button")
            await interaction.response.send_message("Error: Could not identify the button!", ephemeral=True)
            return

        change = -1 if button == "mod_minus" else 1
        self.modifier += change
        print(f"New modifier value: {self.modifier}")

        # Update message to show current modifier
        await interaction.response.edit_message(
            content=f"Current modifier: {self.modifier:+d}",
            view=self
        )

    async def confirm_callback(self, interaction: discord.Interaction) -> None:
        """Handle confirm button clicks.

        Args:
            interaction (discord.Interaction): The interaction that triggered this callback
        """
        try:
            print(f"\n=== Confirming Initiative Roll ===")
            print(f"User: {interaction.user.name} ({interaction.user.id})")
            print(f"Expected user: {self.user.name} ({self.user.id})")
            print(f"Modifier: {self.modifier}")
            
            if str(interaction.user.id) != str(self.user.id):
                print("Wrong user tried to use the throw")
                await interaction.response.send_message("This is not your throw!", ephemeral=True)
                return

            # Make the roll
            roll = random.randint(1, 6)
            total = self.user.ini + roll + self.modifier
            self.user.current_ini = total

            # Create result embed
            embed = discord.Embed(
                title="🎲 Initiative Roll",
                color=discord.Color.blue()
            )
            embed.add_field(name="Player", value=self.user.name, inline=True)
            embed.add_field(name="Base Initiative", value=str(self.user.ini), inline=True)
            embed.add_field(name="Roll", value=f"1d6 = {roll}", inline=True)
            if self.modifier != 0:
                embed.add_field(name="Modifier", value=f"{self.modifier:+d}", inline=True)
            embed.add_field(name="Total", value=str(total), inline=True)

            # Update user in the list
            users = get_users()
            users = [user for user in users if str(user.id) != str(self.user.id)]
            users.append(self.user)
            set_users(users)
            save_all_users()

            # Send new message with results and remove the view
            await interaction.response.edit_message(
                content=None,
                embed=embed,
                view=None
            )

        except Exception as e:
            print(f"Error in confirm callback: {str(e)}")
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ An error occurred: {str(e)}", ephemeral=True)
            else:
                await interaction.followup.send(f"❌ An error occurred: {str(e)}", ephemeral=True)

class InitiativeCog(commands.Cog):
    """Cog for handling initiative-related commands."""

    def __init__(self, bot: commands.Bot):
        """Initialize the initiative cog.

        Args:
            bot (commands.Bot): The bot instance
        """
        self.bot = bot
        self.initiative_order = []

    @app_commands.command(name="init", description="Roll for initiative")
    async def init_command(self, interaction: discord.Interaction):
        """Roll for initiative."""
        try:
            print(f"\n=== Initiative Roll Command ===")
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
            view = InitiativeView(current_user)
            await interaction.response.send_message(
                "Adjust your initiative modifier and click 'Roll Initiative':",
                view=view
            )
            print("Sent initiative roll view to user")

        except Exception as e:
            print(f"Error in init command: {str(e)}")
            if not interaction.response.is_done():
                await interaction.response.send_message(f'❌ An error occurred: {str(e)}', ephemeral=True)
            else:
                await interaction.followup.send(f'❌ An error occurred: {str(e)}', ephemeral=True)

    @app_commands.command(name="init_order", description="Show current initiative order")
    async def init_order_command(self, interaction: discord.Interaction):
        """Show current initiative order."""
        try:
            print(f"\n=== Initiative Order Command ===")
            users = get_users()
            print(f"Current users in memory: {[f'{u.id} ({u.char_name})' for u in users]}")
            
            # Sort users by current initiative
            sorted_users = sorted(users, key=lambda x: x.current_ini, reverse=True)
            
            if not sorted_users:
                embed = discord.Embed(
                    title="❌ No Initiative Rolls",
                    description="No one has rolled for initiative yet!",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed)
                return

            embed = discord.Embed(
                title="📋 Initiative Order",
                color=discord.Color.blue()
            )
            
            for i, user in enumerate(sorted_users, 1):
                embed.add_field(
                    name=f"{i}. {user.char_name}",
                    value=f"Initiative: {user.current_ini}",
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed)

        except Exception as e:
            print(f"Error in init_order command: {str(e)}")
            if not interaction.response.is_done():
                await interaction.response.send_message(f'❌ An error occurred: {str(e)}', ephemeral=True)
            else:
                await interaction.followup.send(f'❌ An error occurred: {str(e)}', ephemeral=True)

    @app_commands.command(name="init_reset", description="Reset all initiative rolls")
    async def init_reset_command(self, interaction: discord.Interaction):
        """Reset all initiative rolls."""
        try:
            print(f"\n=== Initiative Reset Command ===")
            users = get_users()
            print(f"Current users in memory: {[f'{u.id} ({u.char_name})' for u in users]}")
            
            # Reset all current initiative values
            for user in users:
                user.current_ini = 0
            
            set_users(users)
            save_all_users()
            
            embed = discord.Embed(
                title="🔄 Initiative Reset",
                description="All initiative rolls have been reset!",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)

        except Exception as e:
            print(f"Error in init_reset command: {str(e)}")
            if not interaction.response.is_done():
                await interaction.response.send_message(f'❌ An error occurred: {str(e)}', ephemeral=True)
            else:
                await interaction.followup.send(f'❌ An error occurred: {str(e)}', ephemeral=True)

async def setup(bot: commands.Bot):
    """Set up the initiative cog.

    Args:
        bot (commands.Bot): The bot instance
    """
    await bot.add_cog(InitiativeCog(bot)) 