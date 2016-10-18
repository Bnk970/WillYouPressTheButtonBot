from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import Updater, CommandHandler, Job, CallbackQueryHandler
from bs4 import BeautifulSoup
import requests
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

logger = logging.getLogger(__name__)
timers = dict()

def get_q():
    source = requests.get("http://willyoupressthebutton.com").text
    soup = BeautifulSoup(source, "html.parser")
    cond = soup.find(id="cond").text
    res = soup.find(id="res").text
    yes = soup.find(id="yesbtn").get('href')[4:-3]
    no = soup.find(id="nobtn").get('href')
    return [cond, res, yes, no]

def get_stats(answer):
    source = requests.get("http://willyoupressthebutton.com"+answer).text
    soup = BeautifulSoup(source, "html.parser")
    stats = soup.find(id="tytxt").find_all("b")
    full = "*%s* people have pressed this button, while *%s* haven't" % (stats[0].text, stats[1].text)
    return full
# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    keyboard = [[InlineKeyboardButton("Give me a question!", callback_data = 'Ya')],
                [InlineKeyboardButton("Maybe later", callback_data='Nay')]]
    rep = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Welcome to the WillYouPressTheButton.com bot!', reply_markup=rep)

def askme(bot, update):
    q = get_q()
    keyboard = [[InlineKeyboardButton(u"\U0001f534", callback_data = q[2]),
            InlineKeyboardButton("I will not!", callback_data=q[3])]]
    rep = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("%s\n\n*but*\n\n%s" % (q[0], q[1]),
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=rep)

def about(bot, update):
    bot.editMessageText(text="This bot was created by @Bnk970 and @Lunatic_Yeti",
                    chat_id=query.message.chat_id,
                    message_id=query.message.message_id) 

def button(bot, update):
    query = update.callback_query
    if query.data == 'Ya':
        q = get_q()
        keyboard = [[InlineKeyboardButton(u"\U0001f534", callback_data = q[2]),
                InlineKeyboardButton("I will not!", callback_data=q[3])]]
        rep = InlineKeyboardMarkup(keyboard)
        bot.editMessageText(text="%s\n\n*but*\n\n%s" % (q[0], q[1]),
                        chat_id=query.message.chat_id,
                        message_id=query.message.message_id,
                        parse_mode=ParseMode.MARKDOWN,
                        reply_markup=rep)
    elif query.data == "Nay":
        bot.editMessageText(text="M'kay",
                        chat_id=query.message.chat_id,
                        message_id=query.message.message_id)
    elif query.data[-3:] == "yes":
        bot.editMessageText(text=query.message.text+"\n\nYou chose pressing the button.\n"+get_stats(query.data),
                        chat_id=query.message.chat_id,
                        parse_mode=ParseMode.MARKDOWN,
                        message_id=query.message.message_id)
    elif query.data[-2:] == "no":
        bot.editMessageText(text=query.message.text+"\n\n Seems like like you chose not pressing the button \n"+get_stats(query.data),
                        chat_id=query.message.chat_id,
                        parse_mode=ParseMode.MARKDOWN,
                        message_id=query.message.message_id)
    else:
        a = query.data.lower()
        bot.editMessageText(text="Hello \n\n%s," % a,
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
    dp.add_handler(CommandHandler("askme", askme))
    dp.add_handler(CommandHandler("about", about))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    #dp.add_handler(CommandHandler("help", start))

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

