import telebot
import json
import sqlite3
from datetime import datetime, timedelta
import re

# Указать ваш токен
TOKEN = '6703350417:AAHJZ0KBCZ2QMtqCXnTjdQmoj3eI0UvbpZ0'


# Инициализируем бота
bot = telebot.TeleBot(TOKEN)

# Переменные для хранения информации пользователя
user_data = {}

# Создаем базу данных SQLite и таблицу для отслеживания запросов пользователей
conn = sqlite3.connect('user_requests.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS user_requests
             (user_id INTEGER PRIMARY KEY, last_request_date TEXT)''')
conn.commit()
conn.close()

def is_valid_name(name):
    # Имя должно состоять только из букв и быть не короче 2 символов
    return bool(re.match(r'^[a-zA-Zа-яА-Я]{2,}$', name))

def is_valid_surname(surname):
    # Фамилия должна состоять только из букв и быть не короче 2 символов
    return bool(re.match(r'^[a-zA-Zа-яА-Я]{2,}$', surname))

def is_valid_phone(phone):
    # Номер телефона должен начинаться с "+7" и состоять из 12 цифр
    return bool(re.match(r'^\+7\d{10}$', phone))

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Здравствуйте! Этот бот поможет вам оставить заявку на обратную связь компании ЭОС. Введите свои данные и мы вам перезвоним по указанному номеру. Давайте начнём!")

    # Проверяем, был ли уже запрос от пользователя в течение последних 24 часов
    if is_user_allowed(message.chat.id):
        bot.send_message(message.chat.id, "Введите ваше имя:")
        bot.register_next_step_handler(message, get_name)
    else:
        bot.send_message(message.chat.id, "Вы уже сделали запрос сегодня. Пожалуйста, попробуйте завтра.")


def get_name(message):
    name = message.text

    if is_valid_name(name):
        user_data['name'] = name
        bot.send_message(message.chat.id, "Отлично! Теперь введите вашу фамилию:")
        bot.register_next_step_handler(message, get_surname)
    else:
        bot.send_message(message.chat.id, "Введите корректное имя (минимум 2 буквы):")
        bot.register_next_step_handler(message, get_name)

def get_surname(message):
    surname = message.text

    if is_valid_surname(surname):
        user_data['surname'] = surname
        bot.send_message(message.chat.id, "Хорошо! Теперь введите ваш номер телефона:")
        bot.register_next_step_handler(message, get_phone)
    else:
        bot.send_message(message.chat.id, "Введите корректную фамилию (минимум 2 буквы):")
        bot.register_next_step_handler(message, get_surname)

def get_phone(message):
    phone = message.text

    if is_valid_phone(phone):
        user_data['phone'] = phone

        # Остальная часть вашей функции без изменений
        user_json = json.dumps(user_data, ensure_ascii=False)
        #Для теста отправляем самому себе, потом заменить message.chat.id на 272511646
        bot.send_message(272511646, f"Пользователь {message.chat.id} отправил следующие данные:\n{user_json}")
        bot.send_message(message.chat.id, "Запрос отправлен! Скоро мы вам перезвоним. Спасибо что обратились к нам.")
        user_data.clear()
        # ...
    else:
        bot.send_message(message.chat.id, "Введите корректный номер телефона (начиная с \"+7\" и содержащий 12 цифр):")
        bot.register_next_step_handler(message, get_phone)

    # Записываем время последнего запроса в базу данных
    conn = sqlite3.connect('user_requests.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO user_requests (user_id, last_request_date) VALUES (?, ?)",
              (message.chat.id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
              )
    conn.commit()
    conn.close()


def is_user_allowed(user_id):
    conn = sqlite3.connect('user_requests.db')
    c = conn.cursor()

    c.execute("SELECT last_request_date FROM user_requests WHERE user_id = ?", (user_id,))
    last_request_date = c.fetchone()

    if last_request_date is None:
        return True

    last_request_date = datetime.strptime(last_request_date[0], "%Y-%m-%d %H:%M:%S")
    current_time = datetime.now()

    if current_time - last_request_date >= timedelta(days=1):
        return True
    else:
        return False


# Запускаем бота
if __name__ == '__main__':
    bot.polling(none_stop=True)