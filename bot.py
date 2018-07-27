#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
from functools import partial

import requests
from emoji import emojize
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      InlineQueryResultArticle, InputTextMessageContent,
                      KeyboardButton, ReplyKeyboardMarkup)
from telegram.ext import (CallbackQueryHandler, CommandHandler, Filters,
                          InlineQueryHandler, MessageHandler, Updater)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

updater = Updater(token='533092604:AAGjcs5aOhjIvqM7-SJEuho2_64FsKhPXu0')
dispatcher = updater.dispatcher

HOST = '149.28.144.135'
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
            items = r.json()
            names = list()
            for item in items:
                name = item.get('Title')
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

    r = requests.get(request_url + '?page=1&per_page=10', headers=headers)

    if r.status_code == 200:
        items = r.json()
        links = list()
        for item in items:
            link = URL + '/api/item/' + str(item.get('ID'))
            links.append(link)
            text = emojize('\n'.join(links) + "\n:ok_hand:", use_aliases=True)
    else:
        text = emojize("failed:slightly_frowning_face:", use_aliases=True)

    reply_markup = get_page_reply_markup(1)

    update.message.reply_text(text, reply_markup=reply_markup)


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
    r = requests.get(URL + '/api/items/recommand/5')
    items = r.json()
    links = list()
    for item in items:
        link = URL + '/api/item/' + item.get("Link")
        links.append(link)
    bot.send_message(chat_id=update.message.chat_id, text='\n'.join(links))


def export(bot, uodate):
    pass


def import_feeds(bot, uodate):
    pass


def callback(bot, update):
    query = update.callback_query

    page = int(query.data)
    if page < 1:
        return

    user_id = update.callback_query.from_user.id
    token = user_token_dict.get(user_id)
    headers = get_auth_headers(token)
    request_url = URL + '/api/my/items' + '?page=%s&per_page=10' %page
    r = requests.get(request_url, headers=headers)

    if r.status_code == 200:
        items = r.json()
        links = list()
        print(items[0])
        for item in items:
            link = URL + '/api/item/' + str(item.get('ID'))
            links.append(link)
            text = emojize('\n'.join(links) + "\n:ok_hand:", use_aliases=True)
    else:
        text = emojize("failed:slightly_frowning_face:", use_aliases=True)

    reply_markup = get_page_reply_markup(page)
    bot.edit_message_text(
        text=text,
        chat_id=query.message.chat_id,
        message_id=query.message.message_id, reply_markup=reply_markup)


def get_page_reply_markup(page):

    keyboard = [[
        InlineKeyboardButton("Last page", callback_data=page - 1),
        InlineKeyboardButton("Page %s" % page, callback_data=page),
        InlineKeyboardButton("Next page", callback_data=page + 1)
    ]]

    return InlineKeyboardMarkup(keyboard)


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
    dispatcher.add_handler(CallbackQueryHandler(callback))
    # dispatcher.add_handler(CommandHandler('chose', chose))
    # dispatcher.add_handler(CommandHandler('caps', caps, pass_args=True))
    # dispatcher.add_handler(InlineQueryHandler(inline_caps))

    updater.start_polling()
    updater.idle()
