from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from services.cocktail_service import get_random_cocktail, search_cocktail
import logging

logger = logging.getLogger(__name__)

# Define states
TYPING_SEARCH = range(1)

MENU_ACTIONS = {
    'title': '🍸 Cocktail Menu',
    'options': [
        ('Random Drink 🎲', 'random_drink'),
        ('Search Drink 🔍', 'search_drink'),
        ('Help ❓', 'help')
    ]
}

def create_menu_keyboard():
    """Create inline menu keyboard"""
    keyboard = []
    for option_text, callback_data in MENU_ACTIONS['options']:
        keyboard.append([InlineKeyboardButton(option_text, callback_data=callback_data)])
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

async def random_drink(update, context, from_callback=False):
    """Send a random cocktail."""
    cocktail = get_random_cocktail()
    if cocktail:
        # Create ingredients list
        ingredients = []
        for ing, meas in zip(cocktail['ingredients'], cocktail['measurements']):
            if ing and meas:
                ingredients.append(f"🔸 {meas} {ing}")
            elif ing:
                ingredients.append(f"🔸 {ing}")

        message = f"🎲 *Random Cocktail of the Day!* 🎲\n\n"
        message += f"🍸 *{cocktail['name']}*\n"
        message += f"📑 *Category:* {cocktail['category']}\n\n"
        message += "🧪 *Ingredients:*\n"
        message += "\n".join(ingredients) + "\n\n"
        message += f"📝 *Instructions:*\n{cocktail['instructions']}\n\n"
        message += "Want another drink? Hit Random Drink! 🎲"

        # Add inline menu after sending cocktail
        menu_msg = get_menu_message()
        
        if from_callback:
            # Send new cocktail with menu (removed the delete line)
            sent_message = await update.callback_query.message.reply_photo(
                photo=cocktail['image'],
                caption=message,
                parse_mode='Markdown'
            )
        else:
            sent_message = await update.message.reply_photo(
                photo=cocktail['image'],
                caption=message,
                parse_mode='Markdown'
            )
        # Show menu after cocktail
        await sent_message.reply_text(**menu_msg)
    else:
        error_message = "Sorry, I couldn't find a cocktail right now. Please try again!"
        menu_msg = get_menu_message()
        if from_callback:
            await update.callback_query.message.edit_text(
                text=error_message + "\n\n" + menu_msg['text'],
                reply_markup=menu_msg['reply_markup'],
                parse_mode=menu_msg['parse_mode']
            )
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
    logger.info(f"Searching for cocktail: {query}")
    
    # Send searching message
    await update.message.reply_text("🔍 Searching...")
    
    try:
        cocktails = search_cocktail(query)
        
        if cocktails:
            # Send search summary
            total_found = len(cocktails)
            await update.message.reply_text(
                f"🎯 Found {total_found} cocktail{'s' if total_found > 1 else ''} matching '{query}'"
            )
            
            # Send each cocktail
            for idx, cocktail in enumerate(cocktails, 1):
                ingredients = []
                for ing, meas in zip(cocktail['ingredients'], cocktail['measurements']):
                    if ing and meas:
                        ingredients.append(f"🔸 {meas} {ing}")
                    elif ing:
                        ingredients.append(f"🔸 {ing}")

                message = f"🔍 *Result {idx} of {total_found}*\n\n"
                message += f"🍸 *{cocktail['name']}*\n"
                message += f"📑 *Category:* {cocktail['category']}\n\n"
                message += "🧪 *Ingredients:*\n"
                message += "\n".join(ingredients) + "\n\n"
                message += f"📝 *Instructions:*\n{cocktail['instructions']}\n\n"
                message += "Want to search again? Click Search Drink! 🔍"

                sent_message = await update.message.reply_photo(
                    photo=cocktail['image'],
                    caption=message,
                    parse_mode='Markdown'
                )
                
                # Only show menu after the last result
                if idx == total_found:
                    menu_msg = get_menu_message()
                    await sent_message.reply_text(**menu_msg)
        else:
            menu_msg = get_menu_message()
            await update.message.reply_text(
                f"❌ Sorry, I couldn't find any cocktails named '{query}'.\nPlease try another name:",
                reply_markup=menu_msg['reply_markup']
            )
    except Exception as e:
        logger.error(f"Error in search_drink: {e}", exc_info=True)
        menu_msg = get_menu_message()
        await update.message.reply_text(
            "❌ Sorry, something went wrong with the search. Please try again!",
            reply_markup=menu_msg['reply_markup']
        )
    
    return ConversationHandler.END

async def help_command(update, context, from_callback=False):
    """Send help message and show menu."""
    help_text = "Here are the available commands:\n"
    help_text += "/start - Show the main menu\n"
    help_text += "/help - Show this help message\n\n"
    
    menu_msg = get_menu_message()
    
    if from_callback:
        await update.callback_query.message.edit_text(
            text=help_text + "\n" + menu_msg['text'],
            reply_markup=menu_msg['reply_markup'],
            parse_mode=menu_msg['parse_mode']
        )
    else:
        await update.message.reply_text(help_text)
        await update.message.reply_text(**menu_msg)

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button presses from inline keyboard."""
    query = update.callback_query
    await query.answer()

    if query.data == 'random_drink':
        await random_drink(update, context, from_callback=True)
    elif query.data == 'search_drink':
        return await start_search(update, context)
    elif query.data == 'cancel_search':
        return await cancel_search(update, context)
    elif query.data == 'help':
        await help_command(update, context, from_callback=True)
    # Add other button handlers here