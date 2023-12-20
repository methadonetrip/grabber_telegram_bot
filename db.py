import pymysql
import pymysql.cursors
from pyrogram import Client, filters
from pyrogram.types import Message
from config import host, user, password, db_name, bot_token

# Настройка подключения к базе данных
connection = pymysql.connect(host=host,
                             port=3306,
                             user=user,
                             password=password,
                             database=db_name,
                             cursorclass=pymysql.cursors.DictCursor)

app = Client("my_bot", bot_token=bot_token)

# Функции для работы с базой данных
async def add_user_to_db(chat_id):
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO userid (id) VALUES (%s) ON DUPLICATE KEY UPDATE id = id"
            cursor.execute(sql, (chat_id,))
        connection.commit()
    except Exception as e:
        print(f"Error adding user to database: {e}")

async def add_user_status(state, chat_id):
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE userid SET status = %s WHERE id = %s "
            cursor.execute(sql, (state, chat_id))
        connection.commit()
    except Exception as e:
        print(f"Error adding user to database: {e}")

async def add_channel_to_db(channel, chat_id):
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE userid SET channels = %s WHERE id = %s "
            cursor.execute(sql, (channel, chat_id))
        connection.commit()
    except Exception as e:
        print(f"Error adding user to database: {e}")

async def add_keyword_to_db(channel, chat_id):
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE userid SET keywords = %s WHERE id = %s "
            cursor.execute(sql, (channel, chat_id))
        connection.commit()
    except Exception as e:
        print(f"Error adding user to database: {e}")

async def add_payment_to_db(sub, chat_id):
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE userid SET sub = '%s' WHERE id = %s"
            cursor.execute(sql, (sub, chat_id))
        connection.commit()
    except Exception as e:
        print(f"Error updating payment info in database: {e}")

async def read_sub_info(chat_id):
    try:
        with connection.cursor() as cursor:
            sql = "SELECT `sub` FROM usersinfo.userid WHERE `id` = %s"
            cursor.execute(sql, (chat_id,))
            result = cursor.fetchone()
            if result:
                return result.get('sub')
            else:
                return 0
    except Exception as e:
        print(f"Error reading user info from database: {e}")
        return None
    
async def read_status_info(chat_id):
    try:
        with connection.cursor() as cursor:
            sql = "SELECT `status` FROM usersinfo.userid WHERE `id` = %s"
            cursor.execute(sql, (chat_id,))
            result = cursor.fetchone()
            if result:
                return result.get('status')
            else:
                return 0
    except Exception as e:
        print(f"Error reading user info from database: {e}")
        return None

async def read_channels_info(chat_id):
    try:
        with connection.cursor() as cursor:
            sql = "SELECT `channels` FROM usersinfo.userid WHERE `id` = %s"
            cursor.execute(sql, (chat_id,))
            result = cursor.fetchone()
            if result:
                return result.get('channels')
            else:
                return ""
    except Exception as e:
        print(f"Error reading user info from database: {e}")
        return None

async def read_keywords_info(chat_id):
    try:
        with connection.cursor() as cursor:
            sql = "SELECT `keywords` FROM usersinfo.userid WHERE `id` = %s"
            cursor.execute(sql, (chat_id,))
            result = cursor.fetchone()
            if result:
                return result.get('keywords')
            else:
                return ""
    except Exception as e:
        print(f"Error reading user info from database: {e}")
        return None
    
async def find_chat_id_by_payment_id(payment_id):
    with connection.cursor() as cursor:
        try:
            cursor.execute("SELECT chat_id FROM payments WHERE payment_id = %s", (payment_id,))
            result = cursor.fetchone()
            return result['chat_id'] if result else None
        except Exception as e:
            print(f"Error finding chat ID by payment ID: {e}")
            return None
