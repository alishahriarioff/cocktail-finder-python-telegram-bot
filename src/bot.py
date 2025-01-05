import asyncio
from telegram.ext import (ApplicationBuilder, CommandHandler, CallbackQueryHandler,
                         ConversationHandler, MessageHandler, filters)
from telegram.constants import ParseMode
import logging
import sys
from config.settings import BOT_TOKEN
from handlers.commands import (
    start, help_command, random_drink, handle_button, 
    start_search, search_drink, cancel_search,
    start_letter_search, search_by_letter,
    start_ingredient_search, search_by_ingredient,
    start_drinks_by_ingredient, search_drinks_by_ingredient_handler,
    about_command,  # Add this import
    TYPING_SEARCH, TYPING_LETTER, TYPING_INGREDIENT, TYPING_DRINK_BY_INGREDIENT
)

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def run_app():
    """Run the bot application"""
    if not BOT_TOKEN:
        logger.error("No bot token provided!")
        sys.exit(1)

    # Create application with more generous timeout settings
    application = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .connect_timeout(30.0)  # Increase connection timeout
        .read_timeout(30.0)     # Increase read timeout
        .write_timeout(30.0)    # Increase write timeout
        .pool_timeout(30.0)     # Increase pool timeout
        .build()
    )

    # Important: Register conversation handlers FIRST
    search_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_search, pattern='^search_drink$'),
            CommandHandler("search", start_search)
        ],
        states={
            TYPING_SEARCH: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, search_drink),
                CallbackQueryHandler(cancel_search, pattern='^cancel_search$')
            ]
        },
        fallbacks=[CommandHandler('start', start)],
        name='search_conversation'
    )

    letter_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_letter_search, pattern='^letter_search$'),
            CommandHandler("letter", start_letter_search)
        ],
        states={
            TYPING_LETTER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, search_by_letter),
                CallbackQueryHandler(cancel_search, pattern='^cancel_search$')
            ]
        },
        fallbacks=[CommandHandler('start', start)],
        name='letter_search_conversation'
    )

    # Add new conversation handler for ingredient search
    ingredient_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_ingredient_search, pattern='^ingredient_search$'),
            CommandHandler("ingredient", start_ingredient_search)
        ],
        states={
            TYPING_INGREDIENT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, search_by_ingredient),
                CallbackQueryHandler(cancel_search, pattern='^cancel_search$')
            ]
        },
        fallbacks=[CommandHandler('start', start)],
        name='ingredient_search_conversation'
    )

    # Add new conversation handler for drinks by ingredient search
    drinks_by_ingredient_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_drinks_by_ingredient, pattern='^drinks_by_ingredient$'),
            CommandHandler("drinks_by_ingredient", start_drinks_by_ingredient)
        ],
        states={
            TYPING_DRINK_BY_INGREDIENT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, search_drinks_by_ingredient_handler),
                CallbackQueryHandler(cancel_search, pattern='^cancel_search$')
            ]
        },
        fallbacks=[CommandHandler('start', start)],
        name='drinks_by_ingredient_conversation'
    )

    # Register handlers in specific order
    application.add_handler(search_conv_handler)
    application.add_handler(letter_conv_handler)
    application.add_handler(ingredient_conv_handler)  # Add the new handler
    application.add_handler(drinks_by_ingredient_conv_handler)  # Add the new handler
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("random", random_drink))
    application.add_handler(CommandHandler("about", about_command))  # Add this line
    # General callback handler must be last
    application.add_handler(CallbackQueryHandler(handle_button))

    try:
        # Start the bot with error handling
        logger.info("Starting bot...")
        application.run_polling(
            allowed_updates=["message", "callback_query"]
        )
    except Exception as e:
        logger.error(f"Error running bot: {e}")
        sys.exit(1)

if __name__ == '__main__':
    try:
        run_app()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        sys.exit(0)