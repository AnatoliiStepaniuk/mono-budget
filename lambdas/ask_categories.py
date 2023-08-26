import time
import json
from datetime import datetime
import pytz
from tg_client import send_tg_message_with_inline_keyboard
import os
from db_client import add_field, get_transactions_in_range


def mark_trasaction_ask_asked(transaction):
    add_field(transaction['time'], 'category_last_asked_seconds', int(time.time()))


def to_kyiv_pretty_time(transaction):
    dt_object = datetime.fromtimestamp(transaction['time'])
    kyiv = pytz.timezone('Europe/Kiev')
    dt_kyiv = dt_object.replace(tzinfo=pytz.UTC).astimezone(kyiv)
    return dt_kyiv.strftime("%Y-%m-%d %H:%M:%S")


def get_mcc_ukr(mcc):
    with open('mcc.json', 'r') as file:
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
    message = f"{pretty_time}                             Яка це категорія? ({get_mcc_ukr(transaction['mcc'])}) \n{transaction['description']} {transaction['amount'] / 100} грн"

    my_chat_id = os.environ.get('MY_CHAT_ID')
    send_tg_message_with_inline_keyboard(my_chat_id, message, final_category_buttons)


def ask_categories_last_28_days():
    now_in_seconds = int(time.time())
    seconds_in_1_days = 24 * 60 * 60 * 1
    seconds_in_28_days = seconds_in_1_days * 28

    time_28_days_ago = now_in_seconds - seconds_in_28_days

    transactions = get_transactions_in_range(time_28_days_ago, now_in_seconds)

    for transaction in transactions:
        ask_category_if_needed(transaction)


def ask_category_if_needed(transaction):
    if 'category' in transaction and transaction['category'] is not None and transaction['category'] != '':
        return

    current_time = int(time.time())
    one_day_seconds = 24 * 60 * 60

    if 'category_last_asked_seconds' not in transaction \
            or (current_time - transaction['category_last_asked_seconds']) > one_day_seconds:
        print("Asking category for transaction ", transaction)
        ask_category(transaction)
        mark_trasaction_ask_asked(transaction)



def lambda_handler(event, context):
    ask_categories_last_28_days()
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }