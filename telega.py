import logging
import random
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Функция-обработчик для команды /start
def start(update: Update, context: CallbackContext) -> None:
    context.user_data['number'] = random.randint(1, 100)
    update.message.reply_text('Привет! Я загадал число от 1 до 100. Попробуй угадать.')

# Функция-обработчик для сообщений
def guess(update: Update, context: CallbackContext) -> None:
    message = update.message.text
    if not message.isdigit():
        update.message.reply_text('Пожалуйста, введите целое число.')
        return

    guess_number = int(message)
    target_number = context.user_data.get('number')

    if guess_number == target_number:
        update.message.reply_text('Поздравляю! Ты угадал число.')
        context.user_data.pop('number')
    elif guess_number < target_number:
        update.message.reply_text('Загаданное число больше.')
    else:
        update.message.reply_text('Загаданное число меньше.')

# Основная функция, вызывается при запуске бота
def main() -> None:
    # Создание объекта для взаимодействия с Telegram API
    updater = Updater("6061615221:AAHCp6cIYu8_brmXzaVqNkdiAzWdW_-mnfM", use_context=True, update_queue=Queue())

    # Получение объекта диспетчера для регистрации обработчиков
    dispatcher = updater.dispatcher

    # Регистрация обработчиков
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, guess))

    # Запуск бота
    updater.start_polling()

    # Остановка бота при нажатии Ctrl+C
    updater.idle()

if __name__ == '__main__':
    main()