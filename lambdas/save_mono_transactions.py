import os
import psycopg2
import requests as requests
from datetime import datetime, timedelta
import calendar
import json
from ask_categories import ask_category_if_needed
from db_client import db_connection_string

def get_mono_transactions(from_secs, to_secs):
    headers = {
        'X-Token': os.environ.get('MONO_API_KEY')
    }
    account = os.environ.get('MONO_ACCOUNT_ID')
    response = requests.get(f"https://api.monobank.ua/personal/statement/{account}/{from_secs}/{to_secs}", headers=headers)
    if 200 <= response.status_code < 300:
        return response.json()
    else:
        raise Exception(f"Failed to get transactions from monobank: {response.text}")


def save_transactions(transactions):

    """
    Save transactions to the SQL database.

    :param transactions: List of transaction dictionaries
    :param connection_string: Database connection string
    """

    # Connect to the SQL database
    conn = psycopg2.connect(db_connection_string())
    cursor = conn.cursor()

    for transaction in transactions:
        # Check if the transaction already exists in the database
        query_check = """
            SELECT EXISTS(
                SELECT 1
                FROM transactions
                WHERE time = %s
            );
        """
        cursor.execute(query_check, (transaction['time'],))
        exists = cursor.fetchone()[0]

        # If the transaction doesn't exist, insert it
        if not exists:
            query_insert = """
                INSERT INTO transactions (time, mcc, description, amount, category, category_last_asked_seconds, comment)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
            """
            cursor.execute(query_insert, (
                transaction['time'],
                transaction['mcc'],
                transaction['description'],
                transaction['amount'],
                transaction.get('category', None),
                transaction.get('category_last_asked_seconds', None),
                transaction.get('comment', None)
            ))

    # Commit changes
    conn.commit()

    # Close connections
    cursor.close()
    conn.close()


def save_previous_transactions_handler(event, context):
    end = datetime.utcnow()  # Current timestamp
    start = end - timedelta(days=30)

    start_in_seconds = calendar.timegm(start.utctimetuple())
    end_in_seconds = calendar.timegm(end.utctimetuple())

    transactions = get_mono_transactions(start_in_seconds, end_in_seconds)
    save_transactions(transactions)

    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }


def save_current_transaction_handler(event, context):
    print(event)
    if event['body'] is not None:
        body = json.loads(event['body'])
        if body is not None and body.get("type") == "StatementItem":
            if body['data']['account'] == os.environ.get('MONO_ACCOUNT_ID'):
                transaction = {
                    'time': body['data']['statementItem']['time'],
                    'mcc': body['data']['statementItem']['mcc'],
                    'description': body['data']['statementItem']['description'],
                    'amount': body['data']['statementItem']['amount']
                }

                save_transactions([transaction])
                ask_category_if_needed(transaction)
        else:
            print("The body does not have type == StatementItem")
    else:
        print("The request had not body")

    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }
