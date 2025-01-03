def start(update, context):
    """Send a message when the command /start is issued."""
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hello! I'm your Telegram bot. How can I assist you today?")


def help_command(update, context):
    """Send a message when the command /help is issued."""
    help_text = "Here are the commands you can use:\n"
    help_text += "/start - Start the bot\n"
    help_text += "/help - Get help information"
    context.bot.send_message(chat_id=update.effective_chat.id, text=help_text)


def echo(update, context):
    """Echo the user message."""
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)