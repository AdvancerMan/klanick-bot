import logging
import time

import gspread
from oauth2client.service_account import ServiceAccountCredentials


def create_memoized_get(update_message, update, update_time):
    last_update = None
    answer = None

    def memoized_get(*args, **kwargs):
        nonlocal last_update, answer

        now = time.time()
        since_last_update = now - last_update \
            if last_update is not None else update_time

        if since_last_update >= update_time:
            logging.info(update_message)
            last_update = now
            answer = update(*args, **kwargs)
        return answer

    return memoized_get


def initialize_sheets_service():
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        'credentials.json',
        ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive',
         'https://spreadsheets.google.com/feeds'])

    return gspread.authorize(credentials)


get_answers = create_memoized_get(
    "Updating answers from google spreadsheet",
    lambda gsheets_service, spreadsheet_id:
    gsheets_service.open_by_key(spreadsheet_id).sheet1.col_values(1),
    30
)

get_todd_etot_sticker_set = create_memoized_get(
    "Updating sticker set",
    lambda bot: bot.getStickerSet("ToddEtot"),
    60
)
