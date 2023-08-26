import os
import json
from datetime import datetime

import time
from tg_client import send_tg_message
from db_client import get_transactions_in_range, get_smallest_time



def get_sums_per_category(from_seconds, to_seconds):
    transactions = get_transactions_in_range(from_seconds, to_seconds)

    sums_per_category = {}

    for transaction in transactions:
        if 'category' not in transaction:
            continue

        category = transaction['category']

        if category == 'ignore' or category == '':
            continue

        if category not in sums_per_category:
            sums_per_category[category] = 0

        sums_per_category[category] += transaction['amount']

    # Compute the total sum
    total_sum = sum(sums_per_category.values())
    sums_per_category['total'] = total_sum

    return sums_per_category


def all_in_one_report_message_tabular(first_statistics, second_statistics, comparison_name):

    first_statistics = {k: -(v / 100) for k, v in first_statistics.items()}
    second_statistics = {k: -(v / 100) for k, v in second_statistics.items()}

    with open('categories.json', 'r', encoding='utf-8') as file:
        categories = json.load(file)

    total_budget = sum(item['budget'] for item in categories)
    categories.append({"category": "total", "emoji": "💰", "translation": "Загалом", "budget": total_budget})

    emoji_per_category = {item['category']: item['emoji'] for item in categories}
    budget_per_category = {item['category']: item['budget'] for item in categories}

    header = "```\n"
    header += f"{comparison_name:>30}"

    result_strings = [header]

    category_keys = [item['category'] for item in categories]
    for category in category_keys:
        translated_category = emoji_per_category.get(category, category)

        benchmark_value = budget_per_category.get(category, 0)
        first_value = first_statistics.get(category, 0)
        second_value = second_statistics.get(category, 0)

        first_emoji = get_emoji_for_value(first_value, benchmark_value)
        second_emoji = get_emoji_for_value(second_value, benchmark_value)

        first_emoji_and_value = f"{first_emoji} {int(first_value)}"
        second_emoji_and_value = f"{second_emoji} {int(second_value)}"
        result_strings.append(f"{translated_category}: {first_emoji_and_value:<7}| {second_emoji_and_value:<7}| {int(benchmark_value):<7}")

    result_strings.append("------------------------------")
    first_dollars = f"${int(first_statistics['total']/36.65)}"
    second_dollars = f"${int(second_statistics['total']/36.65)}"
    budget_dollars = f"${int(budget_per_category.get('total', 0)/36.65)}"
    result_strings.append(f"💵: {first_dollars:>8}| {second_dollars:>8}| {budget_dollars:>5}")

    result_strings.append("```")

    return '\n'.join(result_strings)


def get_emoji_for_value(value, benchmark_value):
    difference = value - benchmark_value
    if benchmark_value != 0:
        percentage_difference = (difference / abs(benchmark_value)) * 100
    else:
        percentage_difference = 0 if difference == 0 else 100

    # Choose an emoji based on the percentage difference
    percent_color_differentiator = 3
    if percentage_difference > percent_color_differentiator:
        emoji = "🔴"
    elif percentage_difference <= 0:
        emoji = "🟢"
    else:
        emoji = "🔘"

    return emoji


def full_months_difference(d1, d2):
    """Return the difference in full months between two dates."""
    # If d1 is after d2, swap the dates
    if d1 > d2:
        d1, d2 = d2, d1

    months = (d2.year - d1.year) * 12 + d2.month - d1.month
    # If the day of the month of the earlier date is after the day of the later date
    # subtract one month from the difference
    if d1.day > d2.day:
        months -= 1

    return months

def all_in_one_report_lambda_handler(event, context):
    to_seconds = int(time.time())
    month_in_seconds = 24 * 60 * 60 * 31
    from_seconds = to_seconds - month_in_seconds

    current_month_statistics = get_sums_per_category(from_seconds, to_seconds)

    first_transaction_seconds = get_smallest_time()
    first_transaction_date = datetime.fromtimestamp(first_transaction_seconds)
    current_date = datetime.now()
    full_months = full_months_difference(first_transaction_date, current_date)
    full_months = min(full_months, 12)

    from_seconds = to_seconds - full_months * month_in_seconds
    average_month_statistics = get_sums_per_category(from_seconds, to_seconds)
    average_month_statistics = {k: v / full_months for k, v in average_month_statistics.items()}

    report_string = all_in_one_report_message_tabular(current_month_statistics, average_month_statistics, "останній  середній бюджет")
    my_chat_id = os.environ.get('MY_CHAT_ID')
    send_tg_message(my_chat_id, report_string)

    return {
            'statusCode': 200,
            'body': 'Hello from Lambda!'
        }
