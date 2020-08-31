import logging
import time

import telegram.ext.dispatcher

import gspread
from oauth2client.service_account import ServiceAccountCredentials


def memoized(load_period, log_name=None):
    def wrapper(load_resource):
        nonlocal log_name

        if log_name is None:
            log_name = "resource from function %s" % load_resource.__name__

        load_resource_async = telegram.ext.dispatcher.run_async(load_resource)
        last_load = None
        resource = None
        promise = None

        def wait_resouce():
            nonlocal resource, promise
            resource = promise.result()
            logging.info("Loaded %s" % log_name)
            promise = None

        def memoized_load(*args, **kwargs):
            nonlocal last_load, resource, promise

            if promise is not None and promise.done.is_set():
                wait_resouce()

            now = time.time()
            since_last_load = now - last_load \
                if last_load is not None else load_period

            if promise is None and since_last_load >= load_period:
                logging.info("Loading %s" % log_name)
                last_load = now
                promise = load_resource_async(*args, **kwargs)

            if resource is None:
                wait_resouce()

            return resource

        return memoized_load

    return wrapper


def initialize_sheets_service():
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        'credentials.json',
        ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive',
         'https://spreadsheets.google.com/feeds'])

    return gspread.authorize(credentials)


@memoized(30, "answers from google spreadsheet")
def load_answers(gsheets_service, spreadsheet_id):
    return gsheets_service.open_by_key(spreadsheet_id).sheet1.col_values(1)


def create_sticker_set_loader(name):
    @memoized(60, "%s sticker set" % name)
    def load_sticker_set(bot):
        return bot.getStickerSet(name)

    return load_sticker_set


load_todd_etot_sticker_set = create_sticker_set_loader("ToddEtot")
