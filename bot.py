from asyncio.windows_events import NULL
import telebot
import mysql.connector
from mysql.connector import Error
from telebot import types
from prettytable import PrettyTable, from_db_cursor

from KEYS import *

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
bot = telebot.TeleBot(TOKEN)

menu_item = 'Main'
handler_item = ''
elems = []
temp = ""
answer = ''

def CreateQuery(connection, query, parameter=None, is_str=True):
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

        
        if not is_str and parameter is None:
            res = cursor.fetchall()
            res = [ i[0] for i in res ]
            return res
        elif not is_str:
            x = [ i[0] for i in x ]
            return x

        mytable = from_db_cursor(cursor)
        if mytable == None:
            return None
        mytable.align='l'
        return str(mytable)
    except Error as e :
        print(f"The error '{e}' occurred")

def handle_start_message(message):
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

def handle_query(call):
    global menu_item
    global handler_item
    global elems
    global temp
    global answer

    if handler_item == 'Perf':
        temp = elems[int(call.data)-1]
        elems = CreateQuery(connection,"SELECT theatre_name FROM theatre, ticket, performance,visitor WHERE performance.perf_id = ticket.perf_id AND ticket.theatre_id = theatre.theatre_id AND performance.perf_name = %s AND visitor.chat_id = %s", (elems[int(call.data)-1], call.from_user.id), False)
        i = 1
        markup = telebot.types.InlineKeyboardMarkup()
        for elem in elems:
            markup.add(telebot.types.InlineKeyboardButton(text=elem, callback_data=i))
            i+=1
        handler_item = 'Theatre'
        bot.send_message(call.message.chat.id,"Оберіть театр, який ви відвідали", reply_markup=markup)


    elif handler_item == 'Theatre':
        ticket_id = 0
        ticket_id = CreateQuery(connection,"SELECT ticket_id FROM ticket, performance, theatre, visitor WHERE performance.perf_id = ticket.perf_id AND ticket.theatre_id = theatre.theatre_id AND ticket.theatre_id = theatre.theatre_id AND theatre.theatre_name = %s AND performance.perf_name = %s AND ticket.visitor_id = visitor.visitor_id AND visitor.chat_id = %s", (elems[int(call.data)-1],temp,call.from_user.id), False)
        handler_item = 'Review_OK'
        temp = ticket_id[0]
        if CreateQuery(connection,"SELECT visitor_name FROM visitor WHERE visitor.chat_id = %s", (call.from_user.id,), False)[0] == None:
            menu_item = 'Name'
            bot.send_message(call.from_user.id, "Введіть ваше ім'я")
        else :
            menu_item = '***'
            bot.send_message(call.from_user.id, "Напишіть відгук")


    elif handler_item == 'Edit_Perf':
        temp = CreateQuery(connection,"SELECT perf_id FROM performance WHERE perf_name = %s", (elems[int(call.data)-1],), False)[0]
        menu_item = 'Edit_Perf_OK'
        markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
        item4=types.KeyboardButton("Змінити назву")
        item5=types.KeyboardButton("Змінити тривалість")
        item1=types.KeyboardButton("Додати персонажа")
        item2=types.KeyboardButton("Додати театр")
        item3=types.KeyboardButton("<- Назад")
        markup.add(item4, item5)
        markup.add(item1, item2)
        markup.row(item3)
        bot.send_message(call.from_user.id,'Виберіть дію', reply_markup=markup)
        handler_item = ' '


    elif handler_item == 'Edit_Perf_Theatre':
        CreateQuery(connection,"INSERT INTO performance_theatre (perf_id, theatre_id) VALUES (%s, %s)", (temp, CreateQuery(connection,"SELECT theatre_id FROM theatre WHERE theatre_name = %s", (elems[int(call.data)-1],), False)[0]))
        bot.send_message(call.from_user.id, "Театр додано")
        handler_item = ' '

