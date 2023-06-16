import logging
import asyncio
import re
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware
from aiogram.dispatcher import FSMContext
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Настройка журналирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token='6061615221:AAHCp6cIYu8_brmXzaVqNkdiAzWdW_-mnfM')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LifetimeControllerMiddleware())

# Подключение к базе данных SQLite
Base = declarative_base()
engine = create_engine('sqlite:///bot_data.db')
Session = sessionmaker(bind=engine)
session = Session()


# Класс для представления таблицы пользователей в базе данных
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer)
    username = Column(String)
    reminder_text = Column(String)
    reminder_datetime = Column(DateTime)
    document_id = Column(String)


Base.metadata.create_all(engine)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Привет! Я бот-органайзер. Чем я могу тебе помочь?")


@dp.message_handler()
async def handle_message(message: types.Message, state: FSMContext):
    # Проверяем, является ли сообщение командой /set_reminder
    if re.match(r'^/set_reminder\b', message.text):
        await set_reminder(message, state)
    else:
        await handle_reminder(message, state)


async def set_reminder(message: types.Message, state: FSMContext):
    await message.answer("Чтобы установить напоминание, отправь мне следующую информацию:\n"
                         "<текст_напоминания>\n"
                         "<дата_напоминания> <время_напоминания>\n"
                         "Прикрепи файл с домашним заданием (если есть).")


async def handle_reminder(message: types.Message, state: FSMContext):
    args = message.text.split(maxsplit=2)
    if len(args) != 3:
        await message.answer("Неверное количество аргументов. Используйте:\n"
                             "<текст_напоминания>\n"
                             "<дата_напоминания> <время_напоминания>")
        return

    reminder_text = args[0]  # Текст напоминания
    reminder_date = args[1]  # Дата напоминания (в формате DD.MM.YYYY)
    reminder_time = args[2]  # Время напоминания (в формате HH:MM)

    try:
        reminder_datetime = datetime.strptime(f"{reminder_date} {reminder_time}", '%d.%m.%Y %H:%M')

        # Сохраняем данные пользователя в базу данных
        user = User(chat_id=message.chat.id, username=message.from_user.username,
                    reminder_text=reminder_text, reminder_datetime=reminder_datetime)
        session.add(user)
        session.commit()

        await message.answer(f"Напоминание установлено на {reminder_datetime}")

        # Запускаем задачу напоминания
        await send_reminder(reminder_datetime, message.chat.id, reminder_text)

    except ValueError:
        await message.answer("Неверный формат даты или времени. Пожалуйста, используйте правильный формат: "
                             "DD.MM.YYYY HH:MM.")


async def send_reminder(reminder_datetime, chat_id, reminder_text):
    delta = reminder_datetime - datetime.now()

    if delta.total_seconds() > 0:
        await asyncio.sleep(delta.total_seconds())

        # Получаем данные пользователя из базы данных
        user = session.query(User).filter_by(chat_id=chat_id).first()
        if user:
            # Отправляем напоминание
            await bot.send_message(chat_id=chat_id, text=f"Напоминание: {user.reminder_text}")

            # Удаляем данные пользователя из базы данных после отправки напоминания
            session.delete(user)
            session.commit()


@dp.message_handler(content_types=['document'])
async def handle_document(message: types.Message, state: FSMContext):
    document = message.document

    # Получаем данные пользователя из базы данных
    user = session.query(User).filter_by(chat_id=message.chat.id).first()
    if user:
        # Обновляем данные пользователя с информацией о прикрепленном файле
        user.document_id = document.file_id
        session.commit()

        await message.answer(f"Файл {document.file_name} принят.")


@dp.message_handler()
async def unknown_command(message: types.Message):
    await message.answer("Извините, я не понимаю эту команду.")


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(dp.start_polling())
    finally:
        loop.run_until_complete(dp.storage.close())
        loop.run_until_complete(dp.storage.wait_closed())
        loop.close()