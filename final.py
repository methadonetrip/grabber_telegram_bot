#pip install nltk pymorphy2 pyrogram
import re
import pymysql
import json
import nltk
import pymorphy2
import asyncio
import pymysql.cursors

from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton, Message
from aiogram.types import ParseMode
from nltk.stem import WordNetLemmatizer
from pymorphy2 import MorphAnalyzer
from collections import Counter

from db import add_user_to_db, add_channel_to_db, add_user_status, read_status_info, \
    read_channels_info, add_keyword_to_db, read_keywords_info, add_payment_to_db, \
    read_sub_info, find_chat_id_by_payment_id
from yookassa_integration import YooKassaIntegration
from config import host, user, password, db_name, bot_token, api_id, api_hash

lemmatizer = WordNetLemmatizer()
morph = MorphAnalyzer()

api_id = api_id
api_hash = api_hash
bot_token = '6776409787:AAEOHAIOpKMdTK9dFhQVJRLB09c3lqd5-HQ'
app = Client("grabber", api_id=api_id, api_hash=api_hash)
message = Message


# Команда для запуска бота
@app.on_message(filters.command("start"))
async def start(client, message: Message):
    await message.reply("Привет! Я помогу тебе найти твои ключевые слова в каналах! Используй клавиатуру ниже:", \
                        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    chat_id = message.chat.id
    await add_user_to_db(chat_id)


#НОРМАЛИЗАЦИЯ СЛОВ
def normalize_word(word, language):
    if language == 'english':
        return lemmatizer.lemmatize(word.lower())
    elif language == 'russian':
        return morph.parse(word)[0].normal_form
    else:
        return word

# Определение пользовательской клавиатуры
keyboard = [
    [KeyboardButton('/help')]
    [KeyboardButton('/list')],
    [KeyboardButton('/add_channel'), KeyboardButton('/add_keyword')],
    [KeyboardButton('/remove_channel'), KeyboardButton('/remove_keyword')],
    [KeyboardButton('/parse')]
    [KeyboardButton('/analyze_channel')]
]

# КНОПКА HELP
@Client.on_message(filters.command("help", prefixes="/"))
async def help(client, message):
    help_text = "🌟 Эта функция предоставляет помощь и информацию о взаимодействии с ботом Telegram.\n\
    \n\
    Вот что я могу делать для вас:\n\
    \n🚀 /start: Начните использовать бота или получите базовую информацию.\
    \n🔔 /subscribe: Подпишитесь на обновления или уведомления.\
    \n🔕 /unsubscribe: Отмените подписку на обновления или уведомления.\
    \n➕ /add_channel: Добавьте новый канал в список отслеживания бота.\
    \n➖ /remove_channel: Удалите канал из списка отслеживания.\
    \n🗝️ /add_keyword: Добавьте ключевое слово для отслеживания.\
    \n🔑 /remove_keyword: Удалите ключевое слово из отслеживания.\
    \n📃 /list_channels_keywords: Посмотрите список всех отслеживаемых каналов и ключевых слов.\
    \n 📊 Для получения статистики использования команд, используйте /stats.\
    \n🔍 Чтобы проанализировать канал, используйте /analyze_channel [название канала].\
    \nЕсли у вас есть вопросы или вам нужна дополнительная помощь, не стесняйтесь спрашивать!"
    await message.reply(help_text)

# ДОБАВИТЬ КАНАЛ
@app.on_message(filters.command("add_channel") & filters.private)
async def add_channel(client, message: Message):
    user_id = message.from_user.id
    await add_user_status(1, user_id)
    await message.reply("📝 Пожалуйста, отправьте мне название канала(ов), который вы хотите добавить.\n"\
                        "🔹 Формат: @channel1;@channel2\n"\
                        "💬 Вы можете указать несколько каналов, разделив их точкой с запятой.")

# УБРАТЬ КАНАЛ
@app.on_message(filters.command("remove_channel"))
async def remove_channel(client, message: Message):
    # Получение ID пользователя и изменение его статуса в базе данных
    user_id = message.from_user.id
    await add_user_status(-1, user_id)
    # Отправка сообщения пользователю с просьбой написать название канала
    await message.reply("📝 Напишите название канала")

# ДОБАВИТЬ KEYWORD
@app.on_message(filters.command("add_keyword"))
async def add_keyword(client, message: Message):
    user_id = message.from_user.id
    # Изменение статуса пользователя в базе данных для добавления ключевого слова
    await add_user_status(2, user_id)
    # Отправка инструкции пользователю о том, как добавить ключевое слово
    await message.reply("🔍 Отлично! Теперь отправьте мне ключевое слово или слова, которые вы хотите отслеживать.\n"\
                        "🌟 Формат: keyword1;keyword2\n"\
                        "📌 Вы можете указать несколько ключевых слов, разделив их точкой с запятой.")

# УДАЛИТЬ KEYWORD
@app.on_message(filters.command("remove_keyword"))
async def remove_keyword(client, message: Message):
    user_id = message.from_user.id
    # Изменение статуса пользователя в базе данных для удаления ключевого слова
    await add_user_status(-2, user_id)
    # Отправка сообщения пользователю с просьбой написать ключевое слово для удаления
    await message.reply("Write keyword")

# СПИСОК KEYWORDS И КАНАЛОВ
@app.on_message(filters.command("list"))
async def list_channels_keywords(client, message: Message):
    chat_id = message.chat.id
    # Получение списка каналов и ключевых слов, на которые подписан пользователь
    channels_str = await read_channels_info(chat_id)
    keywords_str = await read_keywords_info(chat_id)
    # Формирование и отправка ответа с перечнем каналов и ключевых слов
    response = (
        "📋 Вот каналы и слова, за которыми вы следите:\n\n"
        "📺 Отслеживаемые каналы:\n"
        f"{channels_str or 'None'}\n\n"  #Если каналов нет, то выведет None
        "🔑 Ключевые слова:\n"
        f"{keywords_str or 'None'}"  
        )
    await message.reply(response, reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

# Функция для проверки, содержит ли сообщение любое ключевое слово
async def contains_keyword(text, chat_id):
    if not text:
        return False

    keywords_string = await read_keywords_info(chat_id)
    keywords = keywords_string.split(';')  # Splitting the string into individual keywords
    print(f"Keywords for chat {chat_id}: {keywords}")  # Check the fetched keywords

    normalized_text = text.lower()
    for keyword in keywords:
        pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
        if re.search(pattern, normalized_text):
            print(f"Whole word '{keyword}' found in message.")  # Confirm whole word match
            return True

    return False

########################################################################################
########################################################################################
# ПАРСЕР
########################################################################################
########################################################################################

async def forward_messages_from_channel_to_bot(channel_id, bot_chat_id):
    async for message in app.get_chat_history(channel_id, limit=10):
        if await contains_keyword(message.text, bot_chat_id):
            await app.forward_messages(chat_id=bot_chat_id, from_chat_id=channel_id, message_ids=[message.id])


@app.on_message(filters.command("parse"))
async def check_all_channels(client, message: Message):
    chat_id = message.chat.id
    channel_ids = await read_channels_info(chat_id)
    for channel_id in channel_ids.split(";"):
        await forward_messages_from_channel_to_bot(channel_id, chat_id)

########################################################################################
########################################################################################
# ПАРСЕР
########################################################################################
########################################################################################


# Обработчик команды "analyze_channel", активируется при отправке команды /analyze_channel боту
@app.on_message(filters.command("analyze_channel"))
async def analyze_channel(client, message):
    try:
        # Извлечение названия канала из команды
        channel_name = message.command[1]  # Предполагается формат команды "/analyze_channel [channel_name]"
        # Выполнение анализа канала
        analysis = perform_channel_analysis(channel_name)  # Реализуйте эту функцию для анализа канала
        # Форматирование результатов анализа для отображения
        response = f"Анализ для {channel_name}:\n"
        for metric, value in analysis.items():
            response += f"- {metric}: {value}\n"
        # Отправка результатов анализа пользователю
        await message.reply(response)
    except IndexError:
        # Отправка сообщения об ошибке, если название канала не указано
        await message.reply("Пожалуйста, укажите имя канала. Формат: /analyze_channel [channel_name]")

# Функция для выполнения анализа канала
async def perform_channel_analysis(client, channel_name):
    async with client:
        # Получение истории сообщений из канала
        messages = await client.get_chat_history(channel_name, limit=100)  # Настройте лимит при необходимости
        # Часть анализа
        word_count = Counter()
        message_count = 0
        user_count = set()
        for message in messages:
            if message.text:
                # Подсчет слов в сообщениях
                words = message.text.split()
                word_count.update(words)
            # Увеличение счетчика сообщений и добавление ID пользователей
            message_count += 1
            user_count.add(message.from_user.id if message.from_user else 0)
        # Получение списка 10 наиболее часто встречающихся слов
        most_common_words = word_count.most_common(10)
        # Возврат результатов анализа
        return {
            "Всего сообщений": message_count,
            "Пользователей": len(user_count),
            "Наиьолее популярные слова": most_common_words
        }

# Основной обработчик сообщений, который реагирует на приватные сообщения, не являющиеся командой "add"
@app.on_message(filters.private & ~filters.command("add"))
async def handle_message(client, message: Message):
    # Получение ID пользователя и его текущего состояния
    user_id = message.from_user.id
    state = await read_status_info(user_id)
    print(state)
    # Обработка добавления канала
    if state == 1:
        # Получение текста сообщения и ID чата
        channel = message.text
        chat_id = message.chat.id
        channels_atm = await read_channels_info(chat_id)
        # Логика для добавления канала
        if channels_atm is None:
            # Проверка формата названия канала
            if channel.count("@") - 1 == channel.count(";") and ("@@" or "@;" or ";;") not in channel:
                await add_channel_to_db(channel, chat_id)
                await message.reply(f"Канал '{channel}' сохранен.")
            else:
                await message.reply("Напишите названия в коректном формате")
        else:
            # Проверка на уникальность и формат канала
            if channel.count("@") - 1 == channel.count(";") and ("@@" or "@;" or ";;") not in channel and channel not in channels_atm:
                channels_to_db = channels_atm + ";" + channel
                if channels_to_db[0] == ";":
                    channels_to_db = channels_to_db[1:]
                await add_channel_to_db(channels_to_db, chat_id)
                await message.reply(f"Канал '{channel}' сохранен.")
            else:
                await message.reply("Напишите названия в корректном формате")
        await add_user_status(0, user_id)
    # Обработка добавления ключевого слова
    elif state == 2:
        keyword = message.text
        chat_id = message.chat.id
        keywords_atm = await read_keywords_info(chat_id)
        # Логика для добавления ключевого слова
        if keywords_atm is None:
            if keyword != "." and keyword[-1] != ";":
                await add_keyword_to_db(keyword, chat_id)
                await message.reply(f"Слово '{keyword}' сохранено.")
            else:
                await message.reply("Напишите слова в корректном формате")
        else:
            if keyword != "." and keyword[-1] != ";" and keyword not in keywords_atm:
                keywords_to_db = keywords_atm + ";" + keyword
                if keywords_to_db[0] == ";":
                    keywords_to_db = keywords_to_db[1:]
                await add_keyword_to_db(keywords_to_db, chat_id)
                await message.reply(f"Слово '{keyword}' сохранено.")
            else:
                await message.reply("Напишите слова в корректном формате")
        await add_user_status(0, user_id)

    # Обработка удаления канала
    elif state == -1:
        channel = message.text
        chat_id = message.chat.id
        channel_atm = await read_channels_info(chat_id)
        channel_atm = channel_atm.split(";")
        # Логика для удаления канала
        if channel in channel_atm:
            channel_atm.remove(channel)
            channel_atm = ";".join(channel_atm)
            await add_channel_to_db(channel_atm, chat_id)
            await message.reply(f" '{channel}' удален.")
        else:
            await message.reply("Напишите название канала в корректном формате")
        await add_user_status(0, user_id)
    # Обработка удаления ключевого слова
    elif state == -2:
        keyword = message.text
        chat_id = message.chat.id
        keywords_atm = await read_keywords_info(chat_id)
        keywords_atm = keywords_atm.split(";")
        # Логика для удаления ключевого слова
        if keyword in keywords_atm:
            keywords_atm.remove(keyword)
            keywords_atm = ";".join(keywords_atm)
            await add_keyword_to_db(keywords_atm, chat_id)
            await message.reply(f" '{keyword}' удален.")
        else:
            await message.reply("Напишите слова в корректном формате")
        await add_user_status(0, user_id)

# Запуск приложения
if __name__ == "__main__":
    app.run()
