import logging
import random
import json
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Устанавливаем уровень логирования для получения информации об ошибках
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Список для хранения сохраненных сообщений, гифок и стикеров
saved_data = []

# Пороговое значение для отправки случайных сообщений
N = 3  # Измените это значение на желаемое количество сообщений

# Флаг для отслеживания состояния работы бота
bot_started = False

# Флаг для отслеживания остановки бота
bot_stopped = False

# Объявляем updater и dp как глобальные переменные
updater = None
dp = None


# Функция для обработки команды /start
def start(update: Update, context: CallbackContext):
    global bot_started
    global updater
    global dp

    user = update.effective_user
    if update.message:
        update.message.reply_text(
            f"Привет, {user.first_name}! Я бот")

    if not bot_started:
        updater.start_polling()
        bot_started = True


# Функция для сохранения сообщений, гифок и стикеров в файл
def save_message(update: Update, context: CallbackContext):
    if not bot_stopped:  # Проверяем флаг остановки перед обработкой новых сообщений
        data = {
            'message_id': update.message.message_id,
            'text': update.message.text,
            'document': update.message.document.to_dict() if update.message.document else None,
            'sticker': update.message.sticker.to_dict() if update.message.sticker else None
        }

        saved_data.append(data)

        if len(saved_data) % N == 0:
            send_random_message(update, context)

        with open('saved_data.json', 'w', encoding='utf-8') as file:
            json.dump(saved_data, file, ensure_ascii=False, indent=4)


# Функция для отправки случайных сохраненных сообщений
def send_random_message(update: Update, context: CallbackContext):
    random.shuffle(saved_data)
    random_item = random.choice(saved_data)

    if random_item['text']:
        update.message.reply_text(random_item['text'])
    elif random_item['document']:
        update.message.reply_document(random_item['document']['file_id'])
    elif random_item['sticker']:
        update.message.reply_sticker(random_item['sticker']['file_id'])


# Функция для обработки команды /stop
def stop(update: Update, context: CallbackContext):
    global bot_stopped
    user = update.effective_user
    update.message.reply_text(f"До свидания, {user.first_name}!")
    bot_stopped = True  # Устанавливаем флаг остановки
    updater.stop()
    updater.is_idle = False


def main():
    global updater
    global dp

    # Загрузка сохраненных данных из файла
    try:
        with open('saved_data.json', 'r', encoding='utf-8') as file:
            saved_data.extend(json.load(file))
    except FileNotFoundError:
        pass

    # Замените "YOUR_TELEGRAM_BOT_TOKEN" на свой токен бота
    updater = Updater("YOUR_TELEGRAM_BOT_TOKEN", use_context=True)

    # Получаем диспетчер для регистрации обработчиков команд и сообщений
    dp = updater.dispatcher

    # Обработчик команды /start
    dp.add_handler(CommandHandler("start", start))

    # Обработчик для сохранения сообщений
    dp.add_handler(MessageHandler(Filters.all & ~Filters.command, save_message))

    # Обработчик команды /stop
    dp.add_handler(CommandHandler("stop", stop))

    # Запускаем бота
    updater.start_polling()

    # Чтобы бот работал непрерывно, пока его не остановят явно (Ctrl-C)
    updater.idle()


if __name__ == '__main__':
    main()

