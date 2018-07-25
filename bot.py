#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater
from telegram.ext import CommandHandler, MessageHandler, Filters, InlineQueryHandler, CallbackQueryHandler
from telegram import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardButton, \
    KeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

from emoji import emojize
import logging
import json
import requests
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

updater = Updater(token='533092604:AAGjcs5aOhjIvqM7-SJEuho2_64FsKhPXu0')
dispatcher = updater.dispatcher

IP = '127.0.0.1'
DOMAIN = ''
PORT = 4000

HOST = (DOMAIN or IP) + ':' + str(PORT)

user_token_dict = dict()


def request_with_token(token, url):
    headers = {"Authorization": token}
    return request.get(url, headers=headers)


def start(bot, update):

    bot.send_message(
        chat_id=update.message.chat_id,
        text=emojize(
            "Welcome! Try /list to get feed. :stuck_out_tongue_closed_eyes:",
            use_aliases=True))


def status(bot, update):
    pass


def list_feeds(bot, update):
    reply_keyboard = list()
    r = requests.get(HOST + '/api/feeds/')
    feeds = json.loads(r)
    if len(feeds) <= 0:
        return
    for feed in feeds:
        reply_keyboard.append([feed.title])

    # reply_keyboard = [['hot'], ['new'], ['random'], ['my']]

    update.message.reply_text(
        'Please pick a feed', reply_markup=ReplyKeyboardMarkup(reply_keyboard))


def help(bot, update):
    update.message.reply_text("Use /start to test this bot.")


def add_token(bot, update, args):
    token = args[0]
    user_id = update.message.from_user.id
    user_name = update.message.from_user.full_name
    user_token_dict[user_name] = token
    text = emojize(":ok_hand:", use_aliases=True)
    bot.send_message(chat_id=update.message.chat_id, text=text)


def hot(bot, update):
    r = requests.get(HOST + '/api/items/hot/5')
    items = json.loads(r)
    links = list()
    for item in items:
        link = HOST + '/items/path'
        links.append(link)
    bot.send_message(chat_id=update.message.chat_id, text='\n'.join(links))


def export(bot, uodate):
    pass


def import_feeds(bot, uodate):
    pass


def button(bot, update):
    query = update.callback_query

    bot.edit_message_text(
        text="Selected option: {}".format(query.data),
        chat_id=query.message.chat_id,
        message_id=query.message.message_id)


def chose(bot, update):
    keyboard = [[
        InlineKeyboardButton("Option 1", callback_data='1'),
        InlineKeyboardButton("Option 2", callback_data='2')
    ], [InlineKeyboardButton("Option 3", callback_data='3')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Please choose:', reply_markup=reply_markup)


def caps(bot, update, args):
    text_caps = ' '.join(args).upper()
    bot.send_message(chat_id=update.message.chat_id, text=text_caps)


def inline_caps(bot, update):
    query = update.inline_query.query
    if not query:
        return
    results = list()
    results.append(
        InlineQueryResultArticle(
            id=query.upper(),
            title='caps',
            input_message_content=InputTextMessageContent(query.upper())))
    bot.answer_inline_query(update.inline_query.id, results)


if __name__ == "__main__":
    start_handler = CommandHandler('start', start)
    add_token_handler = CommandHandler("add_token", add_token, pass_args=True)
    # caps_handler = CommandHandler('caps', caps, pass_args=True)
    # inline_query_handler = InlineQueryHandler(inline_caps)

    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(CommandHandler('help', help))
    dispatcher.add_handler(CommandHandler('list', list_feeds))
    dispatcher.add_handler(CommandHandler('hot', hot))
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(add_token_handler)
    # dispatcher.add_handler(CommandHandler('chose', chose))
    # dispatcher.add_handler(caps_handler)
    # dispatcher.add_handler(inline_query_handler)

    updater.start_polling()
    updater.idle()