def Root_menu(message):
    global menu_item
    global handler_item
    global elems
    global temp    
    global answer

    if message.text.strip() == '<- Назад':
        menu_item = 'Main'
        markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1=types.KeyboardButton("Купити квиток")
        item2=types.KeyboardButton("Афіша")
        item4=types.KeyboardButton("Написати відгук")
        item3=types.KeyboardButton("Адміністрування")
        markup.row(item2)
        markup.add(item1, item4)
        markup.row(item3)
        bot.send_message(message.chat.id,'Назад до головного меню', reply_markup=markup)
    elif message.text.strip() == 'Додати виставу' :
        menu_item = 'Add_Perf'
        answer = 'Введіть назву вистави'
    elif message.text.strip() == 'Додати співробітника' :
        answer = "В розробці"
    elif message.text.strip() == 'Звільнити співробітника' :
        answer = "В розробці"
    elif message.text.strip() == 'Змінити виставу' :
        menu_item = 'Edit_Perf'
        markup = telebot.types.InlineKeyboardMarkup()
        elems = CreateQuery(connection,"SELECT perf_name FROM performance",None, False)
        i=1
        handler_item = 'Edit_Perf'
        for elem in elems:
            markup.add(telebot.types.InlineKeyboardButton(text=elem, callback_data=i))
            i+=1
        bot.send_message(message.chat.id,"Оберіть назву вистави", reply_markup=markup)
    else :
        if message.text.strip() == PASSWORD :
            CreateQuery(connection,"SET SQL_SAFE_UPDATES = 0")
            CreateQuery(connection,"UPDATE visitor SET is_root = TRUE WHERE chat_id = %s", (message.chat.id,))
        else :
            menu_item = 'Main'
            answer = 'Неверный пароль'  

        if CreateQuery(connection,"SELECT EXISTS(SELECT visitor_id FROM visitor WHERE chat_id = %s)", (message.chat.id,)):
            markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1=types.KeyboardButton("Додати виставу")
            item2=types.KeyboardButton("Додати співробітника")
            item3=types.KeyboardButton("Змінити виставу")
            item4=types.KeyboardButton("Звільнити співробітника")
            item6=types.KeyboardButton("<- Назад")
            markup.add(item1, item2)
            markup.add(item3, item4)
            markup.row(item6)
            if message.text.strip() == 'Адміністрування' or message.text.strip() == PASSWORD:
                bot.send_message(message.chat.id, '`<- Now you are root ->`', reply_markup=markup, parse_mode='MarkdownV2')
                answer = ''
            else: 
                bot.send_message(message.chat.id, '`' + CreateQuery(connection,message.text) + '`', parse_mode='MarkdownV2')    
                answer = ''    

def Main_menu(message):
    global menu_item
    global handler_item
    global elems
    global temp
    global answer

    if message.text.strip() == 'Адміністрування' :
        if CreateQuery(connection,"SELECT EXISTS(SELECT visitor_id FROM visitor WHERE chat_id = %s AND is_root = TRUE)", (message.chat.id,)):                
            menu_item = 'Root'
            markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1=types.KeyboardButton("Додати виставу")
            item2=types.KeyboardButton("Додати співробітника")
            item3=types.KeyboardButton("Змінити виставу")
            item4=types.KeyboardButton("Звільнити співробітника")
            item6=types.KeyboardButton("<- Назад")
            markup.add(item1, item2)
            markup.add(item3, item4)
            markup.row(item6)
            bot.send_message(message.chat.id, '`<- Now you are root ->`', reply_markup=markup, parse_mode='MarkdownV2')
            answer = ''
        else :
            menu_item = 'Root'
            answer = 'Введите пароль'
    elif message.text.strip() == 'Афіша' :
        bot.send_message(message.chat.id, '`' + CreateQuery(connection,"SELECT performance.perf_name as 'Вистава',theatre.theatre_name as 'Театри' FROM  performance, theatre, performance_theatre WHERE performance_theatre.perf_id = performance.perf_id AND performance_theatre.theatre_id = theatre.theatre_id") + '`', parse_mode='MarkdownV2')  
    elif message.text.strip() == 'Написати відгук' :
        menu_item = 'Review'
        markup = telebot.types.InlineKeyboardMarkup()
        elems = CreateQuery(connection,"SELECT perf_name FROM performance, ticket, visitor WHERE performance.perf_id = ticket.perf_id AND ticket.visitor_id = visitor.visitor_id AND visitor.chat_id = %s  group by perf_name", (message.chat.id,), False)
        i = 1
        for elem in elems:
            markup.add(telebot.types.InlineKeyboardButton(text=elem, callback_data=i))
            i+=1
        handler_item = 'Perf'
        bot.send_message(message.chat.id, text="Оберіть виставу, яку ви відвідали", reply_markup=markup)

