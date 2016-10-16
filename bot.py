from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, Job, CallbackQueryHandler
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

logger = logging.getLogger(__name__)
timers = dict()


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    keyboard = [[InlineKeyboardButton("Give me a question!", callback_data = 'Ya')],
                [InlineKeyboardButton("Maybe later", callback_data='Nay')]]
    rep = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Welcome to the WillYouPressTheButton.com bot!', reply_markup=rep)

def button(bot, update):
    query = update.callback_query
    if query.data == 'Ya':
        bot.editMessageText(text="An error occurred while trying to load a question.\nError code: -1 (this feature does not exist yet!)\nTry again later or contact @BnK970 or @Lunatic_Yeti for help.",
                        chat_id=query.message.chat_id,
                        message_id=query.message.message_id)
    elif query.data == "Nay":
        bot.editMessageText(text="Okay! Keep in mind that you can always send me /start to get a question!",
                        chat_id=query.message.chat_id,
                        message_id=query.message.message_id)
    else: #impossible...
        bot.editMessageText(text="Hell! something went wrong!! Please forward this message to @BnK970 or @Lunatic_Yeti\n\n%s" % query,
                        chat_id=query.message.chat_id,
                        message_id=query.message.message_id)

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    updater = Updater("240151502:AAE5R-gOhNZ9TOHyxvb7b-dCECpmjAltW4M")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    dp.add_handler(CommandHandler("help", start))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Block until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()