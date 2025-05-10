"""Character management cog for the DSA Bot."""

import discord
from discord.ext import commands
from discord import app_commands
from models.user import User
from utils.user_manager import get_users, set_users, save_all_users

class CharacterCog(commands.Cog):
    """Cog for handling character-related commands."""

    def __init__(self, bot: commands.Bot):
        """Initialize the character cog.

        Args:
            bot (commands.Bot): The bot instance
        """
        self.bot = bot

    @app_commands.command(name="char", description="Show your character sheet")
    async def char_command(self, interaction: discord.Interaction):
        """Show the user's character sheet."""
        try:
            print(f"Looking for user with ID: {interaction.user.id}")
            users = get_users()
            print(f"Current users in memory: {[f'{u.id} ({u.char_name})' for u in users]}")
            
            # Find user by Discord ID
            current_user = next((user for user in users if str(user.id) == str(interaction.user.id)), None)
            
            if current_user is None:
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

            embed = discord.Embed(
                title=f"📊 Character Sheet: {current_user.char_name}",
                color=discord.Color.blue()
            )
            embed.add_field(name="Player", value=current_user.name, inline=True)
            embed.add_field(name="Initiative", value=str(current_user.ini), inline=True)
            embed.add_field(name="MU (Mut)", value=str(current_user.MU), inline=True)
            embed.add_field(name="KL (Klugheit)", value=str(current_user.KL), inline=True)
            embed.add_field(name="IN (Intuition)", value=str(current_user.IN), inline=True)
            embed.add_field(name="CH (Charisma)", value=str(current_user.CH), inline=True)
            embed.add_field(name="FF (Fingerfertigkeit)", value=str(current_user.FF), inline=True)
            embed.add_field(name="GE (Gewandtheit)", value=str(current_user.GE), inline=True)
            embed.add_field(name="KO (Konstitution)", value=str(current_user.KO), inline=True)
            embed.add_field(name="KK (Körperkraft)", value=str(current_user.KK), inline=True)
            
            await interaction.response.send_message(embed=embed)

        except Exception as e:
            print(f"Error in char command: {str(e)}")
            await interaction.response.send_message(f'❌ An error occurred: {str(e)}')

    @app_commands.command(name="char_setup", description="Create or update your character")
    @app_commands.describe(
        char_name="Your character's name",
        mu="Mut value",
        kl="Klugheit value",
        in_="Intuition value",
        ch="Charisma value",
        ff="Fingerfertigkeit value",
        ge="Gewandtheit value",
        ko="Konstitution value",
        kk="Körperkraft value",
        ini="Initiative value"
    )
    async def char_setup_command(
        self,
        interaction: discord.Interaction,
        char_name: str,
        mu: int,
        kl: int,
        in_: int,
        ch: int,
        ff: int,
        ge: int,
        ko: int,
        kk: int,
        ini: int
    ):
        """Create or update a character.

        Args:
            interaction (discord.Interaction): The interaction that triggered this command
            char_name (str): Character name
            mu (int): Mut value
            kl (int): Klugheit value
            in_ (int): Intuition value
            ch (int): Charisma value
            ff (int): Fingerfertigkeit value
            ge (int): Gewandtheit value
            ko (int): Konstitution value
            kk (int): Körperkraft value
            ini (int): Initiative value
        """
        try:
            print(f"Creating character for user ID: {interaction.user.id}")
            new_user = User(str(interaction.user.id), interaction.user.name, char_name)
            new_user.MU = mu
            new_user.KL = kl
            new_user.IN = in_
            new_user.CH = ch
            new_user.FF = ff
            new_user.GE = ge
            new_user.KO = ko
            new_user.KK = kk
            new_user.ini = ini

            # Check if user already exists and remove if found
            users = get_users()
            print(f"Current users before update: {[f'{u.id} ({u.char_name})' for u in users]}")
            users = [user for user in users if str(user.id) != str(interaction.user.id)]
            users.append(new_user)
            set_users(users)
            print(f"Users after update: {[f'{u.id} ({u.char_name})' for u in users]}")

            # Save to file
            save_all_users()
            print(f"Saved users to file: {[f'{u.id} ({u.char_name})' for u in users]}")

            embed = discord.Embed(
                title="✅ Character Created",
                color=discord.Color.green()
            )
            embed.add_field(name="Character Name", value=new_user.char_name, inline=True)
            embed.add_field(name="Player", value=new_user.name, inline=True)
            embed.add_field(name="Initiative", value=str(new_user.ini), inline=True)
            embed.add_field(name="MU", value=str(new_user.MU), inline=True)
            embed.add_field(name="KL", value=str(new_user.KL), inline=True)
            embed.add_field(name="IN", value=str(new_user.IN), inline=True)
            embed.add_field(name="CH", value=str(new_user.CH), inline=True)
            embed.add_field(name="FF", value=str(new_user.FF), inline=True)
            embed.add_field(name="GE", value=str(new_user.GE), inline=True)
            embed.add_field(name="KO", value=str(new_user.KO), inline=True)
            embed.add_field(name="KK", value=str(new_user.KK), inline=True)
            await interaction.response.send_message(embed=embed)

        except Exception as e:
            print(f"Error in char_setup command: {str(e)}")
            await interaction.response.send_message(f'❌ An error occurred: {str(e)}')

async def setup(bot: commands.Bot):
    """Set up the character cog.

    Args:
        bot (commands.Bot): The bot instance
    """
    await bot.add_cog(CharacterCog(bot)) 