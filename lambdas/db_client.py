import os
import psycopg2


def db_connection_string():
    dbname = os.environ.get('DB_NAME')
    user = os.environ.get('DB_USER')
    password = os.environ.get('DB_PASSWORD')
    host = os.environ.get('DB_HOST')
    port = os.environ.get('DB_PORT')
    return f"dbname={dbname} user={user} password={password} host={host} port={port}"


def get_transactions_in_range(from_seconds, to_seconds):
    return get_transactions_in_range_with_condition('1 = 1', from_seconds, to_seconds)


def get_transactions_in_range_with_condition(condition, from_seconds, to_seconds):

    """
    Fetch transactions from the SQL database within a specified time range.

    :param condition: additional sql condition (d.g. category is null)
    :param from_seconds: Starting time (inclusive)
    :param to_seconds: Ending time (inclusive)
    :return: List of transactions
    """

    # Connect to the SQL database
    conn = psycopg2.connect(db_connection_string())
    cursor = conn.cursor()

    query = f"""
        SELECT time, mcc, description, amount, category, message_ids, category_last_asked_seconds, comment 
        FROM transactions
        WHERE {condition} AND time BETWEEN %s AND %s;
    """

    cursor.execute(query, (from_seconds, to_seconds))
    records = cursor.fetchall()

    transactions = []
    for record in records:
        transaction = {
            'time': record[0],
            'mcc': record[1],
            'description': record[2],
            'amount': record[3],
            'category': record[4],
            'message_ids': record[5]
        }

        if record[6] is not None:
            transaction['category_last_asked_seconds'] = record[6]

        if record[7] is not None:
            transaction['comment'] = record[7]

        transactions.append(transaction)

    # Close connections
    cursor.close()
    conn.close()

    return transactions

def get_transaction(time):

    """
    Fetch transactions from the SQL database within a specified time range.

    :param time: timestamp of transaction in seconds (transaction identifier)
    :return: Transaction found for the timestamp
    """

    # Connect to the SQL database
    conn = psycopg2.connect(db_connection_string())
    cursor = conn.cursor()

    query = """
        SELECT time, mcc, description, amount, category, message_ids, category_last_asked_seconds, comment 
        FROM transactions
        WHERE time = %s
    """

    cursor.execute(query, (time,))
    record = cursor.fetchone()

    # If no record is found, return None
    if not record:
        return None

    transaction = {
        'time': record[0],
        'mcc': record[1],
        'description': record[2],
        'amount': record[3],
        'category': record[4],
        'message_ids': record[5]
    }

    if record[6] is not None:
        transaction['category_last_asked_seconds'] = record[6]

    if record[7] is not None:
        transaction['comment'] = record[7]

    # Close connections
    cursor.close()
    conn.close()

    return transaction


def set_field(id, key, value):

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


def get_smallest_time():
    """
    Fetch the smallest time value from the transactions table in the SQL database.

    :return: The smallest time value or None if the table is empty
    """

    # Connect to the SQL database
    conn = psycopg2.connect(db_connection_string())
    cursor = conn.cursor()

    query = """
        SELECT MIN(time) 
        FROM transactions;
    """

    cursor.execute(query)
    result = cursor.fetchone()  # fetchone() returns a tuple with a single value

    # Close connections
    cursor.close()
    conn.close()

    # Check if result contains a value, if yes return the value, otherwise return None
    if result and result[0]:
        return result[0]
    else:
        return None