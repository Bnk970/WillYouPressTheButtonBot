from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Updater, CommandHandler, Job, CallbackQueryHandler, InlineQueryHandler
from bs4 import BeautifulSoup
from uuid import uuid4
from time import gmtime, strftime
import requests
import logging
import re

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

logger = logging.getLogger(__name__)
timers = dict()

# Global variables:
# The format of the questions
q_format = "%s\n\n*but*\n\n%s"

# Helper functions
def store_users(user_id):
    ulist = file_get_contents("counters/users.txt")
    if ulist.find(user_id) == -1:
        with open("counters/users.txt", "a") as myfile:
            myfile.write("\n"+user_id)
def escape_markdown(text):
    """Helper function to escape telegram markup symbols"""
    escape_chars = '\*_`\['
    return re.sub(r'([%s])' % escape_chars, r'\\\1', text)

def file_get_contents(filename):
    with open(filename, "r") as f:
        return f.read()
    
def get_q(q=""):
    uses = str(int(float(file_get_contents("counters/uses.txt")))+1)
    outf = open('counters/uses.txt','w')
    outf.write(uses)
    
    source = requests.get("http://willyoupressthebutton.com"+q).text
    soup = BeautifulSoup(source, "html.parser")
    cond = soup.find(id="cond").text[10:-6]
    res = soup.find(id="res").text[10:-6]
    yes = soup.find(id="yesbtn").get('href')
    no = soup.find(id="nobtn").get('href')
    keyboard = [[InlineKeyboardButton(u"\U0001f534", callback_data = yes),
                InlineKeyboardButton("I will not!", callback_data=no)],
                [InlineKeyboardButton("Share this question!", switch_inline_query=yes[:-4])]]
    rep = InlineKeyboardMarkup(keyboard)
    return [cond, res, rep, yes, no]

def get_stats(bot, answer):
    source = requests.get("http://willyoupressthebutton.com"+answer).text
    soup = BeautifulSoup(source, "html.parser")
    pressed = soup.find(class_="peoplePressed").text
    didntPress = soup.find(class_="peopleDidntpress").text
    full = "*%s* people have pressed this button, while *%s* haven't" % (pressed, didntPress)
    return full
# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    store_users(str(update.message.chat_id))
    if update.message.text=="/start":
        keyboard = [[InlineKeyboardButton("Give me a question!", callback_data = 'Ya')],
                    [InlineKeyboardButton("Maybe later", callback_data='Nay')]]
        rep = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Welcome to the WillYouPressTheButton.com bot!\nUse /help if you don\'t understand how to use the bot.', reply_markup=rep)
    else:
        askme(bot, update, update.message.text[7:])

def askme(bot, update, q_id=""):
    store_users(str(update.message.chat_id))
    q = get_q(q_id)
    bot.sendMessage(update.message.chat_id, q_format % (q[0], q[1]),
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=q[2])

def share(bot, update):
    store_users(str(update.message.chat_id))
    share_url = "https://telegram.me/share/url?url=Do%20you%20know%20the%20game%20WillYouPressTheButton.com?&text=Apperently%20@BnK970%20and%20@Lunatic_yeti%20created%20a%20bot%20for%20this%20game%21%21%0Acheck%20out%20@WillYouPressBot%21"
    update.message.reply_text('Click [here](%s) to share the bot to your friends or [here](http://telegram.me/storebot?start=WillYouPressBot) to rate the bot at @StoreBot' % share_url,
                              parse_mode=ParseMode.MARKDOWN)

def about(bot, update):
    store_users(str(update.message.chat_id))
    update.message.reply_text('This bot was created by @Bnk970 and @Lunatic_Yeti')

def cmd_help(bot, update):
    store_users(str(update.message.chat_id))
    update.message.reply_text('You are presented with a red button. Two things will happen if you press the button - one good and one bad. Will you press the button? It is your choice. Millions of users worldwide!')

