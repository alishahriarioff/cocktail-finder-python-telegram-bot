import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv("API_URL", "https://api.telegram.org")
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() in ("true", "1", "t")