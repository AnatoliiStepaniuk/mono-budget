import json
import os
from db_client import set_field, get_transaction
from intro_flow import greet, show_report_example, show_custom_categories_example, show_cash_no_cash_message, show_developer_contact
from auto_set_categories import delete_all_messages, delete_message

def save_category(id, category):
    set_field(id, 'category', category)


def handle_set_category(request):
    data_parts = request['callback_query']['data'].split(':')
    id = data_parts[1]
    category = data_parts[2]

    if id != '0':
        save_category(id, category)

    transaction = get_transaction(id)
    if not transaction.get('message_ids'):
        message_id = request['callback_query']['message']['message_id']
        my_chat_id = os.environ.get('MY_CHAT_ID')
        delete_message(my_chat_id, message_id)
    else:
        delete_all_messages(transaction)


def lambda_handler(event, context):
    print("event:", event)
    request = json.loads(event['body'])
    print("request:", request)

    if request.get('message', {}).get('text') == '/start':
        chat_id = request['message']['from']['id']
        print(f"[{chat_id}] Flow: greeting ")
        greet(chat_id)
        return {
            'statusCode': 200,
            'body': 'Hello from Lambda!'
        }

    if 'callback_query' in request and 'data' in request['callback_query']:
        chat_id = request['callback_query']['from']['id']
        if request['callback_query']['data'].startswith("setCategory"):
            print(f"[{chat_id}] Flow: setCategory ")
            handle_set_category(request)
        if request['callback_query']['data'] == "show_report_example":
            print(f"[{chat_id}] Flow: show_report_example ")
            show_report_example(chat_id)
        if request['callback_query']['data'] == "show_custom_categories_example":
            print(f"[{chat_id}] Flow: show_custom_categories_example ")
            show_custom_categories_example(chat_id)
        if request['callback_query']['data'] == "show_cash_no_cash_message":
            print(f"[{chat_id}] Flow: show_cash_no_cash_message ")
            show_cash_no_cash_message(chat_id)
        if request['callback_query']['data'] == "show_developer_contact":
            print(f"[{chat_id}] Flow: show_developer_contact ")
            show_developer_contact(chat_id)
    elif 'message' in request:
        chat_id = request['message']['from']['id']
        print(f"[{chat_id}] Flow: greeting ")
        greet(chat_id)
        return {
            'statusCode': 200,
            'body': 'Hello from Lambda!'
        }


    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }
