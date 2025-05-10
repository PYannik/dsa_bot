"""Main entry point for the DSA Bot."""

import discord
from discord.ext import commands
import asyncio
from config import BOT_TOKEN, COMMAND_PREFIX, DEFAULT_TIMEOUT
from utils.user_manager import load_all_users

# Initialize bot with intents
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

@bot.event
async def on_ready():
    """Called when the bot is ready."""
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('------')
    
    # Load users from file
    loaded_users = load_all_users()
    print(f"Loaded {len(loaded_users)} users from file:")
    for user in loaded_users:
        print(f"- {user.name} ({user.id}): {user.char_name}")
    
    # Sync commands
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.tree.command(name="sync", description="Sync bot commands")
async def sync(interaction: discord.Interaction):
    """Sync bot commands."""
    if interaction.user.id != 123456789:  # Replace with your Discord ID
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return
    
    try:
        synced = await bot.tree.sync()
        await interaction.response.send_message(f"Synced {len(synced)} command(s)", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Failed to sync commands: {e}", ephemeral=True)

@bot.tree.command(name="join", description="Join your current voice channel")
async def join(interaction: discord.Interaction):
    """Join the user's voice channel."""
    if not interaction.user.voice:
        await interaction.response.send_message("You need to be in a voice channel first!", ephemeral=True)
        return
    
    try:
        await interaction.user.voice.channel.connect()
        await interaction.response.send_message(f"Joined {interaction.user.voice.channel.name}", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Failed to join voice channel: {e}", ephemeral=True)

@bot.tree.command(name="leave", description="Leave the current voice channel")
async def leave(interaction: discord.Interaction):
    """Leave the current voice channel."""
    if not interaction.guild.voice_client:
        await interaction.response.send_message("I'm not in a voice channel!", ephemeral=True)
        return
    
    try:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("Left voice channel", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Failed to leave voice channel: {e}", ephemeral=True)

async def main():
    """Main entry point."""
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN not found in environment variables")
        return
    
    # Load cogs
    cogs = [
        'cogs.character',
        'cogs.dice',
        'cogs.initiative',
        'cogs.dungeon_master'
    ]
    
    for cog in cogs:
        try:
            await bot.load_extension(cog)
            print(f"Loaded extension: {cog}")
        except Exception as e:
            print(f"Failed to load extension {cog}: {e}")
    
    await bot.start(BOT_TOKEN)

if __name__ == "__main__":
    asyncio.run(main()) 