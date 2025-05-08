import discord
from discord.ext import commands
import re
import random
from discord import ButtonStyle
from discord.ui import Button, View



# This example requires the 'message_content' intent.

import discord

intents = discord.Intents.default()
intents.message_content = True


client = discord.Client(intents=intents)

ini_file_path = 'user_ini.txt'
users = []

class User:
    def __init__(self, id, name, char_name):
        self.id = id
        self.name = name
        self.char_name = char_name
        self.ini = 0
        self.current_ini = 0
        # DSA attributes
        self.MU = 0  # Mut
        self.KL = 0  # Klugheit
        self.IN = 0  # Intuition
        self.CH = 0  # Charisma
        self.FF = 0  # Fingerfertigkeit
        self.GE = 0  # Gewandtheit
        self.KO = 0  # Konstitution
        self.KK = 0  # Körperkraft

    def to_string(self):
        return f"{self.id},{self.name},{self.char_name},{self.ini},{self.MU},{self.KL},{self.IN},{self.CH},{self.FF},{self.GE},{self.KO},{self.KK}"

    @classmethod
    def from_string(cls, string):
        parts = string.strip().split(',')
        if len(parts) >= 12:  # We need at least 12 parts for all attributes
            user = cls(int(parts[0]), parts[1], parts[2])
            user.ini = int(parts[3])
            user.MU = int(parts[4])
            user.KL = int(parts[5])
            user.IN = int(parts[6])
            user.CH = int(parts[7])
            user.FF = int(parts[8])
            user.GE = int(parts[9])
            user.KO = int(parts[10])
            user.KK = int(parts[11])
            return user
        return None

