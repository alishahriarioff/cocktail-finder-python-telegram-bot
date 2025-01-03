import requests
from config.settings import COCKTAIL_API_URL, COCKTAIL_SEARCH_API_URL
import logging

logger = logging.getLogger(__name__)

# Add timeout constant
REQUEST_TIMEOUT = 10  # seconds

def get_random_cocktail():
    try:
        response = requests.get(f"https://{COCKTAIL_API_URL}", timeout=REQUEST_TIMEOUT)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        drink = data['drinks'][0]
        
        # Get all ingredients and measurements
        ingredients = []
        measurements = []
        for i in range(1, 16):  # API supports up to 15 ingredients
            ing = drink.get(f'strIngredient{i}')
            meas = drink.get(f'strMeasure{i}')
            if ing:
                ingredients.append(ing)
                measurements.append(meas if meas else None)
        
        return {
            'name': drink['strDrink'],
            'category': drink['strCategory'],
            'instructions': drink['strInstructions'],
            'image': drink['strDrinkThumb'],
            'ingredients': ingredients,
            'measurements': measurements
        }
    except Exception as e:
        print(f"Error fetching cocktail: {e}")
        return None

def search_cocktail(query: str):
    """Search for cocktails by name."""
    try:
        logger.info(f"Making API request for: {query}")
        url = f"https://{COCKTAIL_SEARCH_API_URL.format(query=query.replace(' ', '_'))}"
        logger.info(f"Request URL: {url}")
        
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        data = response.json()
        
        if not data or not data.get('drinks'):
            logger.info(f"No drinks found for query: {query}")
            return None
            
        drinks = []
        for drink in data['drinks']:
            ingredients = []
            measurements = []
            for i in range(1, 16):
                ing = drink.get(f'strIngredient{i}')
                meas = drink.get(f'strMeasure{i}')
                if ing:
                    ingredients.append(ing)
                    measurements.append(meas if meas else None)
            
            drinks.append({
                'name': drink['strDrink'],
                'category': drink['strCategory'],
                'instructions': drink['strInstructions'],
                'image': drink['strDrinkThumb'],
                'ingredients': ingredients,
                'measurements': measurements
            })
        
        return drinks
        
    except Exception as e:
        logger.error(f"Error searching cocktail: {e}")
        return None
