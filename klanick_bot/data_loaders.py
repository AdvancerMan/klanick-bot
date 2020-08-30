import logging
import time

import gspread
from oauth2client.service_account import ServiceAccountCredentials


def memoized(load_period, load_log_message=None):
    def wrapper(load_resource):
        nonlocal load_log_message

        last_load = None
        resource = None
        if load_log_message is None:
            load_log_message = f"Invoking memoized function %s" \
                               % load_resource.__name__

        def memoized_load(*args, **kwargs):
            nonlocal last_load, resource

            now = time.time()
            since_last_load = now - last_load \
                if last_load is not None else load_period

            if since_last_load >= load_period:
                logging.info(load_log_message)
                last_load = now
                resource = load_resource(*args, **kwargs)
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


@memoized(30, "Loading answers from google spreadsheet")
def load_answers(gsheets_service, spreadsheet_id):
    return gsheets_service.open_by_key(spreadsheet_id).sheet1.col_values(1)


def create_sticker_set_loader(name):
    @memoized(60, "Loading %s sticker set" % name)
    def load_sticker_set(bot):
        return bot.getStickerSet(name)
    return load_sticker_set


load_todd_etot_sticker_set = create_sticker_set_loader("ToddEtot")
