"""View for handling dice throws."""

import random
import discord
from discord import ButtonStyle
from discord.ui import Button, View
from models.user import User
import asyncio

class ThrowTypeView(View):
    """View for selecting the type of throw."""

    def __init__(self, user: User, timeout: int = 180, debug: int = None, is_dm: bool = False):
        """Initialize the throw type view.

        Args:
            user (User): The user making the throw
            timeout (int, optional): View timeout in seconds. Defaults to 180.
            debug (int, optional): Debug value for testing. Defaults to None.
            is_dm (bool, optional): Whether this is a DM throw. Defaults to False.
        """
        super().__init__(timeout=timeout)
        self.user = user
        self.debug = debug
        self.is_dm = is_dm
        self.add_throw_type_buttons()

    def add_throw_type_buttons(self) -> None:
        """Add buttons for throw type selection."""
        print("Adding throw type buttons...")
        simple_button = Button(
            label="Simple Throw (1 Attribute)",
            custom_id="throw_simple",
            style=ButtonStyle.primary,
            row=0
        )
        full_button = Button(
            label="Full Throw (3 Attributes)",
            custom_id="throw_full",
            style=ButtonStyle.success,
            row=0
        )
        simple_button.callback = self.simple_callback
        full_button.callback = self.full_callback
        self.add_item(simple_button)
        self.add_item(full_button)
        print("Throw type buttons added")

    async def simple_callback(self, interaction: discord.Interaction) -> None:
        """Handle simple throw selection.

        Args:
            interaction (discord.Interaction): The interaction that triggered this callback
        """
        if str(interaction.user.id) != str(self.user.id):
            await interaction.response.send_message("This is not your throw!", ephemeral=True)
            return

        view = DiceThrowView(self.user, debug=self.debug, is_dm=self.is_dm, simple=True)
        await interaction.response.edit_message(
            content="Select your attribute and adjust the modifier:",
            view=view
        )

    async def full_callback(self, interaction: discord.Interaction) -> None:
        """Handle full throw selection.

        Args:
            interaction (discord.Interaction): The interaction that triggered this callback
        """
        if str(interaction.user.id) != str(self.user.id):
            await interaction.response.send_message("This is not your throw!", ephemeral=True)
            return

        view = DiceThrowView(self.user, debug=self.debug, is_dm=self.is_dm, simple=False)
        await interaction.response.edit_message(
            content="Select your attributes and adjust the modifier:",
            view=view
        )

