from tg_client import send_tg_message, send_tg_message_with_inline_keyboard

def greet(chat_id):
    greeting = "Привіт!\nЯ допоможу тобі слідкувати за твоїм бюджетом 💵\n" \
               "Кожного дня я буду відправляти тобі звіти, щоб ти бачив чи все йде за планом 📈\n" \
               "Так ти завжди зможеш вчасно відреагувати!\n" \
               "Постав свій бюджет на автопілот 🚀"

    inline_keyboard = [[{
        "text": "Показати приклад звіту",
        "callback_data": "show_report_example"
    }]]

    send_tg_message_with_inline_keyboard(chat_id, greeting, inline_keyboard)



def show_report_example(chat_id):
    report_example = """
```
     останній  середній бюджет
🏠: 🟢 11561| 🟢 11445| 12000
🍗: 🟢 4840 | 🔴 5315 | 5000
💪: 🔴 1080 | 🟢 914  | 1000
🚕: 🟢 473  | 🟢 457  | 500
📚: 🟢 525  | 🔴 685  | 600
🍺: 🔴 1590 | 🟢 1410 | 1500
🛶: 🟢 1275 | 🔴 1685 | 1500
👕: 🔴 1100 | 🟢 905  | 1000
🤔: 🟢 910  | 🔴 1050 | 1000
👨‍👩‍👦: 🟢 890  | 🟢 920  | 1000
🚴: 🟢 545  | 🔴 640  | 600
👧: 🟢 1110 | 🔴 1295 | 1200
🙏: 🟢 2900 | 🔴 3150 | 3000
------------------------------
💰: 🔴 30250| 🟢 29010| 29900
------------------------------
💵:    $825 |    $791 | $815
```
        """

    send_tg_message(chat_id, report_example)

    inline_keyboard = [[{
        "text": "Як визначаються категорії?",
        "callback_data": "show_custom_categories_example"
    }]]
    send_tg_message_with_inline_keyboard(chat_id, "Як бачиш, я показую і останній, і середній місяць (за останній рік).\n"
                                                  "Категорії - довільні, ти зможеш створити ті, що тобі до вподоби", inline_keyboard)


def show_custom_categories_example(chat_id):
    custom_category_intro = "У більшості випадків я зможу сам визначити правильну категорію.\nТи зможеш налаштувати гнучкі правила для цього.\n" \
                            "Якщо мені буде потрібна допомога, я спитаю тебе таким чином:"

    send_tg_message(chat_id, custom_category_intro)
    send_tg_message_with_inline_keyboard(chat_id, "Яка це категорія? 20 серпня 2023 - Переказ 200 грн на картку ХХХХ", example_of_ask_category_message_inline_keyboard())

    inline_keyboard = [[{
        "text": "А якщо я плачу готівкою?",
        "callback_data": "show_cash_no_cash_message"
    }]]
    send_tg_message_with_inline_keyboard(chat_id, "Ок, зрозуміло.", inline_keyboard)


def show_cash_no_cash_message(chat_id):
    cash_no_cash_message = "Я підтримую як готівкові, так і безготівкові витрати - можу автоматично підтягувати з твого Mono/Privatbank або ти можеш вносити їх вручну."
    inline_keyboard = [[{
        "text": "Хочу спробувати!",
        "callback_data": "show_developer_contact"
    }]]

    send_tg_message_with_inline_keyboard(chat_id, cash_no_cash_message, inline_keyboard)

def show_developer_contact(chat_id):
    contact_message = "Бот ще в розробці. Якщо хочеш спробувати - звернись до @run\_forrest\_88"
    send_tg_message(chat_id, contact_message)


def example_of_ask_category_message_inline_keyboard():
    translation_dict = {
        'living': '🏠 Проживання',
        'food': '🍗 Харчування',
        'health': '💪 Здоровʼя',
        'transport': '🚕 Транспорт',
        'growth': '📚 Розвиток',
        'relax': '🍺 Відпочинок',
        'travel': '🛶 Мандрівки',
        'look': '👕 Одяг/Вигляд',
        'other': '🤔 Інше',
        'parents': '👨‍👩‍👦 Родина',
        'hobby': '🚴 Хоббі',
        'dog': '🐶 Пес',
        'donate': '🙏 Благодійність',
        'ignore': '🚫 Не рахувати'
    }

    all_category_buttons = [
        {
            "text": text,
            "callback_data": f"setCategory:0:ignore"
        }
        for category, text in translation_dict.items()
    ]

    final_category_buttons = [all_category_buttons[i:i + 3] for i in range(0, len(all_category_buttons), 3)]
    return final_category_buttons