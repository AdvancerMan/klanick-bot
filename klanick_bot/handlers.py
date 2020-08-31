#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging
import random

import telegram
import telegram.ext
import telegram.ext.dispatcher

from klanick_bot.data_loaders import load_answers, load_todd_etot_sticker_set
from klanick_bot.utils import invoke_and_join, trim_indent

logger = logging.getLogger(__name__)


@telegram.ext.dispatcher.run_async
def _async_reply(message, replies):
    for reply in replies:
        log_what_calling = f"{reply[0]}({', '.join(repr(x) for x in reply[1:])})"
        logger.info("Calling %s" % log_what_calling)
        message.__getattribute__(reply[0])(*reply[1:])
        logger.info("Finished calling %s" % log_what_calling)


def make_message_handler(*reply_functions):
    def handle(update: telegram.Update, context: telegram.ext.CallbackContext):
        message = update.effective_message
        if message is None:
            return

        message_text = message.text

        replies = invoke_and_join(reply_functions, update, context,
                                  message_text)
        logger.info(trim_indent(f"""
            Message: {message_text}
            Replies: {replies}
        """.rstrip()))

        _async_reply(message, replies)

    return handle


def random_message_from_gspread(update, context, message):
    return [("reply_text", random.choice(load_answers(
        context.bot_data["gsheets_service"], context.bot_data["spreadsheet_id"]
    )))]


random_message_handler = make_message_handler(random_message_from_gspread)


def random_todd_etot_sticker(update, context, message):
    return [("reply_sticker",
             random.choice(load_todd_etot_sticker_set(context.bot).stickers))]


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
