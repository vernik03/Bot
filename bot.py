from asyncio.windows_events import NULL
import telebot
import mysql.connector
from mysql.connector import Error
from telebot import types

from sql_query import CreateQuery
from KEYS import *
from query_handler import handle_query
from message_handler import handle_message
from global_variables import *


def create_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name,
            auth_plugin='mysql_native_password',
            autocommit=True
        )
        print("Connection to MySQL DB '", db_name, "' successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection


connection = create_connection(IP, USERNAME, PASSWORD, "theatres")

menu_item = 'Main'

handler_item = ''

elems = []

temp = ""

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=["start"])
def start_message(message):
    markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1=types.KeyboardButton("Купити квиток")
    item2=types.KeyboardButton("Афіша")
    item4=types.KeyboardButton("Написати відгук")
    item3=types.KeyboardButton("Адміністрування")
    markup.row(item2)
    markup.add(item1, item4)
    markup.row(item3)
    bot.send_message(message.chat.id, 'Выберите действие',  reply_markup=markup)
    if not CreateQuery(connection,"SELECT EXISTS(SELECT visitor_id FROM visitor WHERE chat_id = %s)", (message.chat.id,)):  
        CreateQuery(connection,"INSERT INTO visitor (visitor_name, phone, chat_id, is_root) VALUES (NULL, NULL, %s, FALSE)", (message.chat.id,))


@bot.callback_query_handler(func=lambda call: True)    
def query_handler(call):
    handle_query(call)


@bot.message_handler(content_types=["text"])
def handle_text(message):
    handle_message(message)
            

bot.polling(none_stop=True, interval=0)