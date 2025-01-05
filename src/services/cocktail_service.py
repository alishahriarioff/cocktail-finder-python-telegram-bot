import requests
from config.settings import (
    COCKTAIL_API_URL, 
    COCKTAIL_SEARCH_API_URL, 
    COCKTAIL_LETTER_SEARCH_API_URL,
    INGREDIENT_SEARCH_API_URL,
    DRINKS_BY_INGREDIENT_API_URL  # Add this import
)
import logging

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT = 10

def get_random_cocktail():
    try:
        response = requests.get(f"https://{COCKTAIL_API_URL}", timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        if not data or not data.get('drinks'):
            return None
        return data['drinks'][0]
    except Exception as e:
        logger.error(f"Error fetching random cocktail: {e}")
        return None

def search_cocktail(query: str):
    try:
        url = f"https://{COCKTAIL_SEARCH_API_URL.format(query=query.replace(' ', '_'))}"
        logger.info(f"Search URL: {url}")
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        return data.get('drinks')
    except Exception as e:
        logger.error(f"Error searching cocktail: {e}")
        return None

def search_cocktail_by_letter(letter: str):
    try:
        url = f"https://{COCKTAIL_LETTER_SEARCH_API_URL.format(letter=letter)}"
        logger.info(f"Letter search URL: {url}")
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        return data.get('drinks')
    except Exception as e:
        logger.error(f"Error searching by letter: {e}")
        return None

def search_ingredient(ingredient: str):
    try:
        url = f"https://{INGREDIENT_SEARCH_API_URL.format(ingredient=ingredient.replace(' ', '_'))}"
        logger.info(f"Ingredient search URL: {url}")
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        if not data or 'ingredients' not in data or not data['ingredients']:
            return None
        return data['ingredients']
    except Exception as e:
        logger.error(f"Error searching ingredient: {e}")
        return None

def search_drinks_by_ingredient(ingredient: str):
    try:
        # Capitalize first letter of each word as the API is case sensitive
        formatted_ingredient = ' '.join(word.capitalize() for word in ingredient.split())
        url = f"https://{DRINKS_BY_INGREDIENT_API_URL.format(ingredient=formatted_ingredient.replace(' ', '_'))}"
        logger.info(f"Drinks by ingredient search URL: {url}")
        
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        
        logger.info(f"Found {len(data.get('drinks', [])) if data and 'drinks' in data else 0} drinks")
        
        if not data or 'drinks' not in data or not data['drinks']:
            logger.warning(f"No drinks found for ingredient: {formatted_ingredient}")
            return None
            
        return data['drinks']
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error searching drinks by ingredient: {e}")
        return None
    except Exception as e:
        logger.error(f"Error searching drinks by ingredient: {e}")
        return None
