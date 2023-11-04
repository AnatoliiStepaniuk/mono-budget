import json
import os
from tg_client import send_tg_message

import boto3

from datetime import datetime, timedelta
import time


def run_insights_query(log_groups, start_time, end_time, query_string):
    cloudwatch_logs = boto3.client('logs')

    query_ids = []

    # Start queries for all log groups
    for log_group_name in log_groups:
        response = cloudwatch_logs.start_query(
            logGroupName=log_group_name,
            startTime=int(start_time.timestamp() * 1000),
            endTime=int(end_time.timestamp() * 1000),
            queryString=query_string,
        )
        query_ids.append(response['queryId'])

    all_cloudwatch_urls = []

    # Continuously poll for the query results until all queries complete
    for log_group_name, query_id in zip(log_groups, query_ids):
        messages = []

        while True:
            results = cloudwatch_logs.get_query_results(
                queryId=query_id
            )

            if results['status'] == 'Complete':
                for event in results['results']:
                    for item in event:
                        if item['field'] == '@message':
                            messages.append(item['value'])

                if messages:
                    cloudwatch_url = transform_to_cloudwatch_url(log_group_name, start_time, end_time)
                    all_cloudwatch_urls.append(cloudwatch_url)
                break
            elif results['status'] == 'Failed':
                raise Exception(f"Query failed for log group {log_group_name}")

            time.sleep(1)  # Wait for a short time before polling again

    return "\n---\n".join(all_cloudwatch_urls)



def list_log_groups():
    cloudwatch_logs = boto3.client('logs')

    log_groups = []
    next_token = None

    while True:
        # The describe_log_groups call has a limit on how many log groups it can return in a single call,
        # so it uses pagination. We need to handle this pagination to get all log group names.
        if next_token:
            response = cloudwatch_logs.describe_log_groups(nextToken=next_token)
        else:
            response = cloudwatch_logs.describe_log_groups()

        for log_group in response['logGroups']:
            log_group_name = log_group['logGroupName']
            if log_group_name.startswith('/aws/lambda/MonoBudget'):
                log_groups.append(log_group_name)

        next_token = response.get('nextToken')
        if not next_token:
            break

    return log_groups


def transform_to_cloudwatch_url_relative(log_group_name, region='eu-central-1'):# TODO make it exact times, not relative
    base_url = f"https://{region}.console.aws.amazon.com/cloudwatch/home?region={region}#logsV2:log-groups/log-group/"
    encoded_log_group_name = log_group_name.replace("/", "$252F")
    return base_url + encoded_log_group_name + "/log-events$3Fstart$3D-3600000"


def transform_to_cloudwatch_url(log_group_name, start_time, end_time, region='eu-central-1'):
    base_url = f"https://{region}.console.aws.amazon.com/cloudwatch/home?region={region}#logsV2:log-groups/log-group/"
    encoded_log_group_name = log_group_name.replace("/", "$252F")

    # Convert datetime objects to timestamps in milliseconds
    start_timestamp = int(start_time.timestamp() * 1000)
    end_timestamp = int(end_time.timestamp() * 1000)

    return base_url + f"{encoded_log_group_name}/log-events$3Fstart$3D{start_timestamp}$26end$3D{end_timestamp}"


def lambda_handler(event, context):
    log_groups = list_log_groups()
    start = datetime.now() - timedelta(minutes=65)
    end = datetime.now()
    query = """
    fields @timestamp, @message
    | filter @message like /ERROR|Error|error|Fail|fail|FAIL/
    | sort @timestamp desc
    | limit 100
    """

    cw_response = run_insights_query(log_groups, start, end, query)
    if cw_response:
        my_chat_id = os.environ.get('MY_CHAT_ID')
        send_tg_message(my_chat_id, f"Errors:\n---\n{cw_response}")


    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }
