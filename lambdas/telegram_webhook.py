import json
import os
import psycopg2
import requests
from db_client import db_connection_string
from intro_flow import greet, show_report_example, show_custom_categories_example, show_cash_no_cash_message, show_developer_contact


def add_field(id, key, value):

    """
    Update a specific field in the transactions table for a given record (identified by time).

    :param id: ID of the record (time value)
    :param key: Column name to be updated
    :param value: New value for the column
    :param connection_string: Database connection string
    """

    # Connect to the SQL database
    conn = psycopg2.connect(db_connection_string())
    cursor = conn.cursor()

    # SQL query to update the specific field for the given record
    query = f"""
        UPDATE transactions
        SET {key} = %s
        WHERE time = %s;
    """

    cursor.execute(query, (value, id))

    # Commit changes
    conn.commit()

    # Close connections
    cursor.close()
    conn.close()

def save_category(id, category):
    add_field(id, 'category', category)



def delete_message(chat_id, message_id):

    url = f"https://api.telegram.org/bot{os.environ.get('TG_BOT_API_KEY')}/deleteMessage"

    payload = json.dumps({
        "chat_id": chat_id,
        "message_id": message_id
    })
    headers = {
        'Content-Type': 'application/json'
    }

    requests.request("POST", url, headers=headers, data=payload)


def handle_set_category(chat_id, request):
    data_parts = request['callback_query']['data'].split(':')
    id = data_parts[1]
    category = data_parts[2]
    message_id = request['callback_query']['message']['message_id']

    if id != '0':
        save_category(id, category)

    delete_message(chat_id, message_id)


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
            handle_set_category(chat_id, request)
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
    else:
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
