from telegram import Update, KeyboardButton
from telegram.ext import CallbackContext, CommandHandler, MessageHandler, Filters, ConversationHandler
import requests

WAITING_LETTER = 3

def start(update: Update, context: CallbackContext):
    keyboard = [
        [KeyboardButton("🔍 Search by name")],
        [KeyboardButton("🎲 Random cocktail")],
        [KeyboardButton("🔤 Search by first letter")]  # New button
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    update.message.reply_text("Welcome! How can I help you?", reply_markup=reply_markup)

def search_by_letter(update: Update, context: CallbackContext):
    update.message.reply_text("Please enter a single letter (A-Z) to search for cocktails:")
    return WAITING_LETTER

def process_letter(update: Update, context: CallbackContext):
    letter = update.message.text.strip().lower()
    if not letter.isalpha() or len(letter) != 1:
        update.message.reply_text("Please enter a single letter (A-Z).")
        return WAITING_LETTER

    response = requests.get(f"https://www.thecocktaildb.com/api/json/v1/1/search.php?f={letter}")
    if response.status_code == 200:
        cocktails = response.json().get('drinks', [])
        if cocktails:
            message = f"Cocktails starting with '{letter.upper()}':\n\n"
            for cocktail in cocktails:
                message += f"🍸 {cocktail['strDrink']}\n"
            update.message.reply_text(message)
        else:
            update.message.reply_text(f"No cocktails found starting with '{letter.upper()}'.")
    else:
        update.message.reply_text("Sorry, couldn't fetch cocktails at the moment. Please try again later.")

    return ConversationHandler.END

def main():
    updater = Updater("YOUR_TOKEN", use_context=True)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    # Add new conversation handler for letter search
    letter_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('^🔤 Search by first letter$'), search_by_letter)],
        states={
            WAITING_LETTER: [MessageHandler(Filters.text & ~Filters.command, process_letter)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    dispatcher.add_handler(letter_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