class DiceThrowView(View):
    def __init__(self, user, timeout=180, debug=None):
        super().__init__(timeout=timeout)
        self.user = user
        self.selected_attributes = []
        self.modifier = 0
        self.rolls = {}
        self.debug = debug
        self.add_attribute_buttons()
        self.add_modifier_buttons()
        self.add_confirm_button()

    def add_attribute_buttons(self):
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

    def add_modifier_buttons(self):
        # Add a single row of modifier buttons
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

    def add_confirm_button(self):
        confirm_button = Button(
            label="Confirm Throw",
            custom_id="confirm_throw",
            style=ButtonStyle.success,
            row=2
        )
        confirm_button.callback = self.confirm_callback
        self.add_item(confirm_button)

    def add_reroll_button(self):
        reroll_button = Button(
            label="Reroll Highest",
            custom_id="reroll_highest",
            style=ButtonStyle.danger,
            row=2
        )
        reroll_button.callback = self.reroll_callback
        self.add_item(reroll_button)

    async def attribute_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("This is not your throw!", ephemeral=True)
            return

        if len(self.selected_attributes) >= 3:
            await interaction.response.send_message("You have already selected 3 attributes!", ephemeral=True)
            return

        # Get the button that was clicked
        button = interaction.data.get("custom_id")
        if not button:
            await interaction.response.send_message("Error: Could not identify the button!", ephemeral=True)
            return

        attr = button.split('_')[1]
        self.selected_attributes.append(attr)
        
        # Update message to show only selected attributes
        selection_text = []
        for i, attr in enumerate(self.selected_attributes):
            attr_value = getattr(self.user, attr)
            selection_text.append(f"{i+1}. {attr}: {attr_value}")
        
        await interaction.response.edit_message(
            content=f"Selected attributes:\n" + "\n".join(selection_text),
            view=self
        )

    async def modifier_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("This is not your throw!", ephemeral=True)
            return

        # Get the button that was clicked
        button = interaction.data.get("custom_id")
        if not button:
            await interaction.response.send_message("Error: Could not identify the button!", ephemeral=True)
            return

        # Update the modifier
        change = -1 if button == "mod_minus" else 1
        self.modifier += change

        # Update message to show selected attributes with modifier
        selection_text = []
        for i, attr in enumerate(self.selected_attributes):
            attr_value = getattr(self.user, attr)
            mod_str = f" ({self.modifier:+d})" if self.modifier != 0 else ""
            selection_text.append(f"{i+1}. {attr}: {attr_value}{mod_str}")
        
        await interaction.response.edit_message(
            content=f"Selected attributes:\n" + "\n".join(selection_text),
            view=self
        )

    async def reroll_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("This is not your throw!", ephemeral=True)
            return

        # Find the highest roll
        highest_roll = max(self.rolls.items(), key=lambda x: x[1])
        highest_index = highest_roll[0]
        highest_attr = self.selected_attributes[highest_index]

        # Make the new roll
        if self.debug is not None:
            new_roll = self.debug
        else:
            new_roll = random.randint(1, 20)
        self.rolls[highest_index] = new_roll

        # Perform the throw with modifier
        results = []
        total_diff = 0
        for i, attr in enumerate(self.selected_attributes):
            roll = self.rolls[i]
            attr_value = getattr(self.user, attr)
            # For negative modifiers, add to attribute (easier), for positive, subtract (harder)
            modified_attr = attr_value + self.modifier
            # Success is when roll is less than or equal to the attribute
            success = roll <= modified_attr
            # For failed throws, difference is how much we missed by
            diff = 0 if success else roll - modified_attr
            total_diff += diff

            # Only show difference for failed throws
            result = f"{attr}: {roll}"
            if not success:
                result += f" (Diff: {diff:+d})"
            results.append(result)

        # Create result embed
        embed = discord.Embed(
            title=f"🎲 Dice Throw Results (Rerolled) - {self.user.char_name}",
            color=discord.Color.blue()
        )

        # Check for party and doom effects
        party_effect = len([r for r in self.rolls.values() if r == 1]) >= 2
        doom_effect = len([r for r in self.rolls.values() if r == 20]) >= 2

        # Add party or doom effect if applicable
        if party_effect:
            embed.color = discord.Color.green()
            # Send the critical hit GIF
            await interaction.channel.send("https://tenor.com/view/critical-critical-hit-cri-critical-gif-25499123")
        elif doom_effect:
            embed.color = discord.Color.red()
            # Send the failure GIF
            await interaction.channel.send("https://tenor.com/view/failure-boo-simpsons-zero-gif-17012756229140509599")

        for result in results:
            embed.add_field(name="", value=result, inline=False)
        
        # Add total difference
        embed.add_field(
            name="Total Difference",
            value=f"{total_diff:+d}",
            inline=False
        )

        # Send new message with results and remove the view
        await interaction.response.edit_message(
            content=None,
            embed=embed,
            view=None
        )

    async def confirm_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("This is not your throw!", ephemeral=True)
            return

        if len(self.selected_attributes) != 3:
            await interaction.response.send_message("You need to select exactly 3 attributes!", ephemeral=True)
            return

        # Make the rolls when confirming
        if self.debug is not None:
            # For party effect, set two 1s
            if self.debug == 1:
                self.rolls = {0: 1, 1: 1, 2: random.randint(1, 20)}
            # For doom effect, set two 20s
            elif self.debug == 20:
                self.rolls = {0: 20, 1: 20, 2: random.randint(1, 20)}
        else:
            self.rolls = {i: random.randint(1, 20) for i in range(3)}

        # Check for party and doom effects
        party_effect = len([r for r in self.rolls.values() if r == 1]) >= 2
        doom_effect = len([r for r in self.rolls.values() if r == 20]) >= 2

        # Perform the throw with modifier
        results = []
        total_diff = 0
        any_failures = False
        for i, attr in enumerate(self.selected_attributes):
            roll = self.rolls[i]
            attr_value = getattr(self.user, attr)
            # For negative modifiers, add to attribute (easier), for positive, subtract (harder)
            modified_attr = attr_value + self.modifier
            # Success is when roll is less than or equal to the attribute
            success = roll <= modified_attr
            # For failed throws, difference is how much we missed by
            diff = 0 if success else roll - modified_attr
            total_diff += diff
            if not success:
                any_failures = True

            # Only show difference for failed throws
            result = f"{attr}: {roll}"
            if not success:
                result += f" (Diff: {diff:+d})"
            results.append(result)

        # Create result embed
        embed = discord.Embed(
            title=f"🎲 Dice Throw Results - {self.user.char_name}",
            color=discord.Color.blue()
        )

        # Add party or doom effect if applicable
        if party_effect:
            embed.color = discord.Color.green()
            # Send the critical hit GIF
            await interaction.channel.send("https://tenor.com/view/critical-critical-hit-cri-critical-gif-25499123")
        elif doom_effect:
            embed.color = discord.Color.red()
            # Send the failure GIF
            await interaction.channel.send("https://tenor.com/view/failure-boo-simpsons-zero-gif-17012756229140509599")

        for result in results:
            embed.add_field(name="", value=result, inline=False)
        
        # Add total difference
        embed.add_field(
            name="Total Difference",
            value=f"{total_diff:+d}",
            inline=False
        )

        # If there are any failures, add the reroll button
        if any_failures:
            self.clear_items()
            self.add_reroll_button()
            await interaction.response.edit_message(
                content=None,
                embed=embed,
                view=self
            )
        else:
            # Send new message with results and remove the view
            await interaction.response.edit_message(
                content=None,
                embed=embed,
                view=None
            )

