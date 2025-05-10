"""Configuration settings for the DSA Bot."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
COMMAND_PREFIX = '/'

# File paths
INI_FILE_PATH = 'user_ini.txt'

# Discord configuration
DEFAULT_TIMEOUT = 180  # seconds 