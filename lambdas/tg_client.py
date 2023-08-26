import json
import requests
import os


def send_tg_message(chat_id, message):
    url = f"https://api.telegram.org/bot{os.environ.get('TG_BOT_API_KEY')}/sendMessage"

    payload = json.dumps({
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    })
    headers = {
        'Content-Type': 'application/json'
    }

    requests.request("POST", url, headers=headers, data=payload)


def send_tg_message_with_inline_keyboard(chat_id, message, inline_keyboard):
    url = f"https://api.telegram.org/bot{os.environ.get('TG_BOT_API_KEY')}/sendMessage"

    payload = json.dumps({
        "chat_id": chat_id,
        "text": message,
        "reply_markup": {
            "inline_keyboard": inline_keyboard
        },
        "parse_mode": "Markdown"
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code != 200:
        print(response.text)