class DiceThrowView(View):
    """View for handling dice throws with attribute selection."""

    def __init__(self, user: User, timeout: int = 180, debug: int = None, is_dm: bool = False, simple: bool = False):
        """Initialize the dice throw view.

        Args:
            user (User): The user making the throw
            timeout (int, optional): View timeout in seconds. Defaults to 180.
            debug (int, optional): Debug value for testing. Defaults to None.
            is_dm (bool, optional): Whether this is a DM throw. Defaults to False.
            simple (bool, optional): Whether this is a simple attribute throw. Defaults to False.
        """
        super().__init__(timeout=timeout)
        self.user = user
        self.selected_attributes = []
        self.modifier = 0
        self.rolls = {}
        self.debug = debug
        self.is_dm = is_dm
        self.simple = simple
        print(f"\n=== Initializing DiceThrowView ===")
        print(f"User: {user.name} ({user.id})")
        print(f"Character: {user.char_name}")
        print(f"Debug mode: {debug}")
        print(f"DM throw: {is_dm}")
        print(f"Simple throw: {simple}")
        self.add_attribute_buttons()
        self.add_modifier_buttons()
        self.add_confirm_button()

    def add_attribute_buttons(self) -> None:
        """Add buttons for attribute selection."""
        print("Adding attribute buttons...")
        attributes = [
            ("MU", "Mut"),
            ("KL", "Klugheit"),
            ("IN", "Intuition"),
            ("CH", "Charisma"),
            ("FF", "Fingerfertigkeit"),
            ("GE", "Gewandtheit"),
            ("KO", "Konstitution"),
            ("KK", "Körperkraft")
        ]
        
        # Add attributes in rows of 4
        for i, (attr, name) in enumerate(attributes):
            button = Button(
                label=f"{attr} ({name})",
                custom_id=f"attr_{attr}",
                style=ButtonStyle.primary,
                row=i // 4
            )
            button.callback = self.attribute_callback
            self.add_item(button)
        print("Attribute buttons added")

    def add_modifier_buttons(self) -> None:
        """Add buttons for modifier adjustment."""
        print("Adding modifier buttons...")
        minus_button = Button(
            label="-1",
            custom_id="mod_minus",
            style=ButtonStyle.danger,
            row=2
        )
        plus_button = Button(
            label="+1",
            custom_id="mod_plus",
            style=ButtonStyle.success,
            row=2
        )
        minus_button.callback = self.modifier_callback
        plus_button.callback = self.modifier_callback
        self.add_item(minus_button)
        self.add_item(plus_button)
        print("Modifier buttons added")

    def add_confirm_button(self) -> None:
        """Add the confirm button."""
        print("Adding confirm button...")
        confirm_button = Button(
            label="Confirm Throw",
            custom_id="confirm_throw",
            style=ButtonStyle.success,
            row=2
        )
        confirm_button.callback = self.confirm_callback
        self.add_item(confirm_button)
        print("Confirm button added")

    async def attribute_callback(self, interaction: discord.Interaction) -> None:
        """Handle attribute button clicks.

        Args:
            interaction (discord.Interaction): The interaction that triggered this callback
        """
        print(f"\n=== Attribute Selection ===")
        print(f"User: {interaction.user.name} ({interaction.user.id})")
        print(f"Expected user: {self.user.name} ({self.user.id})")
        
        if str(interaction.user.id) != str(self.user.id):
            print("Wrong user tried to use the throw")
            await interaction.response.send_message("This is not your throw!", ephemeral=True)
            return

        max_attributes = 1 if self.simple else 3
        if len(self.selected_attributes) >= max_attributes:
            print(f"User tried to select more than {max_attributes} attributes")
            await interaction.response.send_message(f"You have already selected {max_attributes} attribute{'s' if max_attributes > 1 else ''}!", ephemeral=True)
            return

        button = interaction.data.get("custom_id")
        if not button:
            print("Could not identify button")
            await interaction.response.send_message("Error: Could not identify the button!", ephemeral=True)
            return

        attr = button.split('_')[1]
        self.selected_attributes.append(attr)
        print(f"Selected attribute: {attr}")
        
        selection_text = []
        for i, attr in enumerate(self.selected_attributes):
            attr_value = getattr(self.user, attr)
            selection_text.append(f"{i+1}. {attr}: {attr_value}")
        
        print(f"Current selection: {selection_text}")
        await interaction.response.edit_message(
            content=f"Selected attributes:\n" + "\n".join(selection_text),
            view=self
        )

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

        selection_text = []
        for i, attr in enumerate(self.selected_attributes):
            attr_value = getattr(self.user, attr)
            mod_str = f" ({self.modifier:+d})" if self.modifier != 0 else ""
            selection_text.append(f"{i+1}. {attr}: {attr_value}{mod_str}")
        
        print(f"Updated selection: {selection_text}")
        await interaction.response.edit_message(
            content=f"Selected attributes:\n" + "\n".join(selection_text),
            view=self
        )

    async def play_sound(self, interaction: discord.Interaction, sound_id: int) -> None:
        """Play a soundboard sound in the voice channel.

        Args:
            interaction (discord.Interaction): The interaction that triggered this callback
            sound_id (int): ID of the soundboard sound to play
        """
        try:
            # Get the user's voice channel
            if not interaction.user.voice:
                print("User is not in a voice channel")
                return

            voice_channel = interaction.user.voice.channel
            print(f"User is in voice channel: {voice_channel.name}")

            # Play the soundboard sound using the correct format
            sound = discord.BaseSoundboardSound(id=sound_id, volume=1.0)
            await voice_channel.send_sound(sound)
            print(f"Playing soundboard sound: {sound_id}")

        except Exception as e:
            print(f"Error playing sound: {str(e)}")

    async def confirm_callback(self, interaction: discord.Interaction) -> None:
        """Handle confirm button clicks.

        Args:
            interaction (discord.Interaction): The interaction that triggered this callback
        """
        try:
            print(f"\n=== Confirming Throw ===")
            print(f"User: {interaction.user.name} ({interaction.user.id})")
            print(f"Expected user: {self.user.name} ({self.user.id})")
            print(f"Selected attributes: {self.selected_attributes}")
            print(f"Modifier: {self.modifier}")
            
            if str(interaction.user.id) != str(self.user.id):
                print("Wrong user tried to use the throw")
                await interaction.response.send_message("This is not your throw!", ephemeral=True)
                return

            required_attributes = 1 if self.simple else 3
            if len(self.selected_attributes) != required_attributes:
                print(f"User tried to confirm with wrong number of attributes")
                await interaction.response.send_message(f"You need to select exactly {required_attributes} attribute{'s' if required_attributes > 1 else ''}!", ephemeral=True)
                return

            # Defer the response immediately to prevent timeout
            await interaction.response.defer()

            # Make the rolls
            if self.debug is not None:
                print(f"Using debug value: {self.debug}")
                if self.debug == 1:
                    self.rolls = {0: 1, 1: 1, 2: random.randint(1, 20)}
                elif self.debug == 20:
                    self.rolls = {0: 20, 1: 20, 2: random.randint(1, 20)}
            else:
                self.rolls = {i: random.randint(1, 20) for i in range(required_attributes)}
            print(f"Rolls: {self.rolls}")

            # Check for party and doom effects
            party_effect = len([r for r in self.rolls.values() if r == 1]) >= 2
            doom_effect = len([r for r in self.rolls.values() if r == 20]) >= 2
            print(f"Party effect: {party_effect}")
            print(f"Doom effect: {doom_effect}")

            # Perform the throw
            results = []
            total_diff = 0
            any_failures = False
            all_success = True

            for i, attr in enumerate(self.selected_attributes):
                roll = self.rolls[i]
                attr_value = getattr(self.user, attr)
                modified_attr = attr_value + self.modifier
                success = roll <= modified_attr
                diff = 0 if success else roll - modified_attr
                total_diff += diff
                
                if not success:
                    any_failures = True
                    all_success = False

                result = f"{attr}: {roll}"
                if not success:
                    result += f" (Diff: {diff:+d})"
                results.append(result)
                print(f"Attribute {attr}: Roll={roll}, Value={attr_value}, Modified={modified_attr}, Success={success}, Diff={diff}")

            print(f"Total difference: {total_diff}")
            print(f"All success: {all_success}")

            # Create result embed
            embed = discord.Embed(
                title=f"🎲 Dice Throw Results - {self.user.char_name}",
                color=discord.Color.blue()
            )

            # Play appropriate sound based on result
            if party_effect:
                embed.color = discord.Color.green()
                embed.description = "🎉 Two 1s were rolled!"
                await self.play_sound(interaction, 1370159584701976656)  # Party effect sound
            elif doom_effect:
                embed.color = discord.Color.red()
                embed.description = "💀 Two 20s were rolled!"
                await self.play_sound(interaction, 1370159584701976657)  # Doom effect sound
            elif all_success:
                embed.color = discord.Color.green()
                embed.description = "✅ All checks successful!"
                await self.play_sound(interaction, 1370159584701976658)  # Success sound

            for result in results:
                embed.add_field(name="", value=result, inline=False)
            
            embed.add_field(
                name="Total Difference",
                value=f"{total_diff:+d}",
                inline=False
            )

            print("Sending results to user")
            # Use followup since we deferred the response
            await interaction.followup.edit_message(
                message_id=interaction.message.id,
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