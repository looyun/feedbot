from telegram.ext import Updater
from telegram.ext import CommandHandler, MessageHandler, Filters, InlineQueryHandler,CallbackQueryHandler
from telegram import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardButton, KeyboardButton, InlineKeyboardMarkup,ReplyKeyboardMarkup
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

updater = Updater(token='533092604:AAHByyEuPVgWApg6z5oRNzIJMiQvxtuGMY8')
dispatcher = updater.dispatcher

HOT = range(5)

def start(bot, update):
    bot.send_message(
        chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")


def list(bot, update):
    reply_keyboard = [['ithome'], ['freebuf'], ['blog']]

    update.message.reply_text(
        'Please pick a feed',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard))


def button(bot, update):
    query = update.callback_query

    bot.edit_message_text(
        text="Selected option: {}".format(query.data),
        chat_id=query.message.chat_id,
        message_id=query.message.message_id)


def help(bot, update):
    update.message.reply_text("Use /start to test this bot.")


def chose(bot, update):
    keyboard = [[
        InlineKeyboardButton("Option 1", callback_data='1'),
        InlineKeyboardButton("Option 2", callback_data='2')
    ], [InlineKeyboardButton("Option 3", callback_data='3')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Please choose:', reply_markup=reply_markup)


def echo(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=update.message.text)


def caps(bot, update, args):
    text_caps = ' '.join(args).upper()
    bot.send_message(chat_id=update.message.chat_id, text=text_caps)


def inline_caps(bot, update):
    query = update.inline_query.query
    if not query:
        return
    result = list()
    result.append(
        InlineQueryResultArticle(
            id=query.upper(),
            title='caps',
            input_message_content=InputTextMessageContent(query.upper())))
    bot.answer_inline_query(update.inline_query.id, result)


updater.dispatcher.add_handler(CallbackQueryHandler(button))
updater.dispatcher.add_handler(CommandHandler('help', help))
updater.dispatcher.add_handler(CommandHandler('chose', chose))
updater.dispatcher.add_handler(CommandHandler('list', list))
start_handler = CommandHandler('start', start)
echo_handler = MessageHandler(Filters.text, echo)
caps_handler = CommandHandler('caps', caps, pass_args=True)
inline_query_handler = InlineQueryHandler(inline_caps)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(echo_handler)
dispatcher.add_handler(caps_handler)
dispatcher.add_handler(inline_query_handler)
updater.start_polling()