#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging
import os

import telegram
import telegram.ext

import klanick_bot.data_loaders
import klanick_bot.handlers


def bot_command(command_handler, comand_name):
    def wrapper(update: telegram.Update, context: telegram.ext.CallbackContext):
        logging.info("Handling /%s command" % comand_name)
        command_handler(update, context)

    return wrapper


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


def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

    logging.info("Starting bot")

    logging.info("Initializing gsheets_service...")
    gsheets_service = klanick_bot.data_loaders.initialize_sheets_service()

    with open("spreadsheet_id.txt") as f:
        spreadsheet_id = f.read()

    logging.info("Initializing bot...")
    with open("bot_token.txt") as f:
        updater = telegram.ext.Updater(f.read(), use_context=True)

    dp: telegram.ext.Dispatcher = updater.dispatcher
    dp.bot_data["gsheets_service"] = gsheets_service
    dp.bot_data["spreadsheet_id"] = spreadsheet_id

    commandHandlers = [
        ("help", help_command),
        ("klan", klanick_bot.handlers.klan_message_handler),
        ("random", klanick_bot.handlers.random_message_handler),
        ("sticker", klanick_bot.handlers.random_sticker_handler)
    ]

    for command, callback in commandHandlers:
        dp.add_handler(telegram.ext.CommandHandler(
            command, bot_command(callback, command)))

    dp.add_handler(telegram.ext.MessageHandler(
        telegram.ext.Filters.update.edited_message,
        klanick_bot.handlers.edited_message_handler))

    dp.add_handler(telegram.ext.MessageHandler(
        telegram.ext.Filters.all & ~telegram.ext.Filters.command
        & ~telegram.ext.Filters.update.edited_message,
        klanick_bot.handlers.klan_message_handler))

    updater.start_polling()

    logging.info("Initializing done!")
    updater.idle()


if __name__ == '__main__':
    main()
