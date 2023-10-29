import telebot
import json

# Указать ваш токен
TOKEN = '6549394842:AAH6uK7zKiULJXDaXqH7onmZ1iedxH4Np4Y'

# Инициализируем бота
bot = telebot.TeleBot(TOKEN)

# Переменные для хранения информации пользователя
user_data = {}

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.chat.id
    bot.send_message(user_id, "Привет! Давайте начнем регистрацию.")
    bot.send_message(user_id, "Введите ваше имя:")
    bot.register_next_step_handler(message, get_name)

def get_name(message):
    user_id = message.chat.id
    user_data['name'] = message.text
    bot.send_message(user_id, "Отлично! Теперь введите вашу фамилию:")
    bot.register_next_step_handler(message, get_surname)

def get_surname(message):
    user_id = message.chat.id
    user_data['surname'] = message.text
    bot.send_message(user_id, "Хорошо! Теперь введите ваш номер телефона:")
    bot.register_next_step_handler(message, get_phone)

def get_phone(message):
    user_id = message.chat.id
    user_data['phone'] = message.text

    # Формируем JSON из данных пользователя
    user_json = json.dumps(user_data, ensure_ascii=False)

    # Отправляем JSON другому пользователю (замените ID на ID другого пользователя)
    bot.send_message(user_id, f"Пользователь {user_id} отправил следующие данные:\n{user_json}")

    bot.send_message(user_id, "Спасибо! Ваши данные были отправлены.")
    user_data.clear()

# Запускаем бота
bot.polling()