class SingleAttributeThrowView(View):
    def __init__(self, user, timeout=180, debug=None):
        super().__init__(timeout=timeout)
        self.user = user
        self.selected_attribute = None
        self.modifier = 0
        self.roll = None
        self.debug = debug
        self.add_attribute_buttons()
        self.add_modifier_buttons()
        self.add_confirm_button()

    def add_attribute_buttons(self):
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

    def add_modifier_buttons(self):
        # Add a single row of modifier buttons
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

    def add_confirm_button(self):
        confirm_button = Button(
            label="Confirm Throw",
            custom_id="confirm_throw",
            style=ButtonStyle.success,
            row=2
        )
        confirm_button.callback = self.confirm_callback
        self.add_item(confirm_button)

    async def attribute_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("This is not your throw!", ephemeral=True)
            return

        # Get the button that was clicked
        button = interaction.data.get("custom_id")
        if not button:
            await interaction.response.send_message("Error: Could not identify the button!", ephemeral=True)
            return

        attr = button.split('_')[1]
        self.selected_attribute = attr
        
        # Update message to show selected attribute
        attr_value = getattr(self.user, attr)
        await interaction.response.edit_message(
            content=f"Selected attribute:\n{attr}: {attr_value}",
            view=self
        )

    async def modifier_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("This is not your throw!", ephemeral=True)
            return

        if not self.selected_attribute:
            await interaction.response.send_message("Please select an attribute first!", ephemeral=True)
            return

        # Get the button that was clicked
        button = interaction.data.get("custom_id")
        if not button:
            await interaction.response.send_message("Error: Could not identify the button!", ephemeral=True)
            return

        # Update the modifier
        change = -1 if button == "mod_minus" else 1
        self.modifier += change

        # Update message to show selected attribute with modifier
        attr_value = getattr(self.user, self.selected_attribute)
        mod_str = f" ({self.modifier:+d})" if self.modifier != 0 else ""
        await interaction.response.edit_message(
            content=f"Selected attribute:\n{self.selected_attribute}: {attr_value}{mod_str}",
            view=self
        )

    async def confirm_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("This is not your throw!", ephemeral=True)
            return

        if not self.selected_attribute:
            await interaction.response.send_message("Please select an attribute first!", ephemeral=True)
            return

        # Make the roll when confirming
        if self.debug is not None:
            self.roll = self.debug
        else:
            self.roll = random.randint(1, 20)

        # Perform the throw with modifier
        attr_value = getattr(self.user, self.selected_attribute)
        # For negative modifiers, add to attribute (easier), for positive, subtract (harder)
        modified_attr = attr_value + self.modifier
        # Success is when roll is less than or equal to the attribute
        success = self.roll <= modified_attr
        # For failed throws, difference is how much we missed by
        diff = 0 if success else self.roll - modified_attr

        # Create result embed
        embed = discord.Embed(
            title="🎲 Dice Throw Result",
            color=discord.Color.blue()
        )
        
        # Add party or doom effect if applicable
        if self.roll == 1:
            embed.description = "🎉 **Party Effect!** A 1 was rolled!"
            embed.color = discord.Color.green()
        elif self.roll == 20:
            embed.description = "💀 **Doom Effect!** A 20 was rolled!"
            embed.color = discord.Color.red()
        
        # Only show difference for failed throws
        result = f"{self.selected_attribute}: {self.roll}"
        if not success:
            result += f" (Diff: {diff:+d})"
        
        embed.add_field(name="", value=result, inline=False)

        # Send new message with results and remove the view
        await interaction.response.edit_message(
            content=None,
            embed=embed,
            view=None
        )

