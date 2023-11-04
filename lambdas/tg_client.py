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

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        return data["result"]["message_id"]
    else:
        raise Exception(f'Unsuccessful response from TG: {response.text}')


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
    if response.status_code == 200:
        data = response.json()
        return data["result"]["message_id"]
    else:
        raise Exception(f'Unsuccessful response from TG: {response.text}')


def delete_message(chat_id, message_id):

    url = f"https://api.telegram.org/bot{os.environ.get('TG_BOT_API_KEY')}/deleteMessage"

    payload = json.dumps({
        "chat_id": chat_id,
        "message_id": message_id
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    if not (200 <= response.status_code < 300):
        print(f"Failed to delete message. Status: {response.status_code}. Response: {response.text}")
        if "Bad Request: message can't be deleted for everyone" in response.text:
            send_tg_message(chat_id, "Message is too old to be deleted by bot. Please delete it manually.")