def stats(bot, update):
    store_users(str(update.message.chat_id))
    keyboard = [[InlineKeyboardButton("refresh stats", callback_data = "refresh_stats")]]
    rep = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(strftime("%H:%M:%S\n", gmtime())+"The bot was used %s times\n%s Telegram users are using the bot" % (file_get_contents("counters/uses.txt"), sum(1 for line in open('counters/users.txt', "r"))), reply_markup=rep)

def inlinequery (bot, update):
    query = update.inline_query.query
    q = get_q(query)
    results = list()
    if(query==""):
        ttl = "Share a random question"
    else:
        ttl = "Share this question"
    keyboard = [[InlineKeyboardButton("what would you do?", url = 'https://telegram.me/WillYouPressBot?start='+q[4][:-3])]]
    rep = InlineKeyboardMarkup(keyboard)
    results.append(InlineQueryResultArticle(id=uuid4(),
                    title=ttl,
                    input_message_content=InputTextMessageContent(
                                "%s\n\n*%s\n\n*%s" % (escape_markdown(q[0]), escape_markdown("but"), escape_markdown(q[1])),
                                parse_mode=ParseMode.MARKDOWN),
                                reply_markup=rep))
    update.inline_query.answer(results)

def button(bot, update):
    query = update.callback_query
    store_users(str(query.message.chat_id))
    if query.data == 'Ya':
        q = get_q()
        bot.editMessageText(text=q_format % (q[0], q[1]),
                        chat_id=query.message.chat_id,
                        message_id=query.message.message_id,
                        parse_mode=ParseMode.MARKDOWN,
                        reply_markup=q[2])
    elif query.data == "Nay":
        bot.editMessageText(text="M'kay",
                        chat_id=query.message.chat_id,
                        message_id=query.message.message_id)
    elif query.data[-3:] == "yes":
        keyboard = [[InlineKeyboardButton("send me another one!", callback_data = "askme")],
                [InlineKeyboardButton("Share this question!", switch_inline_query=query.data[:-4])]]
        rep = InlineKeyboardMarkup(keyboard)
        bot.editMessageText(text=query.message.text+"\n\nYou chose to press the button.\n"+get_stats(bot, query.data),
                        chat_id=query.message.chat_id,
                        parse_mode=ParseMode.MARKDOWN,
                        message_id=query.message.message_id,
                        reply_markup=rep)
    elif query.data[-2:] == "no":
        keyboard = [[InlineKeyboardButton("Send me another one!", callback_data = "askme")],
                [InlineKeyboardButton("Share this question!", switch_inline_query=query.data[:-3])]]
        rep = InlineKeyboardMarkup(keyboard)
        bot.editMessageText(text=query.message.text+"\n\nYou didn't press the button.\n"+get_stats(bot, query.data),
                        chat_id=query.message.chat_id,
                        parse_mode=ParseMode.MARKDOWN,
                        message_id=query.message.message_id,
                        reply_markup=rep)
    elif query.data == "askme":
        askme(bot, query)
    elif query.data == "refresh_stats":
        keyboard = [[InlineKeyboardButton("refresh stats", callback_data = "refresh_stats")]]
        rep = InlineKeyboardMarkup(keyboard)
        bot.editMessageText(text=strftime(strftime("%H:%M:%S\n", gmtime())+"The bot was used %s times\n%s Telegram users are using the bot" % (file_get_contents("counters/uses.txt"), sum(1 for line in open('counters/users.txt', "r")))),
                        chat_id=query.message.chat_id,
                        message_id=query.message.message_id,
                        reply_markup=rep)
    else:
        bot.editMessageText(text="error: "+query.data,
                        chat_id=query.message.chat_id,
                        message_id=query.message.message_id)

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    updater = Updater(file_get_contents("token.ini"))

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("askme", askme))
    dp.add_handler(CommandHandler("share", share))
    dp.add_handler(CommandHandler("about", about))
    dp.add_handler(CommandHandler("help", cmd_help))
    dp.add_handler(CommandHandler("stats", stats))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))

    # on inline query
    dp.add_handler(InlineQueryHandler(inlinequery))

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
