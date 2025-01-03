import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv("API_URL", "https://api.telegram.org")
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() in ("true", "1", "t")
COCKTAIL_API_URL = "www.thecocktaildb.com/api/json/v1/1/random.php"
COCKTAIL_SEARCH_API_URL = "www.thecocktaildb.com/api/json/v1/1/search.php?s={query}"