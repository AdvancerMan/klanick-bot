import logging
import random

import telegram
import telegram.ext

from klanick_bot.data_loaders import get_answers, get_todd_etot_sticker_set
from klanick_bot.utils import invoke_and_join


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


def random_message_from_gspread(update, context, message):
    return [("reply_text", random.choice(get_answers(
        context.bot_data["gsheets_service"], context.bot_data["spreadsheet_id"]
    )))]


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