class InitiativeRollView(View):
    def __init__(self, user, timeout=180):
        super().__init__(timeout=timeout)
        self.user = user
        self.modifier = 0
        self.roll = None
        self.add_modifier_buttons()
        self.add_confirm_button()

    def add_modifier_buttons(self):
        # Add a single row of modifier buttons
        minus_button = Button(
            label="-1",
            custom_id="mod_minus",
            style=ButtonStyle.danger,
            row=0
        )
        plus_button = Button(
            label="+1",
            custom_id="mod_plus",
            style=ButtonStyle.success,
            row=0
        )
        minus_button.callback = self.modifier_callback
        plus_button.callback = self.modifier_callback
        self.add_item(minus_button)
        self.add_item(plus_button)

    def add_confirm_button(self):
        confirm_button = Button(
            label="Roll Initiative",
            custom_id="confirm_roll",
            style=ButtonStyle.primary,
            row=0
        )
        confirm_button.callback = self.confirm_callback
        self.add_item(confirm_button)

    async def modifier_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("This is not your throw!", ephemeral=True)
            return

        # Get the button that was clicked
        button = interaction.data.get("custom_id")
        if not button:
            await interaction.response.send_message("Error: Could not identify the button!", ephemeral=True)
            return

        # Update the modifier
        change = -1 if button == "mod_minus" else 1
        self.modifier += change

        # Update message to show base initiative with modifier
        mod_str = f" ({self.modifier:+d})" if self.modifier != 0 else ""
        await interaction.response.edit_message(
            content=f"Base Initiative: {self.user.ini}{mod_str}\nClick 'Roll Initiative' to roll 1d6",
            view=self
        )

    async def confirm_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("This is not your throw!", ephemeral=True)
            return

        # Make the roll
        self.roll = random.randint(1, 6)
        # Add modifier only once to the total
        total = self.user.ini + self.roll + self.modifier
        self.user.current_ini = total

        # Create result embed
        embed = discord.Embed(
            title="🎲 Initiative Roll",
            color=discord.Color.blue()
        )
        embed.add_field(name="Player", value=self.user.name, inline=True)
        embed.add_field(name="Base Initiative", value=str(self.user.ini), inline=True)
        embed.add_field(name="Roll", value=f"1d6 = {self.roll}", inline=True)
        if self.modifier != 0:
            embed.add_field(name="Modifier", value=f"{self.modifier:+d}", inline=True)
        embed.add_field(name="Total", value=str(total), inline=True)

        # Send new message with results and remove the view
        await interaction.response.edit_message(
            content=None,
            embed=embed,
            view=None
        )