def handle_message(message):
    global menu_item
    global handler_item
    global elems
    global temp
    global answer

    if message.chat.type == 'private':
        if menu_item == 'Name':
            CreateQuery(connection,"UPDATE visitor SET visitor_name = %s WHERE chat_id = %s", (message.text, message.chat.id))
            menu_item = 'Main'
        
        if menu_item == 'Main' and handler_item == 'Review_OK': 
            menu_item = '***'
            answer = 'Напишіть відгук'  

        if menu_item == '***' and handler_item == 'Review_OK': 
            handler_item = ''
            menu_item = 'Main'
            answer = 'Дякуємо за відгук!'  
            print(temp)
            CreateQuery(connection,"INSERT INTO review (ticket_id, review_content) VALUES (%s, %s)", (temp, message.text))

        elif menu_item == 'Phone':
            CreateQuery(connection,"UPDATE visitor SET phone = %s WHERE chat_id = %s", (message.text, message.chat.id))
            menu_item = 'Perf'
        
            
        if menu_item == 'Add_Perf':
            CreateQuery(connection,"INSERT INTO performance (perf_name, duration, number_of_parts) VALUES (%s, NULL, NULL)", (message.text,))
            temp = CreateQuery(connection,"SELECT perf_id FROM performance WHERE perf_name = %s", (message.text,), False)[0]
            menu_item ='Add_Perf_Theatre'
            answer = 'Введіть тривалість выстави'
        elif menu_item == 'Add_Perf_Theatre' or menu_item == 'Edit_Perf_Duration':
            CreateQuery(connection,"UPDATE performance SET duration = %s WHERE perf_id = %s", (message.text, temp))            
            if menu_item == 'Add_Perf_Theatre':
                menu_item ='Add_Perf_Part'
                answer = 'Введіть кількість частин'
            else:
                bot.send_message(message.chat.id,'Тривалість змінено')
                menu_item ='Edit_Perf_OK'
            
        elif menu_item == 'Add_Perf_Part':
            CreateQuery(connection,"UPDATE performance SET number_of_parts = %s WHERE perf_id = %s", (message.text, temp))
            menu_item ='Add_Perf_OK'
            bot.send_message(message.chat.id,'Виставу додано')
        elif menu_item == 'Edit_Perf_Name':
            CreateQuery(connection,"UPDATE performance SET perf_name = %s WHERE perf_id = %s", (message.text, temp))
            menu_item ='Edit_Perf_OK'
            bot.send_message(message.chat.id,'Назву змінено')
        elif menu_item == 'Add_Perf_Person' or menu_item == 'Edit_Perf_Person':
            CreateQuery(connection,"INSERT INTO personage (perf_id, name, significance) VALUES (%s, %s, %s)", (temp, message.text, 'main'))
            bot.send_message(message.chat.id,'Персонажа додано')
            if menu_item == 'Add_Perf_Person':
                menu_item ='Add_Perf_OK'
            else:
                menu_item ='Edit_Perf_OK'
        elif menu_item == 'Add_Perf_Theatre' or menu_item == 'Edit_Perf_Theatre':
            CreateQuery(connection,"INSERT INTO performance_theatre (perf_id, theatre_id) VALUES (%s, %s)", (temp, CreateQuery(connection,"SELECT theatre_id FROM theatre WHERE theatre_name = %s", (message.text,), False)[0]))
            bot.send_message(message.chat.id,'Театр додано')
            if menu_item == 'Add_Perf_Theatre':
                menu_item ='Add_Perf_OK'
            else:
                menu_item ='Edit_Perf_OK'
        
        if menu_item == 'Edit_Perf_OK':
            if message.text.strip() == 'Додати персонажа' :
                menu_item ='Edit_Perf_Person'
                answer = "Введіть ім'я персонажа"
            elif message.text.strip() == 'Додати театр' :
                handler_item = 'Edit_Perf_Theatre'
                markup = telebot.types.InlineKeyboardMarkup()
                elems = CreateQuery(connection,"SELECT theatre_name FROM theatre", None, False)
                i = 1
                for elem in elems:
                    markup.add(telebot.types.InlineKeyboardButton(text=elem, callback_data=i))
                    i+=1
                bot.send_message(message.chat.id, text="Оберіть назву театру", reply_markup=markup)
            elif message.text.strip() == 'Змінити назву' :
                menu_item ='Edit_Perf_Name'
                answer = "Введіть нову назву вистави"
            elif message.text.strip() == 'Змінити тривалість' :
                menu_item ='Edit_Perf_Duration'
                answer = "Введіть нову тривалість вистави"
            elif message.text.strip() == 'Видалити' :
                CreateQuery(connection,"DELETE FROM performance WHERE perf_id = %s", (temp,))
                menu_item ='Main'
                answer = "Виставу видалено"
            elif message.text.strip() == '<- Назад' :
                menu_item ='Root'
                markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
                item1=types.KeyboardButton("Додати виставу")
                item2=types.KeyboardButton("Додати співробітника")
                item3=types.KeyboardButton("Змінити виставу")
                item4=types.KeyboardButton("Звільнити співробітника")
                item6=types.KeyboardButton("<- Назад")
                markup.add(item1, item2)
                markup.add(item3, item4)
                markup.row(item6)
                bot.send_message(message.chat.id,'Назад до консолі керування', reply_markup=markup)
                message.text = 'Адміністрування'
            else:
                markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
                item4=types.KeyboardButton("Змінити назву")
                item5=types.KeyboardButton("Змінити тривалість")
                item1=types.KeyboardButton("Додати персонажа")
                item2=types.KeyboardButton("Додати театр")
                item3=types.KeyboardButton("<- Назад")
                markup.add(item4, item5)
                markup.add(item1, item2)
                markup.row(item3)
                bot.send_message(message.chat.id,'Виберіть дію', reply_markup=markup)
        
        if menu_item == 'Add_Perf_OK':
            if message.text.strip() == 'Додати персонажа' :
                menu_item ='Add_Perf_Person'
                answer = "Введіть ім'я персонажа"
            elif message.text.strip() == 'Додати театр' :
                handler_item = 'Edit_Perf_Theatre'
                markup = telebot.types.InlineKeyboardMarkup()
                elems = CreateQuery(connection,"SELECT theatre_name FROM theatre", None, False)
                i = 1
                for elem in elems:
                    markup.add(telebot.types.InlineKeyboardButton(text=elem, callback_data=i))
                    i+=1
                bot.send_message(message.chat.id, text="Оберіть назву театру", reply_markup=markup)
            elif message.text.strip() == '<- Назад' :
                menu_item ='Root'
                markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
                item1=types.KeyboardButton("Додати виставу")
                item2=types.KeyboardButton("Додати співробітника")
                item3=types.KeyboardButton("Змінити виставу")
                item4=types.KeyboardButton("Звільнити співробітника")
                item6=types.KeyboardButton("<- Назад")
                markup.add(item1, item2)
                markup.add(item3, item4)
                markup.row(item6)
                bot.send_message(message.chat.id,'Назад до консолі керування', reply_markup=markup)
                message.text = 'Адміністрування'
            else:
                markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
                item1=types.KeyboardButton("Додати персонажа")
                item2=types.KeyboardButton("Додати театр")
                item3=types.KeyboardButton("<- Назад")
                markup.add(item1, item2)
                markup.row(item3)
                bot.send_message(message.chat.id,'Виберіть дію', reply_markup=markup)
        


        if menu_item == 'Root':
            Root_menu(message)

        if menu_item == 'Main':  
            Main_menu(message)      
            
        if answer != '':
            bot.send_message(message.chat.id, answer)

@bot.message_handler(commands=["start"])
def start_message(message):
    handle_start_message(message)


@bot.callback_query_handler(func=lambda call: True)    
def query_handler(call):
    handle_query(call)


@bot.message_handler(content_types=["text"])
def handle_text(message):
    handle_message(message)
            

bot.polling(none_stop=True, interval=0)