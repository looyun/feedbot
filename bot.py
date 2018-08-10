#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import sqlite3
import traceback
from datetime import time
from functools import partial

import requests
from emoji import emojize
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      InlineQueryResultArticle, InputTextMessageContent,
                      KeyboardButton, ReplyKeyboardMarkup)
from telegram.ext import (CallbackQueryHandler, CommandHandler, Filters,
                          InlineQueryHandler, MessageHandler, Updater)
from telegraph import Telegraph

try:
    from bs4 import BeautifulSoup
except ImportError:
    from BeautifulSoup import BeautifulSoup


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

telegraph = Telegraph()
telegraph.create_account(
    short_name='feedall', author_name='feedall', author_url='https://t.me/Gofeedbot')

updater = Updater(token='533092604:AAGjcs5aOhjIvqM7-SJEuho2_64FsKhPXu0')
dispatcher = updater.dispatcher

HOST = '149.28.144.135'
DOMAIN = ''
PORT = 4000
SCHEMA = 'http://'
URL = SCHEMA + (DOMAIN or HOST) + ':' + str(PORT)


def get_auth_headers(token):
    return {"Authorization": token}


def get_instant_view_links(items):
    links = list()
    for item in items:
        id = item.get('_id')
        link = get_link(id)
        if link:
            links.append(link)
            continue

        html_content = item.get('content') or item.get('description')
        try:
            soup = BeautifulSoup(html_content)
            h2s = soup.find_all('h2')
            for h2 in h2s:
                h2.name = 'h3'
            spans = soup.find_all('span')
            for span in spans:
                span.unwrap()
            divs = soup.find_all('div')
            for div in divs:
                div.unwrap()
            response = telegraph.create_page(
                item.get('title'),
                author_name=item.get('feed')[0].get('title'),
                html_content=unicode(soup),
                author_url=item.get('link')
            )
            link = u'http://telegra.ph/{}'.format(response['path'])
            links.append(link)
            add_link(id, link)
        except Exception:
            traceback.print_exc()
            print item
            continue
    return links


def get_new_items(bot, job):
    user_id = job.context.get('user_id')
    token = get_token(user_id)
    headers = get_auth_headers(token)
    request_url = URL + '/api/my/items'

    r = requests.get(request_url + '?page=1&per_page=10', headers=headers)

    if r.status_code == 200:
        items = r.json()
        links = get_instant_view_links(items)
        if len(links) == 0:
            text = emojize("no data:slightly_frowning_face:", use_aliases=True)
        else:
            text = emojize('\n'.join(links) + "\n:ok_hand:", use_aliases=True)
    else:
        text = emojize("failed:slightly_frowning_face:", use_aliases=True)

    bot.send_message(chat_id=job.context.get('chat_id'), text=text)


def start(bot, update, job_queue):

    bot.send_message(
        chat_id=update.message.chat_id,
        text=emojize(
            "Welcome! You will get 10 items every day. Try /my manage your feeds. :stuck_out_tongue_closed_eyes:",
            use_aliases=True)
    )
    context = {'chat_id': update.message.chat_id,
               'user_id': update.message.from_user.id}
    t = time(9, 10, 0)
    job_queue.run_daily(get_new_items, t, context=context)
    # job_queue.run_repeating(get_new_items, interval=300,
    #                         first=0, context=context)


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
        'Your choice:', reply_markup=ReplyKeyboardMarkup(reply_keyboard))


def echo(bot, update):
    msg = update.message.text
    user_id = update.message.from_user.id
    token = get_token(user_id)
    headers = get_auth_headers(token)

    if msg == 'feeds':
        request_url = URL + '/api/my/feeds'
        r = requests.get(request_url, headers=headers)

        if r.status_code == 200:
            items = r.json()
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

    r = requests.get(request_url + '?page=1&per_page=10', headers=headers)

    if r.status_code == 200:
        items = r.json()
        links = get_instant_view_links(items)
        if len(links) == 0:
            text = emojize("no data:slightly_frowning_face:", use_aliases=True)
        else:
            text = emojize('\n'.join(links) + "\n:ok_hand:", use_aliases=True)
    else:
        text = emojize("failed:slightly_frowning_face:", use_aliases=True)

    reply_markup = get_page_reply_markup(1)

    update.message.reply_text(text, reply_markup=reply_markup)


def help(bot, update):
    update.message.reply_text("Use /start to test this bot.")


def add_token(bot, update, args):
    if not args:
        return
    token = args[0]
    user_id = update.message.from_user.id

    # Insert a row of data
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO user VALUES (?,?)", (user_id, token))
    conn.commit()

    text = emojize(":ok_hand:", use_aliases=True)
    bot.send_message(chat_id=update.message.chat_id, text=text)


def get_token(id):
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute("select token from user where id=?", (id, ))
    result = c.fetchone()
    return result[0] if result else None


def add_link(id, link):
    # Insert a row of data
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO item VALUES (?,?)", (id, link))
    conn.commit()


def get_link(id):
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute("select link from item where id=?", (id, ))
    result = c.fetchone()
    return result[0] if result else None


def subscribe(bot, update, args):
    feedurl = args[0]
    user_id = update.message.from_user.id
    token = get_token(user_id)
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
    links = get_instant_view_links(items)
    bot.send_message(chat_id=update.message.chat_id, text='\n'.join(links))


def export(bot, uodate):
    pass


def import_feeds(bot, uodate):
    pass


def callback(bot, update):
    query = update.callback_query

    print(query.data)
    if query.data == 'current_page':
        return
    page = int(query.data)
    if page < 1:
        return

    user_id = update.callback_query.from_user.id
    token = get_token(user_id)
    headers = get_auth_headers(token)
    request_url = URL + '/api/my/items' + '?page=%s&per_page=10' % page
    r = requests.get(request_url, headers=headers)

    if r.status_code == 200:
        items = r.json()
        links = get_instant_view_links(items)
        if len(links) == 0:
            text = emojize("no data:slightly_frowning_face:", use_aliases=True)
        else:
            text = emojize('\n'.join(links) + "\n:ok_hand:", use_aliases=True)
    else:
        text = emojize("failed:slightly_frowning_face:", use_aliases=True)

    reply_markup = get_page_reply_markup(page)
    bot.edit_message_text(
        text=text,
        chat_id=query.message.chat_id,
        message_id=query.message.message_id, reply_markup=reply_markup)
    print('finished')
    return


def get_page_reply_markup(page):

    keyboard = [[
        InlineKeyboardButton("Last page", callback_data=page - 1),
        InlineKeyboardButton("Page %s" % page, callback_data='current_page'),
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
    # Create table
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute(
        '''CREATE TABLE if not exists user (id INTEGER PRIMARY KEY, token text)''')
    c.execute(
        '''CREATE TABLE if not exists item (id text PRIMARY KEY, link text)''')
    conn.commit()
    conn.close()

    dispatcher.add_handler(CommandHandler('start', start, pass_job_queue=True))
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