@client.event
async def on_ready():
    try:
        with open(ini_file_path, 'r') as file:
            print(f'Loading character file from {ini_file_path}')
            for line in file:
                user = User.from_string(line)
                if user:
                    users.append(user)
            print(f'Loaded {len(users)} characters')
    except FileNotFoundError:
        print(f'No character file found at {ini_file_path}')
        try:
            with open(ini_file_path, 'x') as file:
                print(f'Created new character file at {ini_file_path}')
        except FileExistsError:
            pass

    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    global users
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('**Hello!** 👋')
    
    if message.content.startswith('/char setup'):
        try:
            # Parse the command: /char setup "Character Name" MU KL IN CH FF GE KO KK INI
            parts = message.content.split('"')
            if len(parts) < 3:
                raise ValueError("Please provide a character name in quotes")
            
            char_name = parts[1]
            attr_parts = parts[2].strip().split()
            if len(attr_parts) != 9:
                raise ValueError("Need exactly 9 values after the character name: MU KL IN CH FF GE KO KK INI")
            
            values = [int(x) for x in attr_parts]
            new_user = User(message.author.id, message.author.name, char_name)
            new_user.MU = values[0]
            new_user.KL = values[1]
            new_user.IN = values[2]
            new_user.CH = values[3]
            new_user.FF = values[4]
            new_user.GE = values[5]
            new_user.KO = values[6]
            new_user.KK = values[7]
            new_user.ini = values[8]

            # Check if user already exists and remove if found
            users = [user for user in users if user.id != message.author.id]
            users.append(new_user)

            # Save to file
            with open(ini_file_path, 'w') as file:
                for user in users:
                    file.write(f'{user.to_string()}\n')

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
            await message.channel.send(embed=embed)

        except ValueError as e:
            embed = discord.Embed(
                title="❌ Invalid Input",
                description=str(e),
                color=discord.Color.red()
            )
            embed.add_field(
                name="Correct Format",
                value='`/char setup "Character Name" MU KL IN CH FF GE KO KK INI`\nExample: `/char setup "Gandalf" 12 13 14 15 16 17 18 19 20`',
                inline=False
            )
            await message.channel.send(embed=embed)
        except Exception as e:
            await message.channel.send(f'❌ An error occurred: {str(e)}')

    if message.content == '/char':
        try:
            current_user = next((user for user in users if user.id == message.author.id), None)
            
            if current_user is None:
                embed = discord.Embed(
                    title="❌ No Character Found",
                    description=f"No character found for {message.author.name}",
                    color=discord.Color.red()
                )
                embed.add_field(
                    name="How to create a character",
                    value='Use `/char setup "Character Name" MU KL IN CH FF GE KO KK INI` to create your character.',
                    inline=False
                )
                await message.channel.send(embed=embed)
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
            
            await message.channel.send(embed=embed)

        except Exception as e:
            await message.channel.send(f'❌ An error occurred: {str(e)}')

    if message.content.startswith('/d'):
        pattern = r'/d (\d+)d(20|4|6)'
        match = re.match(pattern, message.content)
        if match:
            num_dice = int(match.group(1))
            dice_type = int(match.group(2))
            await message.channel.send(f'🎲 Rolling {num_dice}d{dice_type}...')
            results = [random.randint(1,dice_type) for _ in range(num_dice)]
            result_str = ', '.join(str(x) for x in results)
            total = sum(results)
            embed = discord.Embed(
                title="🎲 Dice Roll Results",
                color=discord.Color.blue()
            )
            embed.add_field(name="Roll", value=f"{num_dice}d{dice_type}", inline=True)
            embed.add_field(name="Results", value=result_str, inline=True)
            embed.add_field(name="Total", value=str(total), inline=True)
            await message.channel.send(embed=embed)

    if message.content.startswith('/ini add'):
        try:
            ini_value = int(message.content.split('add')[1].strip())
            new_user = User(message.author.id, message.author.name, "")
            new_user.ini = ini_value
            users = [user for user in users if user.id != message.author.id]
            users.append(new_user)
            with open(ini_file_path, 'w') as file:
                for user in users:
                    file.write(f'{user.to_string()}\n')
            
            embed = discord.Embed(
                title="✅ Initiative Added",
                color=discord.Color.green()
            )
            embed.add_field(name="Player", value=message.author.name, inline=True)
            embed.add_field(name="Initiative", value=str(ini_value), inline=True)
            await message.channel.send(embed=embed)

        except (ValueError, IndexError):
            await message.channel.send('❌ Please provide a valid number after `/ini add`')
        except Exception as e:
            await message.channel.send(f'❌ An error occurred: {str(e)}')
    
    if message.content.startswith('/ini roll'):
        try:
            current_user = next((user for user in users if user.id == message.author.id), None)
            
            if current_user is None:
                embed = discord.Embed(
                    title="❌ No Initiative Found",
                    description=f"No initiative found for {message.author.name}",
                    color=discord.Color.red()
                )
                embed.add_field(
                    name="How to set initiative",
                    value='Use `/char setup "Character Name" MU KL IN CH FF GE KO KK INI` to set your base initiative.',
                    inline=False
                )
                await message.channel.send(embed=embed)
                return

            view = InitiativeRollView(current_user)
            await message.channel.send(
                f"Base Initiative: {current_user.ini}\nClick 'Roll Initiative' to roll 1d6",
                view=view
            )

        except Exception as e:
            await message.channel.send(f'❌ An error occurred: {str(e)}')
    
    if message.content == '/ini':
        try:
            if not users:
                embed = discord.Embed(
                    title="❌ No Initiative Values",
                    description="No initiative values found.",
                    color=discord.Color.red()
                )
                embed.add_field(name="How to set initiative", value='Use "/ini add <value>" to set your base initiative.')
                await message.channel.send(embed=embed)
                return
                
            embed = discord.Embed(
                title="📊 Current Initiative Values",
                color=discord.Color.blue()
            )
            for user in users:
                ini_value = user.current_ini if hasattr(user, 'current_ini') and user.current_ini is not None else user.ini
                embed.add_field(name=user.name, value=str(ini_value), inline=True)
                
            await message.channel.send(embed=embed)
            
        except Exception as e:
            await message.channel.send(f'❌ An error occurred: {str(e)}')

    if message.content.startswith('/p'):
        try:
            current_user = next((user for user in users if user.id == message.author.id), None)
            
            if current_user is None:
                embed = discord.Embed(
                    title="❌ No Character Found",
                    description=f"No character found for {message.author.name}",
                    color=discord.Color.red()
                )
                embed.add_field(
                    name="How to create a character",
                    value='Use `/char setup "Character Name" MU KL IN CH FF GE KO KK INI` to create your character.',
                    inline=False
                )
                await message.channel.send(embed=embed)
                return

            # Check for debug parameter
            debug_value = None
            if message.content.strip() == '/p debug 1':
                debug_value = 1
            elif message.content.strip() == '/p debug 20':
                debug_value = 20
            view = DiceThrowView(current_user, debug=debug_value)
            await message.channel.send(
                f"Select 3 attributes for {current_user.char_name}'s throw:",
                view=view
            )

        except Exception as e:
            await message.channel.send(f'❌ An error occurred: {str(e)}')

    if message.content.startswith('/a'):
        try:
            current_user = next((user for user in users if user.id == message.author.id), None)
            
            if current_user is None:
                embed = discord.Embed(
                    title="❌ No Character Found",
                    description=f"No character found for {message.author.name}",
                    color=discord.Color.red()
                )
                embed.add_field(
                    name="How to create a character",
                    value='Use `/char setup "Character Name" MU KL IN CH FF GE KO KK INI` to create your character.',
                    inline=False
                )
                await message.channel.send(embed=embed)
                return

            # Check for debug parameter
            debug_value = None
            if message.content.strip() == '/a debug 1':
                debug_value = 1
            elif message.content.strip() == '/a debug 20':
                debug_value = 20
            view = SingleAttributeThrowView(current_user, debug=debug_value)
            await message.channel.send(
                f"Select an attribute for {current_user.char_name}'s throw:",
                view=view
            )

        except Exception as e:
            await message.channel.send(f'❌ An error occurred: {str(e)}')

    if message.content == '/help':
        embed = discord.Embed(
            title="📖 DSA Bot Commands",
            description="Here are all available commands:",
            color=discord.Color.blue()
        )
        
        # Character Setup
        embed.add_field(
            name="Character Setup",
            value='`/char setup "Character Name" MU KL IN CH FF GE KO KK INI`\n'
                  'Creates or updates your character with the given attributes.\n'
                  'Example: `/char setup "Gandalf" 12 13 14 15 16 17 18 19 20`',
            inline=False
        )
        
        # Character Sheet
        embed.add_field(
            name="Character Sheet",
            value='`/char`\n'
                  'Displays your character sheet with all attributes.',
            inline=False
        )
        
        # Single Attribute Throw
        embed.add_field(
            name="Single Attribute Throw",
            value='`/a` - Normal throw\n'
                  '`/a debug 1` - Test throw with party effect\n'
                  '`/a debug 20` - Test throw with doom effect\n'
                  'Starts a single attribute throw. Select one attribute and optionally adjust the modifier.',
            inline=False
        )
        
        # Multiple Attribute Throw
        embed.add_field(
            name="Multiple Attribute Throw",
            value='`/p` - Normal throw\n'
                  '`/p debug 1` - Test throw with party effect\n'
                  '`/p debug 20` - Test throw with doom effect\n'
                  'Starts a throw with three attributes. Select three attributes and optionally adjust the modifier.',
            inline=False
        )
        
        # Initiative Commands
        embed.add_field(
            name="Initiative Commands",
            value='`/ini roll` - Rolls initiative (1d6 + base + modifier)\n'
                  'Use +1/-1 buttons to adjust the modifier before rolling\n'
                  '`/ini` - Shows all current initiative values',
            inline=False
        )
        
        # Dice Roll
        embed.add_field(
            name="Simple Dice Roll",
            value='`/d <number>d<type>`\n'
                  'Rolls the specified number of dice.\n'
                  'Example: `/d 2d20` rolls two d20s',
            inline=False
        )
        
        # Modifier Explanation
        embed.add_field(
            name="About Modifiers",
            value='• Positive modifiers (+1, +2, etc.) make the roll easier\n'
                  '• Negative modifiers (-1, -2, etc.) make the roll harder\n'
                  '• Success is when the roll is less than or equal to the attribute value\n',
            inline=False
        )
        
        await message.channel.send(embed=embed)

client.run('')



