import asyncio
from telegram.ext import (ApplicationBuilder, CommandHandler, CallbackQueryHandler,
                         ConversationHandler, MessageHandler, filters)
from telegram.constants import ParseMode
import logging
import sys
from config.settings import BOT_TOKEN
from handlers.commands import (start, help_command, random_drink, handle_button, 
                             TYPING_SEARCH, start_search, search_drink, cancel_search)

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def run_app():
    """Run the bot application"""
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

    # Important: Register conversation handler FIRST
    conv_handler = ConversationHandler(
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
        fallbacks=[
            CommandHandler('start', start)
        ],
        per_chat=True,
        name='search_conversation'
    )

    # Register handlers in specific order
    application.add_handler(conv_handler)  # Must be first
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    # General callback handler must be last
    application.add_handler(CallbackQueryHandler(handle_button))

    try:
        # Start the bot with error handling
        logger.info("Starting bot...")
        application.run_polling(
            stop_signals=None,
            drop_pending_updates=True,  # Ignore any pending updates
            allowed_updates=["message", "callback_query"]  # Specify which updates to handle
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