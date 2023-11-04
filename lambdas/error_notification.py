import json
import os
from tg_client import send_tg_message

import boto3

from datetime import datetime, timedelta


def fetch_cloudwatch_logs(log_group_name):
    cloudwatch_logs = boto3.client('logs')

    # Calculate time range for the last 5 minutes
    end_time = int(datetime.now().timestamp() * 1000)
    start_time = int((datetime.now() - timedelta(minutes=5)).timestamp() * 1000)

    # Start a query
    query = "fields @timestamp, @message | sort @timestamp desc"
    start_query_response = cloudwatch_logs.start_query(
        logGroupName=log_group_name,
        startTime=start_time,
        endTime=end_time,
        queryString=query,
    )

    query_id = start_query_response['queryId']

    # Wait for the query to complete
    response = None
    while response == None or response['status'] == 'Running':
        print('Waiting for query to complete...')
        response = cloudwatch_logs.get_query_results(
            queryId=query_id,
        )

    print(f"response cw for group {log_group_name} : {response['results']}")

    messages = []
    for event in response['results']:
        for item in event:
            if item['field'] == '@message':
                messages.append(item['value'])

    combined_message = "\n".join(messages)
    return combined_message


def lambda_handler(event, context):
    errorJson = event["Records"][0]["Sns"]["Message"]
    err = json.loads(errorJson)
    lambda_name = err['Trigger']['MetricName'].replace("Errors-Function-", "", 1)
    log_group = '/aws/lambda/'+lambda_name

    if err['NewStateValue'] == 'ALARM':
        cw_response = fetch_cloudwatch_logs(log_group)

        if cw_response:
            my_chat_id = os.environ.get('MY_CHAT_ID')
            send_tg_message(my_chat_id, f"Error for lambda {short_function_name(lambda_name)}:\n{cw_response}")


    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }


def short_function_name(lambda_name):
    parts = lambda_name.split('-')
    if len(parts) > 1:
        return parts[1]
    return lambda_name  # return the original name if it doesn't fit the expected pattern
