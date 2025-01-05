import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv("API_URL", "https://api.telegram.org")
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() in ("true", "1", "t")

# Fix API URLs with complete HTTPS paths
COCKTAIL_API_URL = "www.thecocktaildb.com/api/json/v1/1/random.php"
COCKTAIL_SEARCH_API_URL = "www.thecocktaildb.com/api/json/v1/1/search.php?s={query}"
COCKTAIL_LETTER_SEARCH_API_URL = "www.thecocktaildb.com/api/json/v1/1/search.php?f={letter}"
INGREDIENT_SEARCH_API_URL = "www.thecocktaildb.com/api/json/v1/1/search.php?i={ingredient}"
DRINKS_BY_INGREDIENT_API_URL = "www.thecocktaildb.com/api/json/v1/1/filter.php?i={ingredient}"