import telebot
import mysql.connector
from mysql.connector import Error
from prettytable import PrettyTable, from_db_cursor

def create_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name,
            auth_plugin='mysql_native_password'
        )
        print("Connection to MySQL DB '", db_name, "' successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection

def Query(connection, query):
    cursor = connection.cursor()
    mytable = PrettyTable()
    try:
        cursor.execute(query)
        mytable = from_db_cursor(cursor)
        mytable.align='l'
        return mytable
    except Error as e:
        print(f"The error '{e}' occurred")

def CreateQuery(connection, query):
    result = Query(connection, query)
    return str(result) #?????

connection = create_connection("178.159.224.36", "vernik03", "server03", "theatres")

# print(CreateQuery(connection,"SELECT * FROM visitor"))
# Создаем экземпляр бота
bot = telebot.TeleBot('5305649926:AAETirjAU_QJ-Hd4Sv4_09I3qUkKmlf7jHM')
# Функция, обрабатывающая команду /start
@bot.message_handler(commands=["start"])
def start(m, res=False):
    bot.send_message(m.chat.id, 'Я на связи. Напиши мне что-нибудь )')
# Получение сообщений от юзера
@bot.message_handler(content_types=["text"])
def handle_text(message):
    bot.send_message(message.chat.id, '`' + CreateQuery(connection,message.text) + '`', parse_mode='MarkdownV2')
# Запускаем бота
bot.polling(none_stop=True, interval=0)