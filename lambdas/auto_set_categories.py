import time
import json
import os
from db_client import set_field, get_transactions_in_range_with_condition
from tg_client import delete_message

def populate_category(transaction):

    print(f"Assigning category to transaction {transaction}")

    # mcc-based rules
    with open('mcc.json', 'r', encoding='utf-8') as file:
        mcc_translations = json.load(file)
    with open('json/mcc_translation_to_category.json', 'r', encoding='utf-8') as file:
        translation_to_category = json.load(file)
    translation = mcc_translations.get(str(transaction['mcc']), {}).get('uk')
    if translation:
        transaction['category'] = translation_to_category.get(translation)

    # description based rules
    with open('json/description_to_category.json', 'r', encoding='utf-8') as file:
        description_to_category = json.load(file)
    transaction["category"] = description_to_category.get(transaction["description"], transaction.get("category"))

    if 'category' in transaction:
        print(f"Set category {transaction['category']} found for {transaction}")
    else:
        print(f"Could not define category automatically for {transaction}")

def set_categories_last_28_days():
    now_in_seconds = int(time.time())
    seconds_in_1_days = 24 * 60 * 60 * 1
    seconds_in_28_days = seconds_in_1_days * 28

    time_28_days_ago = now_in_seconds - seconds_in_28_days

    transactions = get_transactions_in_range_with_condition("category is null or category = ''", time_28_days_ago, now_in_seconds)
    for transaction in transactions:
        auto_set_category_if_needed(transaction)


def auto_set_category_if_needed(transaction):
    if non_empty_category(transaction):
        return

    current_time_in_seconds = int(time.time())
    # too early. give user time to specify the transaction manually
    if current_time_in_seconds - int(transaction['time']) < 2*3600:
        return

    populate_category(transaction)

    if non_empty_category(transaction):
        set_field(transaction['time'], 'category', transaction['category'])
        delete_all_messages(transaction)



def non_empty_category(transaction):
    return 'category' in transaction and transaction['category'] is not None and transaction['category'] != ''

def delete_all_messages(transaction):
    message_ids = []
    if 'message_ids' in transaction and transaction['message_ids']:
        message_ids = [int(i) for i in transaction['message_ids'].split(",")]
    my_chat_id = os.environ.get('MY_CHAT_ID')
    for message_id in message_ids:
        delete_message(my_chat_id, message_id)
    set_field(transaction['time'], 'message_ids', '')


def lambda_handler(event, context):
    set_categories_last_28_days()
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }