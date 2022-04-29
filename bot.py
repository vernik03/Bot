import telebot
import mysql.connector
from mysql.connector import Error
from prettytable import PrettyTable, from_db_cursor
from telebot import types



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

def Query(connection, query, parameter):
    cursor = connection.cursor()
    mytable = PrettyTable()
    try:
        if parameter is None:
            cursor.execute(query)
        else:
            cursor.execute(query, parameter)  
            x = cursor.fetchall()
            if x == []:
                 return None
            if x[0][0] == 0 or x[0][0] == 1:
                return x[0][0]
        
        mytable = from_db_cursor(cursor)
        if mytable == None:
            return None
        mytable.align='l'
        return str(mytable)
    except Error as e :
        print(f"The error '{e}' occurred")

def CreateQuery(connection, query, parameter=None):
    result = Query(connection, query, parameter)
    return result #?????


# print(CreateQuery(connection,"SELECT * FROM visitor"))
# Создаем экземпляр бота

connection = create_connection("178.159.224.36", "-root", "server03", "theatres")
menu_item = 'Main'
bot = telebot.TeleBot('5305649926:AAETirjAU_QJ-Hd4Sv4_09I3qUkKmlf7jHM')
# Функция, обрабатывающая команду /start
@bot.message_handler(commands=["start"])
def start_message(message):
    markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1=types.KeyboardButton("Остановить работу")
    item2=types.KeyboardButton("Root")
    markup.add(item1)
    markup.add(item2)
    bot.send_message(message.chat.id, 'Выберите действие',  reply_markup=markup)
    if not CreateQuery(connection,"SELECT EXISTS(SELECT visitor_id FROM visitor WHERE chat_id = %s)", (message.chat.id,)):  
        CreateQuery(connection,"INSERT INTO visitor (visitor_name, phone, chat_id, is_root) VALUES (NULL, NULL, %s, FALSE)", (message.chat.id,))
    #markup = telebot.types.InlineKeyboardMarkup()
    #markup.add(telebot.types.InlineKeyboardButton(text='Root', callback_data=1))
    #markup.add(telebot.types.InlineKeyboardButton(text='Остановить работу', callback_data=4))
    #bot.send_message(message.chat.id, text="Выберите дальнейшее действие", reply_markup=markup)
    #CreateQuery(connection,"INSERT INTO visitor (visitor_name, phone, chat_id, is_root) VALUES (NULL, NULL, %s, FALSE);", message.chat.id)
#@bot.callback_query_handler(func=lambda call: True)    
#def query_handler(call):

    #bot.answer_callback_query(callback_query_id=call.id, text='Спасибо за ответ!')
    #answer = ''
    #if call.data == '1':
        #answer = 'Введите пароль'
    #elif call.data == '4':
        #answer = 'Работа остановлена'
    #bot.send_message(call.message.chat.id, answer)
    #bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
# Получение сообщений от юзера
@bot.message_handler(content_types=["text"])
def handle_text(message):
    global menu_item
    answer = ''
    #if CreateQuery(connection,"SELECT EXISTS(SELECT id FROM logged_in_users WHERE id = %s)", message.chat.id):
    #   bot.send_message(message.chat.id, 'Вы уже вошли в систему')
    #else :
    #    if (message.text == 'server03') :
    #        CreateQuery(connection,"INSERT INTO visitors VALUES (None, None, ?, 1);", message.chat.id)
    
    if menu_item == 'Main':        
        if message.text.strip() == 'Root' :
            if CreateQuery(connection,"SELECT EXISTS(SELECT visitor_id FROM visitor WHERE chat_id = %s AND is_root = TRUE)", (message.chat.id,)):                
                menu_item = 'Root'
                answer = 'Вы уже вошли в систему'
            else :
                menu_item = 'Root'
                answer = 'Введите пароль'
        elif message.text.strip() == 'Остановить работу':
                answer = 'Пока'
    elif menu_item == 'Root':
        if message.text.strip() == 'Остановить работу' :
            menu_item = 'Main'
            answer = 'Пока'
        elif message.text.strip() == 'server03' :
            CreateQuery(connection,"SET SQL_SAFE_UPDATES = 0")
            CreateQuery(connection,"UPDATE visitor SET is_root = TRUE WHERE chat_id = %s", (message.chat.id,))
            answer = 'Вы успешно вошли в систему'
        elif CreateQuery(connection,"SELECT EXISTS(SELECT visitor_id FROM visitor WHERE chat_id = %s)", (message.chat.id,)):
            bot.send_message(message.chat.id, '`' + CreateQuery(connection,message.text) + '`', parse_mode='MarkdownV2')    
            answer = ''    
        else :
            menu_item = 'Main'
            answer = 'Неверный пароль'  
    if answer != '':
        bot.send_message(message.chat.id, answer)
            
       
      
    
# Запускаем бота
bot.polling(none_stop=True, interval=0)