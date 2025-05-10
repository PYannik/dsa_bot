# DSA Bot

A Discord bot for managing The Dark Eye (Das Schwarze Auge) tabletop RPG sessions. This bot helps players manage their characters, make dice throws, and handle initiative rolls.

## Features

### Character Management
- `/char_setup` - Create or update your character with attributes:
  - Character name
  - MU (Mut)
  - KL (Klugheit)
  - IN (Intuition)
  - CH (Charisma)
  - FF (Fingerfertigkeit)
  - GE (Gewandtheit)
  - KO (Konstitution)
  - KK (Körperkraft)
  - Initiative
- `/char` - View your character sheet

### Dice Throws
- `/throw` - Make a dice throw with two options:
  - Simple Throw (1 Attribute)
  - Full Throw (3 Attributes)
- Supports modifiers for throws
- Special effects for rolling multiple 1s (Party Effect) or 20s (Doom Effect)
- Sound effects for successful throws and special effects

### Initiative System
- `/init` - Roll for initiative with modifiers
- `/init_order` - View current initiative order
- `/init_reset` - Reset all initiative rolls

### Dungeon Master Tools
- `/dm` - Make rolls for any character (DM only)
- `/dm_debug` - Make debug rolls for testing special effects

### Voice Channel Integration
- `/join` - Bot joins your current voice channel
- `/leave` - Bot leaves the current voice channel

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/dsa_bot.git
cd dsa_bot
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with your Discord bot token:
```
BOT_TOKEN=your_discord_bot_token_here
```

5. Run the bot:
```bash
python main.py
```

## Requirements
- Python 3.8 or higher
- Discord.py
- python-dotenv

## Permissions
The bot requires the following Discord permissions:
- Send Messages
- Embed Links
- Use Slash Commands
- Connect to Voice Channels
- Play Soundboard Sounds

## Contributing
Feel free to submit issues and pull requests for any improvements or bug fixes.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
