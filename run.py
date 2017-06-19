# -*- coding: utf-8 -*-

import codecs
import json
import logging
import urllib
import urllib.parse
import urllib.request


from telegram.ext import CommandHandler
from telegram.ext import Updater


logging.basicConfig(filename='panpis.log', level=logging.DEBUG)
TELEGRAM_TOKEN = open('.telegram_token').readline()[:-1]
KNOWLEDGE_API_TOKEN = open('.gcloud_api_token').readline()[:-1]
KNOWLEDGE_API_URL = 'https://kgsearch.googleapis.com/v1/entities:search'

START_COMMAND = "start"
LMK_COMMAND = "lmk"

logging.info('PanpisBot starting...')


def start(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id,
                    text="Type '/lmk <something>' to use this bot.")


def let_me_know(bot, update):
    query = update.message.text[len(LMK_COMMAND)+2:]

    params = {
        'query': query,
        'limit': 5,
        'key': KNOWLEDGE_API_TOKEN,
        'languages': 'en'
    }

    url = KNOWLEDGE_API_URL + '?' + urllib.parse.urlencode(params)
    reader = codecs.getreader("utf-8")
    obj = json.load(reader(urllib.request.urlopen(url)))
    items = obj.get("itemListElement", None)
    # logging.debug(obj)
    final_score = 0
    final_item = None

    # search items for an exact name match
    for item in items:
        result = item.get("result", None)
        if result is not None:
            name = result.get("name", None)
            score = item.get('resultScore', None)
            if name is not None and name.lower() == query.lower():
                final_score = score
                final_item = item
                break

    # if no exact name match is found, get the item with the highest score
    if final_item is None:
        for item in items:
            score = item.get('resultScore', None)
            if score is not None and (score > final_score):
                final_score = score
                final_item = item

    response = "not found " + query
    if final_item is not None:
        result = final_item.get("result", None)
        if result is not None:
            detailedDescription = result.get("detailedDescription", None)
            if detailedDescription is None:
                # try description
                description = result.get("description", None)
                if description is not None:
                    response = description
            else:
                response = detailedDescription.get("articleBody", None)

    logging.info('%s: %s', query, response)
    bot.sendMessage(chat_id=update.message.chat_id, text=response)


def lambda_handler(event, context):
    updater = Updater(token=TELEGRAM_TOKEN)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler(START_COMMAND, start)
    lmk_handler = CommandHandler(LMK_COMMAND, let_me_know)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(lmk_handler)

    logging.info('PanpisBot ready to go!')

    updater.start_polling()


if __name__ == '__main__':
    event = {

    }
    lambda_handler(event, None)
