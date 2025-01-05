from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from services.cocktail_service import (
    get_random_cocktail, search_cocktail, search_cocktail_by_letter, 
    search_ingredient, search_drinks_by_ingredient
)
import logging
import asyncio  # Add this import at the top with other imports

logger = logging.getLogger(__name__)

# Update states to include drinks by ingredient search
(TYPING_SEARCH, TYPING_LETTER, TYPING_INGREDIENT, TYPING_DRINK_BY_INGREDIENT) = range(4)

MENU_ACTIONS = {
    'title': '🍸 Cocktail Menu',
    'options': [
        ('Get a random Drink 🎲', 'random_drink'),
        ('Search drink by name 🔍', 'search_drink'),
        ('Search drink by first letter 🔤', 'letter_search'),
        ('Search drink by ingredient 🍶', 'drinks_by_ingredient'),
        ('Search ingredient by name ℹ️', 'ingredient_search'),
    ],
    'footer_options': [
        ('Help ❓', 'help'),
        ('About 👤', 'about')
    ]
}

def create_menu_keyboard():
    """Create inline menu keyboard"""
    keyboard = []
    # Add main options
    for option_text, callback_data in MENU_ACTIONS['options']:
        keyboard.append([InlineKeyboardButton(option_text, callback_data=callback_data)])
    # Add footer buttons side by side
    footer_buttons = [
        InlineKeyboardButton(text, callback_data=data)
        for text, data in MENU_ACTIONS['footer_options']
    ]
    keyboard.append(footer_buttons)
    return InlineKeyboardMarkup(keyboard)

