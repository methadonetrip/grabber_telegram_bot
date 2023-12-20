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

from db import add_user_to_db, add_channel_to_db, add_user_status, read_status_info, \
    read_channels_info, add_keyword_to_db, read_keywords_info, add_payment_to_db, \
    read_sub_info, find_chat_id_by_payment_id
from yookassa_integration import YooKassaIntegration
from config import host, user, password, db_name, bot_token, api_id, api_hash

lemmatizer = WordNetLemmatizer()
morph = MorphAnalyzer()

api_id = api_id     # Замените на ваш Telegram API ID
api_hash = api_hash # Замените на ваш Telegram API Hash
bot_token = '6776409787:AAEOHAIOpKMdTK9dFhQVJRLB09c3lqd5-HQ'
app = Client("grabber", api_id=api_id, api_hash=api_hash)
message = Message


# Команда для запуска бота
@app.on_message(filters.command("start"))
async def start(client, message: Message):
    """
    start

    :param client: client
    :param message: message
    :return: message and add_user_to_db
    """
    await message.reply("Bot is running. Use the keyboard below:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    chat_id = message.chat.id
    await add_user_to_db(chat_id)


#НОРМАЛИЗАЦИЯ СЛОВ
def normalize_word(word, language):
    """
    word normalization

    :param word: word
    :param language: language
    :return: word
    """
    if language == 'english':
        return lemmatizer.lemmatize(word.lower())
    elif language == 'russian':
        return morph.parse(word)[0].normal_form
    else:
        return word

# Определение пользовательской клавиатуры
keyboard = [
    [KeyboardButton('/subscribe'), KeyboardButton('/unsubscribe'), KeyboardButton('/list')],
    [KeyboardButton('/add_channel'), KeyboardButton('/add_keyword')],
    [KeyboardButton('/remove_channel'), KeyboardButton('/remove_keyword')],
    [KeyboardButton('/parse')]
]

@app.on_message(filters.command("add_channel") & filters.private)
async def add_channel(client, message: Message):
    """
    add channel

    :param client: client
    :param message: message
    :return: message and add_user_status
    """
    user_id = message.from_user.id
    await add_user_status(1, user_id)
    await message.reply("Please send me the name/names of the channel/channels.\n Format: @channel1;@channel2")


# УБРАТЬ КАНАЛ
@app.on_message(filters.command("remove_channel"))
async def remove_channel(client, message: Message):
    """
    remove channel

    :param client: client
    :param message: message
    :return: message and add_user_status
    """
    user_id = message.from_user.id
    await add_user_status(-1, user_id)
    await message.reply("Write channel")

# ПАДПИСАЦА
@app.on_message(filters.command("subscribe"))
async def subscribe(client, message: Message):
    """
    subscribe

    :param client: client
    :param message: message
    :return: message
    """
    chat_id = message.from_user.id
    sub = await read_sub_info(chat_id)
    if sub == 0:
        await message.reply("You subscrbed now.", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        await add_payment_to_db(1, chat_id)
    else:
        await message.reply("You have already subscribed.", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

# ОТПИСАТЬСЯ
@app.on_message(filters.command("unsubscribe"))
async def unsubscribe(client, message: Message):
    """
    unsubscribe

    :param client: client
    :param message: message
    :return: message
    """
    chat_id = message.from_user.id
    sub = await read_sub_info(chat_id)
    if sub == 1:
        await message.reply("You now unsubscribed.", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        await add_payment_to_db(0, chat_id)
    else:
        await message.reply("You have not subscribed.", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

# ДОБАВИТЬ KEYWORD
@app.on_message(filters.command("add_keyword"))
async def add_keyword(client, message: Message):
    """
    add keyword

    :param client: client
    :param message: message
    :return: message and add_user_status
    """
    user_id = message.from_user.id
    await add_user_status(2, user_id)
    await message.reply("Please send me the keyword/keywords \n Format: keyword1;keyword2")

# УДАЛИТЬ KEYWORD
@app.on_message(filters.command("remove_keyword"))
async def remove_keyword(client, message: Message):
    """
    remove keyword

    :param client: client
    :param message: message
    :return: message and add_user_status
    """
    user_id = message.from_user.id
    await add_user_status(-2, user_id)
    await message.reply("Write keyword")

# СПИСОК KEYWORDS И КАНАЛОВ
@app.on_message(filters.command("list"))
async def list_channels_keywords(client, message: Message):
    """
    list channels keywords

    :param client: client
    :param message: message
    :return: message
    """
    chat_id = message.chat.id
    channels_str = await read_channels_info(chat_id)
    keywords_str = await read_keywords_info(chat_id)
    response = f"Monitored Channels: {channels_str}\nKeywords: {keywords_str}"
    await message.reply(response, reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

# Функция для проверки, содержит ли сообщение любое ключевое слово

import re

async def contains_keyword(text, chat_id):
    """
    contains keyword

    :param text: text
    :return: func
    """
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
    """
    forward messages from channel to bot

    :param channel_id: channel id
    :param bot_chat_id: bot chat id
    :return: forward_messages
    """
    async for message in app.get_chat_history(channel_id, limit=10):
        if await contains_keyword(message.text, bot_chat_id):
            await app.forward_messages(chat_id=bot_chat_id, from_chat_id=channel_id, message_ids=[message.id])


@app.on_message(filters.command("parse"))
async def check_all_channels(client, message: Message):
    """
    check all channales

    :param client: client
    :param message: message
    :return: forward_messages_from_channel_to_bot
    """
    chat_id = message.chat.id
    channel_ids = await read_channels_info(chat_id)
    for channel_id in channel_ids.split(";"):
        await forward_messages_from_channel_to_bot(channel_id, chat_id)

########################################################################################
########################################################################################
# ПАРСЕР
########################################################################################
########################################################################################

# Основной обработчик сообщений
@app.on_message(filters.private & ~filters.command("add"))
async def handle_message(client, message: Message):
    """
    handle message

    :param client: client
    :param message: message
    :return: message and func
    """
    user_id = message.from_user.id
    state = await read_status_info(user_id)
    print(state)
    if state == 1:
        # Сохраняем сообщение в базу данных
        channel = message.text
        chat_id = message.chat.id
        channels_atm = await read_channels_info(chat_id)
        if channels_atm is None:
            if channel.count("@") - 1 == channel.count(";") and ("@@" or "@;" or ";;") not in channel:
                await add_channel_to_db(channel, chat_id)
                await message.reply(f"Channel '{channel}' saved.")
            else:
                await message.reply("Write the channel names in the correct format")
        else:
            if channel.count("@") - 1 == channel.count(";") and ("@@" or "@;" or ";;") not in channel and channel not in channels_atm:
                channels_to_db = channels_atm + ";" + channel
                if channels_to_db[0] == ";":
                    channels_to_db = channels_to_db[1:]
                await add_channel_to_db(channels_to_db, chat_id)
                await message.reply(f"Channel '{channel}' saved.")
            else:
                await message.reply("Write the channel names in the correct format")
        await add_user_status(0, user_id)
    if state == 2:
        # Сохраняем сообщение в базу данных
        keyword = message.text
        chat_id = message.chat.id
        keywords_atm = await read_keywords_info(chat_id)
        if keywords_atm is None:
            if keyword != "." and keyword[-1] != ";":
                await add_keyword_to_db(keyword, chat_id)
                await message.reply(f" '{keyword}' saved.")
            else:
                await message.reply("Write the keyword names in the correct format")
        else:
            if keyword != "." and keyword[-1] != ";" and keyword not in keywords_atm:
                keywords_to_db = keywords_atm + ";" + keyword
                if keywords_to_db[0] == ";":
                    keywords_to_db = keywords_to_db[1:]
                await add_keyword_to_db(keywords_to_db, chat_id)
                await message.reply(f" '{keyword}' saved.")
            else:
                 await message.reply("Write the keyword names in the correct format")
        await add_user_status(0, user_id)
    if state == -1:
        channel = message.text
        chat_id = message.chat.id
        channel_atm = await read_channels_info(chat_id)
        channel_atm = channel_atm.split(";")
        if channel in channel_atm:
            channel_atm.remove(channel)
            channel_atm = ";".join(channel_atm)
            await add_channel_to_db(channel_atm, chat_id)
            await message.reply(f" '{channel}' deleted.")
        else:
            await message.reply("Write the channel name in the correct format")
        await add_user_status(0, user_id)
    if state == -2:
        keyword = message.text
        chat_id = message.chat.id
        keywords_atm = await read_keywords_info(chat_id)
        keywords_atm = keywords_atm.split(";")
        if keyword in keywords_atm:
            keywords_atm.remove(keyword)
            keywords_atm = ";".join(keywords_atm)
            await add_keyword_to_db(keywords_atm, chat_id)
            await message.reply(f" '{keyword}' deleted.")
        else:
            await message.reply("Write the keyword name in the correct format")
        await add_user_status(0, user_id)
if __name__ == "__main__":
    app.run()
