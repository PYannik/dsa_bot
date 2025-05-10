"""View for handling dungeon master rolls."""

import discord
from models.user import User
from views.dice_throw import DiceThrowView

class DungeonMasterRollView(discord.ui.View):
    """View for handling dungeon master rolls."""

    def __init__(self, users: list[User], debug: int = None):
        """Initialize the dungeon master roll view.

        Args:
            users (list[User]): List of users to choose from
            debug (int, optional): Debug value for testing. Defaults to None.
        """
        super().__init__(timeout=300)  # 5 minute timeout
        self.debug = debug
        self.users = users  # Store users list as instance variable
        self.add_character_buttons(users)

    def add_character_buttons(self, users: list[User]):
        """Add character selection buttons to the view.

        Args:
            users (list[User]): List of users to create buttons for
        """
        for user in users:
            button = discord.ui.Button(
                label=user.char_name,
                custom_id=f"char_{user.id}",
                style=discord.ButtonStyle.primary
            )
            button.callback = self.character_callback
            self.add_item(button)

    async def character_callback(self, interaction: discord.Interaction):
        """Handle character selection.

        Args:
            interaction (discord.Interaction): The interaction that triggered this callback
        """
        try:
            # Get the selected character
            char_id = interaction.data["custom_id"].split("_")[1]
            selected_user = next((user for user in self.users if str(user.id) == char_id), None)
            
            if not selected_user:
                await interaction.response.send_message(
                    "Selected character not found!",
                    ephemeral=True
                )
                return

            # Create dice throw view for the selected character
            view = DiceThrowView(selected_user, debug=self.debug, is_dm=True)
            await interaction.response.edit_message(
                content=f"Making throw for {selected_user.char_name}. Select up to 3 attributes:",
                view=view
            )

        except Exception as e:
            print(f"Error in character callback: {str(e)}")
            await interaction.response.send_message(f'❌ An error occurred: {str(e)}') 