def get_menu_message():
    """Get menu message with inline keyboard"""
    return {
        'text': f"{MENU_ACTIONS['title']}\nWhat would you like to do?",
        'reply_markup': create_menu_keyboard(),
        'parse_mode': 'Markdown'
    }

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message with inline menu."""
    menu_msg = get_menu_message()
    await update.message.reply_text(**menu_msg)

async def random_drink(update: Update, context: ContextTypes.DEFAULT_TYPE, from_callback=False):
    """Send a random cocktail."""
    cocktail = get_random_cocktail()
    
    if not cocktail:
        error_message = "Sorry, couldn't fetch a cocktail right now. Please try again!"
        menu_msg = get_menu_message()
        if from_callback:
            await update.callback_query.message.reply_text(error_message)
            await update.callback_query.message.reply_text(**menu_msg)
        else:
            await update.message.reply_text(error_message)
            await update.message.reply_text(**menu_msg)
        return

    try:
        # Format ingredients
        ingredients = []
        for i in range(1, 16):
            ing = cocktail.get(f'strIngredient{i}')
            meas = cocktail.get(f'strMeasure{i}')
            if ing:
                if meas:
                    ingredients.append(f"🔸 {meas.strip()} {ing}")
                else:
                    ingredients.append(f"🔸 {ing}")

        message = (
            f"🎲 *Random Cocktail!* 🎲\n\n"
            f"🍸 *{cocktail['strDrink']}*\n"
            f"📑 *Category:* {cocktail.get('strCategory', 'N/A')}\n\n"
            f"🧪 *Ingredients:*\n{chr(10).join(ingredients)}\n\n"
            f"📝 *Instructions:*\n{cocktail.get('strInstructions', 'N/A')}"
        )

        if from_callback:
            sent_message = await update.callback_query.message.reply_photo(
                photo=cocktail['strDrinkThumb'],
                caption=message,
                parse_mode='Markdown'
            )
            menu_msg = get_menu_message()
            await sent_message.reply_text(**menu_msg)
        else:
            sent_message = await update.message.reply_photo(
                photo=cocktail['strDrinkThumb'],
                caption=message,
                parse_mode='Markdown'
            )
            menu_msg = get_menu_message()
            await sent_message.reply_text(**menu_msg)
    except Exception as e:
        logger.error(f"Error in random_drink: {e}")
        error_message = "Sorry, something went wrong. Please try again!"
        menu_msg = get_menu_message()
        if from_callback:
            await update.callback_query.message.reply_text(error_message)
            await update.callback_query.message.reply_text(**menu_msg)
        else:
            await update.message.reply_text(error_message)
            await update.message.reply_text(**menu_msg)

async def start_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start search conversation."""
    keyboard = [[InlineKeyboardButton("❌ Cancel Search", callback_data="cancel_search")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.answer()
        message = update.callback_query.message
    else:
        message = update.message

    await message.reply_text(
        "🔍 Please enter the name of the cocktail you're looking for:",
        reply_markup=reply_markup
    )
    return TYPING_SEARCH

async def cancel_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel search and return to main menu."""
    query = update.callback_query
    await query.answer()
    menu_msg = get_menu_message()
    await query.message.reply_text(**menu_msg)
    return ConversationHandler.END

async def search_drink(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the search query."""
    query = update.message.text.strip()
    if not query:
        await update.message.reply_text("Please enter a cocktail name to search.")
        return TYPING_SEARCH

    await update.message.reply_text("🔍 Searching...")
    drinks = search_cocktail(query)
    
    if not drinks:
        menu_msg = get_menu_message()
        await update.message.reply_text(
            f"❌ No cocktails found matching '{query}'",
            reply_markup=menu_msg['reply_markup']
        )
        return ConversationHandler.END

    try:
        await update.message.reply_text(
            f"🎯 Found {len(drinks)} cocktail(s) matching '{query}'"
        )

        for index, drink in enumerate(drinks, 1):
            ingredients = []
            for i in range(1, 16):
                ing = drink.get(f'strIngredient{i}')
                meas = drink.get(f'strMeasure{i}')
                if ing:
                    if meas:
                        ingredients.append(f"🔸 {meas.strip()} {ing}")
                    else:
                        ingredients.append(f"🔸 {ing}")

            message = (
                f"🍸 Drink {index} of {len(drinks)}\n"
                f"*{drink['strDrink']}*\n"
                f"📑 *Category:* {drink.get('strCategory', 'N/A')}\n\n"
                f"🧪 *Ingredients:*\n{chr(10).join(ingredients)}\n\n"
                f"📝 *Instructions:*\n{drink.get('strInstructions', 'N/A')}"
            )

            try:
                await update.message.reply_photo(
                    photo=drink['strDrinkThumb'],
                    caption=message,
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"Error sending photo: {e}")
                await update.message.reply_text(message, parse_mode='Markdown')

    except Exception as e:
        logger.error(f"Error in search_drink: {e}")
        await update.message.reply_text("❌ Something went wrong. Please try again!")

    menu_msg = get_menu_message()
    await update.message.reply_text(**menu_msg)
    return ConversationHandler.END

async def start_letter_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start letter search conversation."""
    keyboard = [[InlineKeyboardButton("❌ Cancel Search", callback_data="cancel_search")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.answer()
        message = update.callback_query.message
    else:
        message = update.message

    await message.reply_text(
        "🔤 Please enter a single letter (A-Z) to find cocktails:",
        reply_markup=reply_markup
    )
    return TYPING_LETTER

async def search_by_letter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the letter search query."""
    letter = update.message.text.strip().upper()
    if not letter.isalpha() or len(letter) != 1:
        await update.message.reply_text("Please enter a single letter (A-Z).")
        return TYPING_LETTER

    await update.message.reply_text(f"🔍 Searching for cocktails starting with '{letter}'...")
    drinks = search_cocktail_by_letter(letter)

    if not drinks:
        menu_msg = get_menu_message()
        await update.message.reply_text(
            f"❌ No cocktails found starting with '{letter}'",
            reply_markup=menu_msg['reply_markup']
        )
        return ConversationHandler.END

    try:
        message = f"Found {len(drinks)} cocktail(s) starting with '{letter}':\n\n"
        for drink in drinks:
            message += f"🍸 {drink['strDrink']}\n"

        # Split message if too long
        if len(message) > 4000:
            chunks = [message[i:i+4000] for i in range(0, len(message), 4000)]
            for chunk in chunks:
                await update.message.reply_text(chunk)
        else:
            await update.message.reply_text(message)

    except Exception as e:
        logger.error(f"Error in search_by_letter: {e}")
        await update.message.reply_text("❌ Something went wrong. Please try again!")

    menu_msg = get_menu_message()
    await update.message.reply_text(**menu_msg)
    return ConversationHandler.END

async def start_ingredient_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start ingredient search conversation."""
    keyboard = [[InlineKeyboardButton("❌ Cancel Search", callback_data="cancel_search")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.answer()
        message = update.callback_query.message
    else:
        message = update.message

    await message.reply_text(
        "🧪 Please enter the name of the ingredient you want to search for:",
        reply_markup=reply_markup
    )
    return TYPING_INGREDIENT

async def search_by_ingredient(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the ingredient search query."""
    query = update.message.text.strip()
    if not query:
        await update.message.reply_text("Please enter an ingredient name to search.")
        return TYPING_INGREDIENT

    await update.message.reply_text("🔍 Searching...")
    ingredients = search_ingredient(query)
    
    if not ingredients:
        menu_msg = get_menu_message()
        await update.message.reply_text(
            f"❌ No ingredients found matching '{query}'",
            reply_markup=menu_msg['reply_markup']
        )
        return ConversationHandler.END

    try:
        for ingredient in ingredients:
            # Create a more user-friendly message with emojis
            message = (
                f"📌 *Ingredient Information*\n\n"
                f"🧪 *Name:* {ingredient['strIngredient']}\n"
                f"📋 *Type:* {ingredient.get('strType', 'N/A')}\n"
                f"🍺 *Alcoholic:* {ingredient.get('strAlcohol', 'N/A')}\n"
                f"🔵 *ABV:* {ingredient.get('strABV', 'N/A')}\n\n"
                f"📝 *Description:*\n{ingredient.get('strDescription', 'No description available.')}"
            )
            await update.message.reply_text(message, parse_mode='Markdown')

    except Exception as e:
        logger.error(f"Error in search_by_ingredient: {e}")
        await update.message.reply_text("❌ Something went wrong. Please try again!")

    menu_msg = get_menu_message()
    await update.message.reply_text(**menu_msg)
    return ConversationHandler.END

# Add new handlers
async def start_drinks_by_ingredient(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start drinks by ingredient search conversation."""
    keyboard = [[InlineKeyboardButton("❌ Cancel Search", callback_data="cancel_search")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.answer()
        message = update.callback_query.message
    else:
        message = update.message

    await message.reply_text(
        "🍶 Please enter an ingredient to find drinks (e.g., Gin, Vodka, Rum):",
        reply_markup=reply_markup
    )
    return TYPING_DRINK_BY_INGREDIENT

async def search_drinks_by_ingredient_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the drinks by ingredient search query."""
    query = update.message.text.strip()
    if not query:
        await update.message.reply_text("Please enter an ingredient name to search.")
        return TYPING_DRINK_BY_INGREDIENT

    await update.message.reply_text(f"🔍 Searching for drinks with ingredient '{query}'...")
    drinks = search_drinks_by_ingredient(query)
    
    if not drinks:
        menu_msg = get_menu_message()
        await update.message.reply_text(
            f"❌ No drinks found with ingredient '{query}'. Please try another ingredient (e.g., Gin, Vodka, Rum, Tequila)",
            reply_markup=menu_msg['reply_markup']
        )
        return ConversationHandler.END

    try:
        total_drinks = len(drinks)
        await update.message.reply_text(
            f"🎯 Found {total_drinks} drink(s) containing '{query}'"
        )

        # Send drinks in smaller batches to avoid rate limits
        batch_size = 5
        current_drink = 0

        for i in range(0, total_drinks, batch_size):
            batch = drinks[i:i + batch_size]
            for drink in batch:
                current_drink += 1
                try:
                    message = (
                        f"🍸 *{drink['strDrink']}*\n"
                        f"Drink {current_drink} of {total_drinks} with {query}"
                    )
                    await update.message.reply_photo(
                        photo=drink['strDrinkThumb'],
                        caption=message,
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    logger.error(f"Error sending photo for drink {drink['strDrink']}: {e}")
                    await update.message.reply_text(message, parse_mode='Markdown')
            
            # Add a small delay between batches to avoid rate limits
            if i + batch_size < total_drinks:
                await asyncio.sleep(0.5)

        # Send completion message
        await update.message.reply_text(
            f"✅ Successfully displayed all {total_drinks} drinks containing '{query}'"
        )

    except Exception as e:
        logger.error(f"Error in search_drinks_by_ingredient: {e}")
        await update.message.reply_text("❌ Something went wrong. Please try again!")
        return ConversationHandler.END

    menu_msg = get_menu_message()
    await update.message.reply_text(**menu_msg)
    return ConversationHandler.END

async def help_command(update, context, from_callback=False):
    """Send help message and show menu."""
    help_text = (
        "*🍸 Welcome to Cocktail Bot - Your Personal Mixologist*\n\n"
        "*Command Reference:*\n"
        "• `/start` - Launch the main menu\n"
        "• `/help` - Display this help guide\n"
        "• `/random` - Get a random cocktail recipe\n"
        "• `/about` - View information about the bot and developer\n\n"
        "*Available Features:*\n"
        "1️⃣ *Random Cocktail Discovery*\n"
        "   • Get random cocktail suggestions\n"
        "   • Complete with recipes and images\n"
        "   • Perfect for trying something new\n\n"
        "2️⃣ *Search Capabilities*\n"
        "   • Search by cocktail name\n"
        "   • Browse by first letter\n"
        "   • Find drinks by ingredient\n"
        "   • Explore ingredient information\n\n"
        "3️⃣ *Detailed Information*\n"
        "   • Full ingredient lists\n"
        "   • Step-by-step instructions\n"
        "   • High-quality drink images\n"
        "   • Ingredient details and properties\n\n"
        "*Pro Tips:*\n"
        "📌 *For Best Results:*\n"
        "   • Use exact ingredient names (e.g., 'Gin', 'Vodka')\n"
        "   • Try alternative spellings if no results\n"
        "   • Use the ingredient search for detailed info\n\n"
        "📌 *Navigation:*\n"
        "   • Use menu buttons for easy access\n"
        "   • Cancel searches anytime with ❌\n"
        "   • Return to menu with /start\n\n"
        "*Need More Help?*\n"
        "Use the About section to contact the developer for support or suggestions."
    )
    
    menu_msg = get_menu_message()
    
    if from_callback:
        await update.callback_query.message.edit_text(
            text=help_text,
            reply_markup=menu_msg['reply_markup'],
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(help_text, parse_mode='Markdown')
        await update.message.reply_text(**menu_msg)

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE, from_callback=False):
    """Send information about the bot and developer."""
    about_text = (
        "*🍸 About Cocktail Bot*\n\n"
        "This bot helps you discover and learn about various cocktails and their ingredients. "
        "Whether you're a professional bartender or just looking to make something special at home, "
        "this bot provides easy access to a vast database of cocktail recipes and ingredient information.\n\n"
        "*Features:*\n"
        "• Comprehensive cocktail database\n"
        "• Multiple search options\n"
        "• Detailed ingredient information\n"
        "• High-quality cocktail images\n"
        "• Easy-to-follow recipes\n\n"
        "*👨‍💻 Developer Information*\n"
        "Created by Ali Shahriari\n\n"
        "*Find me on:*\n"
        "• Twitter: @alishahriarioff\n"
        "• Instagram: @alishahriarioff\n"
        "• LinkedIn: @alishahriarioff\n"
        "• GitHub: @alishahriarioff\n\n"
        "Feel free to reach out for feedback or suggestions!"
    )

    menu_msg = get_menu_message()
    
    if from_callback:
        await update.callback_query.message.edit_text(
            text=about_text,
            reply_markup=menu_msg['reply_markup'],
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(about_text, parse_mode='Markdown')
        await update.message.reply_text(**menu_msg)

# Update handle_button to include about command
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button presses from inline keyboard."""
    query = update.callback_query
    await query.answer()

    if query.data == 'random_drink':
        await random_drink(update, context, from_callback=True)
    elif query.data == 'search_drink':
        return await start_search(update, context)
    elif query.data == 'letter_search':
        return await start_letter_search(update, context)
    elif query.data == 'drinks_by_ingredient':
        return await start_drinks_by_ingredient(update, context)
    elif query.data == 'ingredient_search':
        return await start_ingredient_search(update, context)
    elif query.data == 'cancel_search':
        return await cancel_search(update, context)
    elif query.data == 'help':
        await help_command(update, context, from_callback=True)
    elif query.data == 'about':
        await about_command(update, context, from_callback=True)