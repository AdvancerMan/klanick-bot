#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging
import random
import time
import os

import telegram
import telegram.ext

import gspread
from oauth2client.service_account import ServiceAccountCredentials

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)


def bot_command(command_handler, comand_name):
    def wrapper(update: telegram.Update, context: telegram.ext.CallbackContext):
        logger.info("Handling /%s command" % comand_name)
        command_handler(update, context)

    return wrapper


def initialize_sheets_service():
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        'credentials.json',
        ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive',
         'https://spreadsheets.google.com/feeds'])

    return gspread.authorize(credentials)


def create_memoized_get(update_message, update, update_time):
    last_update = None
    answer = None

    def memoized_get(*args):
        nonlocal last_update, answer

        now = time.time()
        since_last_update = now - last_update \
            if last_update is not None else update_time

        if since_last_update >= update_time:
            logging.info(update_message)
            last_update = now
            answer = update(*args)
        return answer

    return memoized_get


get_answers = create_memoized_get(
    "Updating answers from google spreadsheet",
    lambda: gsheets_service.open_by_key(spreadsheet_id).sheet1.col_values(1),
    30
)

get_todd_etot_sticker_set = create_memoized_get(
    "Updating sticker set",
    lambda bot: bot.getStickerSet("ToddEtot"),
    60
)


def invoke_and_join(functions, *args, **kwargs):
    return [result for f in functions for result in f(*args, **kwargs)]


def make_message_handler(*reply_functions):
    def handle(update: telegram.Update, context: telegram.ext.CallbackContext):
        message = update.effective_message
        if message is None:
            return

        message_text = message.text

        logging.info("Message: %s" % message_text)
        replies = invoke_and_join(reply_functions, update, context, message_text)
        logging.info("Replies: %s" % replies)

        for reply in replies:
            message.__getattribute__(reply[0])(*reply[1:])

    return handle


def random_message_from_gspread(*args):
    return [("reply_text", random.choice(get_answers()))]


random_message_handler = make_message_handler(random_message_from_gspread)


def random_todd_etot_sticker(update, context, message):
    return [("reply_sticker",
             random.choice(get_todd_etot_sticker_set(context.bot).stickers))]


random_sticker_handler = make_message_handler(random_todd_etot_sticker)


def random_reply(*reply_functions_and_probas):
    reply_functions = [pair[0] for pair in reply_functions_and_probas]
    probas = [pair[1] for pair in reply_functions_and_probas]
    return make_message_handler(
        lambda update, context, message:
        invoke_and_join(random.choices(reply_functions, probas)[0],
                        update, context, message)
    )


klan_message_handler = random_reply(
    ([random_message_from_gspread], 90),
    ([random_todd_etot_sticker], 5),
    ([random_message_from_gspread, random_todd_etot_sticker], 5),
)

edited_message_handler = make_message_handler(
    lambda *_: [("reply_text", "Я все вииииижууууууу")]
)

gsheets_service: gspread.Client = None
spreadsheet_id = None


def main():
    logging.info("Starting bot")

    logging.info("Initializing gsheets_service...")
    global gsheets_service
    gsheets_service = initialize_sheets_service()

    global spreadsheet_id
    with open("spreadsheet_id.txt") as f:
        spreadsheet_id = f.read()

    logging.info("Initializing bot...")
    with open("bot_token.txt") as f:
        updater = telegram.ext.Updater(f.read(), use_context=True)

    dp: telegram.ext.Dispatcher = updater.dispatcher

    def help_command(update: telegram.Update, context):
        update.message.reply_markdown(os.linesep.join(s.lstrip() for s in f"""
            [Код клана](https://github.com/AdvancerMan/klanick-bot)
            [Гугл таблица](https://docs.google.com/spreadsheets/d/{spreadsheet_id})

            Клан умеет исполнять следующие команды:
            
            /help -- выводит данное описание команд
            /klan msg -- клан отвечает на сообщение msg
            /random -- клан отвечает рандомной фразой из гугл таблиц
            /sticker -- клан отвечает рандомным стикером из стикерпака "Тодд Этот"
        """.splitlines()))

    commandHandlers = [
        ("help", help_command),
        ("klan", klan_message_handler),
        ("random", random_message_handler),
        ("sticker", random_sticker_handler)
    ]

    for command, callback in commandHandlers:
        dp.add_handler(telegram.ext.CommandHandler(
            command, bot_command(callback, command)))

    dp.add_handler(telegram.ext.MessageHandler(
        telegram.ext.Filters.update.edited_message,
        edited_message_handler))

    dp.add_handler(telegram.ext.MessageHandler(
        telegram.ext.Filters.all & ~telegram.ext.Filters.command
        & ~telegram.ext.Filters.update.edited_message,
        klan_message_handler))

    updater.start_polling()

    logging.info("Initializing done!")
    updater.idle()


if __name__ == '__main__':
    main()
