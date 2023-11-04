import time
import json
from datetime import datetime
import pytz
from tg_client import send_tg_message_with_inline_keyboard
import os
from db_client import set_field, get_transactions_in_range_with_condition

def mark_trasaction_ask_asked(transaction, message_id):
    set_field(transaction['time'], 'category_last_asked_seconds', int(time.time()))
    if not transaction.get('message_ids'):
        message_ids = str(message_id)
    else:
        message_ids = transaction['message_ids'] + f",{message_id}"

    set_field(transaction['time'], 'message_ids', message_ids)


def to_kyiv_pretty_time(transaction):
    dt_object = datetime.fromtimestamp(transaction['time'])
    kyiv = pytz.timezone('Europe/Kiev')
    dt_kyiv = dt_object.replace(tzinfo=pytz.UTC).astimezone(kyiv)
    return dt_kyiv.strftime("%Y-%m-%d %H:%M:%S")


def get_mcc_ukr(mcc):
    with open('json/mcc.json', 'r') as file:
        data = json.load(file)

    # Check if the mcc key exists in the JSON data
    if mcc in data:
        return data[mcc]["uk"]
    else:
        return "Невідомо"


def ask_category(transaction):

    with open('json/categories.json', 'r', encoding='utf-8') as file:
        categories = json.load(file)

    categories.append({'category': 'ignore', 'emoji': '🚫', 'translation': 'Ignore'})

    all_category_buttons = [
        {
            "text": f"{cat['emoji']} {cat['translation']}",
            "callback_data": f"setCategory:{transaction['time']}:{cat['category']}"
        }
        for cat in categories
    ]

    final_category_buttons = [all_category_buttons[i:i + 3] for i in range(0, len(all_category_buttons), 3)]

    pretty_time = to_kyiv_pretty_time(transaction)
    description = ''
    if 'description' in transaction:
        description = remove_markedown_symbols(transaction['description'])

    message = f"{pretty_time}                             Яка це категорія? ({get_mcc_ukr(transaction['mcc'])}) \n{description} {transaction['amount'] / 100} грн"

    my_chat_id = os.environ.get('MY_CHAT_ID')
    return send_tg_message_with_inline_keyboard(my_chat_id, message, final_category_buttons)


def remove_markedown_symbols(string):
    for symbol in ['*', '_', '~~', '`', '[', ']', '#', '>', '|']:
        string = string.replace(symbol, '')
    return string


def ask_categories_last_28_days():
    now_in_seconds = int(time.time())
    seconds_in_1_days = 24 * 60 * 60 * 1
    seconds_in_28_days = seconds_in_1_days * 28

    time_28_days_ago = now_in_seconds - seconds_in_28_days

    transactions = get_transactions_in_range_with_condition("category is null or category = ''", time_28_days_ago, now_in_seconds)


    for transaction in transactions:
        ask_category_if_needed(transaction)


def ask_category_if_needed(transaction):
    if is_non_empty_category(transaction):
        return

    current_time = int(time.time())
    one_day_seconds = 24 * 60 * 60

    if 'category_last_asked_seconds' not in transaction \
            or (current_time - transaction['category_last_asked_seconds']) > one_day_seconds:
        print("Asking category for transaction ", transaction)
        message_id = ask_category(transaction)
        mark_trasaction_ask_asked(transaction, message_id)


def is_non_empty_category(transaction):
    return 'category' in transaction and transaction['category'] is not None and transaction['category'] != ''

def lambda_handler(event, context):
    ask_categories_last_28_days()
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }