#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater
from telegram.ext import CommandHandler, MessageHandler, Filters, InlineQueryHandler, CallbackQueryHandler
from telegram import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardButton, \
    KeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

from functools import partial
from emoji import emojize
import logging
import json
import requests
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

updater = Updater(token='533092604:AAGjcs5aOhjIvqM7-SJEuho2_64FsKhPXu0')
dispatcher = updater.dispatcher

HOST = '127.0.0.1'
DOMAIN = ''
PORT = 4000
SCHEMA = 'http://'
URL = SCHEMA + (DOMAIN or HOST) + ':' + str(PORT)

user_token_dict = dict()


def get_auth_headers(token):
    return {"Authorization": token}


def start(bot, update):

    bot.send_message(
        chat_id=update.message.chat_id,
        text=emojize(
            "Welcome! Try /list to get feed. :stuck_out_tongue_closed_eyes:",
            use_aliases=True))


def status(bot, update):
    bot.send_message(
        chat_id=update.message.chat_id,
        text=emojize(
            "Feeds %d, unread items %d, star items %d. :stuck_out_tongue_closed_eyes:" % (
                10, 50, 5),
            use_aliases=True))


def my(bot, update):
    user_id = update.message.from_user.id
    token = user_token_dict.get(user_id)
    reply_keyboard = [['feeds'], ['items'], ['stars'], ['status']]
    update.message.reply_text(
        'Your feed:', reply_markup=ReplyKeyboardMarkup(reply_keyboard))


def echo(bot, update):
    msg = update.message.text
    user_id = update.message.from_user.id
    token = user_token_dict.get(user_id)
    headers = get_auth_headers(token)

    if msg == 'feeds':
        request_url = URL + '/api/my/feeds'
        r = requests.get(request_url, headers=headers)

        if r.status_code == 200:
            items = json.loads(r)
            names = list()
            for item in items:
                name = item.get('title')
                names.append(name)
            text = emojize('\n'.join(names) + "\n:ok_hand:", use_aliases=True)
        else:
            text = emojize("failed:slightly_frowning_face:", use_aliases=True)
        bot.send_message(chat_id=update.message.chat_id, text=text)
        return
    elif msg == 'items':
        request_url = URL + '/api/my/items'
    elif msg == 'stars':
        request_url = URL + '/api/my/stars'
    elif msg == 'status':
        bot.send_message(
            chat_id=update.message.chat_id,
            text=emojize(
                "Feeds %d, unread items %d, star items %d. :stuck_out_tongue_closed_eyes:" % (
                    10, 50, 5),
                use_aliases=True))
        return

    r = requests.get(request_url, headers=headers)

    if r.status_code == 200:
        items = json.loads(r)
        links = list()
        for item in items:
            link = URL + '/item/' + item.get('link')
            links.append(link)
            text = emojize('\n'.join(links) + "\n:ok_hand:", use_aliases=True)
    else:
        text = emojize("failed:slightly_frowning_face:", use_aliases=True)
    bot.send_message(chat_id=update.message.chat_id, text=text)


def help(bot, update):
    update.message.reply_text("Use /start to test this bot.")


def add_token(bot, update, args):
    token = args[0]
    user_id = update.message.from_user.id
    user_token_dict[user_id] = token
    text = emojize(":ok_hand:", use_aliases=True)
    bot.send_message(chat_id=update.message.chat_id, text=text)


def subscribe(bot, update, args):
    feedurl = args[0]
    user_id = update.message.from_user.id
    token = user_token_dict.get(user_id)
    payload = {"feedurl": feedurl}
    request_url = URL + '/api/my/subscribe'
    headers = get_auth_headers(token)
    r = requests.post(request_url, data=payload, headers=headers)
    if r.status_code == 200:
        text = emojize(":ok_hand:", use_aliases=True)
    else:
        text = emojize("failed:slightly_frowning_face:", use_aliases=True)
    bot.send_message(chat_id=update.message.chat_id, text=text)


def hot(bot, update):
    r = requests.get(URL + '/api/items/hot/5')
    items = json.loads(r)
    links = list()
    for item in items:
        link = URL + '/items/path'
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

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', help))
    dispatcher.add_handler(CommandHandler('status', status))
    dispatcher.add_handler(CommandHandler('my', my))
    # dispatcher.add_handler(CommandHandler('hot', hot))
    dispatcher.add_handler(MessageHandler(Filters.text, echo))
    dispatcher.add_handler(CommandHandler(
        "add_token", add_token, pass_args=True))
    dispatcher.add_handler(CommandHandler(
        "subscribe", subscribe, pass_args=True))
    # dispatcher.add_handler(CallbackQueryHandler(button))
    # dispatcher.add_handler(CommandHandler('chose', chose))
    # dispatcher.add_handler(CommandHandler('caps', caps, pass_args=True))
    # dispatcher.add_handler(InlineQueryHandler(inline_caps))

    updater.start_polling()
    updater.idle()
