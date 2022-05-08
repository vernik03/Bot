from asyncio.windows_events import NULL
import telebot
import mysql.connector
from mysql.connector import Error
from telebot import types
from prettytable import PrettyTable, from_db_cursor
from datetime import date

from KEYS import *

# from yattag import Doc

# doc, tag, text = Doc().tagtext()

# with tag('html'):
#     with tag('body'):
#         with tag('p', id = 'main'):
#             text('some text')
#         with tag('a', href='/my-url'):
#             text('some link')

# result = doc.getvalue()

logfile = open('log.txt', 'w')
logfile.close()

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
    logfile = open('log.txt', 'a')
    logfile.write(query + ';' + '\n')
    logfile.close()
    cursor = connection.cursor()
    mytable = PrettyTable()
    try:
        if parameter is None:
            cursor.execute(query)
            
        else:
            cursor.execute(query, parameter)    
            if not is_str:          
                x = cursor.fetchall()
                if x == []:
                    return None
                if x[0][0] == 0 or x[0][0] == 1:
                    return x[0][0]

        
        if is_str:            
            mytable = from_db_cursor(cursor)
            if mytable == None:
                return None
            mytable.align='l'
            return str(mytable)
        else:
            if parameter is None:
                res = cursor.fetchall()
                res = [ i[0] for i in res ]
                return res
            else:
                x = [ i[0] for i in x ]
                return x

        
    except Error as e :
        print(f"The error '{e}' occurred")

def Make_Main():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1=types.KeyboardButton("Купити квиток")
    item2=types.KeyboardButton("Афіша")
    item4=types.KeyboardButton("Написати відгук")
    item3=types.KeyboardButton("Адміністрування")
    item5=types.KeyboardButton("Мої квитки")
    markup.add(item2, item5)
    markup.add(item1, item4)
    markup.row(item3)
    return markup

def Make_Root():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1=types.KeyboardButton("Додати виставу")
    item2=types.KeyboardButton("Додати співробітника")
    item3=types.KeyboardButton("Змінити виставу")
    item4=types.KeyboardButton("Звільнити співробітника")
    item6=types.KeyboardButton("<- Назад")
    markup.add(item1, item2)
    markup.add(item3, item4)
    markup.row(item6)
    return markup

def Make_Add_Perf():
    markup= types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1=types.KeyboardButton("Додати персонажа")
    item2=types.KeyboardButton("Додати театр")
    item3=types.KeyboardButton("<- Назад")
    markup.add(item1, item2)
    markup.row(item3)
    return markup

def Make_Edit_Perf():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item4=types.KeyboardButton("Змінити назву")
    item5=types.KeyboardButton("Змінити тривалість")
    item1=types.KeyboardButton("Додати персонажа")
    item2=types.KeyboardButton("Додати театр")
    item3=types.KeyboardButton("<- Назад")
    markup.add(item4, item5)
    markup.add(item1, item2)
    markup.row(item3)
    return markup

def handle_start_message(message):
    markup=Make_Main()
    bot.send_message(message.chat.id,'Оберіть дію', reply_markup=markup)
    if not CreateQuery(connection,"SELECT EXISTS(SELECT visitor_id FROM visitor WHERE chat_id = %s)", (message.chat.id,)):  
        CreateQuery(connection,"INSERT INTO visitor (visitor_name, phone, chat_id, is_root) VALUES (NULL, NULL, %s, FALSE)", (message.chat.id,))

def query_markup(message, input_query, input_text):
    global menu_item, handler_item, elems, temp, answer
    markup = telebot.types.InlineKeyboardMarkup()
    elems = CreateQuery(connection,input_query, None, False)
    i = 1
    for elem in elems:
        markup.add(telebot.types.InlineKeyboardButton(text=elem, callback_data=i))
        i+=1
    bot.send_message(message.chat.id, text=input_text, reply_markup=markup)


def handle_query(call):
    global menu_item, handler_item, elems, temp, answer

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
        markup=Make_Edit_Perf()
        bot.send_message(call.from_user.id,'Виберіть дію', reply_markup=markup)
        handler_item = ' '


    elif handler_item == 'Edit_Perf_Theatre':
        CreateQuery(connection,"INSERT INTO performance_theatre (perf_id, theatre_id) VALUES (%s, %s)", (temp, CreateQuery(connection,"SELECT theatre_id FROM theatre WHERE theatre_name = %s", (elems[int(call.data)-1],), False)[0]))
        bot.send_message(call.from_user.id, "Театр додано")
        handler_item = ' '

    elif handler_item == 'Add_Staff':
        temp = CreateQuery(connection,"SELECT theatre_id FROM theatre WHERE theatre_name = %s", (elems[int(call.data)-1],), False)
        if temp != 1:
            temp = temp[0]
        bot.send_message(call.from_user.id, "Введіть прізвище та ім'я співробітника")
        handler_item = ' '

    elif handler_item == 'Delete_Staff':
        temp = CreateQuery(connection,"SELECT theatre_id FROM theatre WHERE theatre_name = %s", (elems[int(call.data)-1],), False)[0]
        markup = telebot.types.InlineKeyboardMarkup()
        elems = CreateQuery(connection,"SELECT staff_name FROM staff WHERE theatre_id = %s", (temp,), False)
        i = 1
        for elem in elems:
            markup.add(telebot.types.InlineKeyboardButton(text=elem, callback_data=i))
            i+=1
        bot.send_message(call.from_user.id, "Оберіть прізвище та ім'я співробітника", reply_markup=markup)
        handler_item = 'Delete_Staff_ID'

    elif handler_item == 'Delete_Staff_ID':
        temp = CreateQuery(connection,"SELECT staff_id FROM staff WHERE staff_name = %s", (elems[int(call.data)-1],), False)[0]
        CreateQuery(connection,"DELETE FROM staff WHERE staff_id = %s", (temp,))
        bot.send_message(call.from_user.id, "Співробітника звільнено")
        handler_item = ' '
        menu_item = 'Root'

    elif handler_item == 'Poster':
        temp = CreateQuery(connection,"SELECT theatre_id FROM theatre WHERE theatre_name = %s", (elems[int(call.data)-1],), False)
        if temp != 1:
            temp = temp[0]
        if CreateQuery(connection,"SELECT EXISTS(SELECT performance.perf_name as 'Вистава',theatre.theatre_name as 'Театри' FROM  performance, theatre, performance_theatre WHERE performance_theatre.perf_id = performance.perf_id AND performance_theatre.theatre_id = theatre.theatre_id AND theatre.theatre_id = %s)", (temp,), False):  
            bot.send_message(call.from_user.id, '`' + CreateQuery(connection,"SELECT performance.perf_name as 'Вистава',theatre.theatre_name as 'Театри' FROM  performance, theatre, performance_theatre WHERE performance_theatre.perf_id = performance.perf_id AND performance_theatre.theatre_id = theatre.theatre_id AND theatre.theatre_id = %s",(temp,)) + '`', parse_mode='MarkdownV2')  
        else:
            bot.send_message(call.from_user.id, "На даний момент немає вистав в цьому театрі")

    elif handler_item == 'Buy_Ticket_Theatre':
        temp = CreateQuery(connection,"SELECT theatre_id FROM theatre WHERE theatre_name = %s", (elems[int(call.data)-1],), False)
        if temp != 1:
            temp = temp[0]
        markup = telebot.types.InlineKeyboardMarkup()
        
        CreateQuery(connection,"INSERT INTO ticket (visitor_id, theatre_id, perf_id, price, place_number, perf_date, start_time) VALUES (%s, %s, NULL, 200, NULL, %s, '18:00:00')", (CreateQuery(connection,"SELECT visitor_id FROM visitor WHERE chat_id = %s", (call.from_user.id,), False)[0], temp, date.today()))
        elems = CreateQuery(connection,"SELECT perf_name FROM performance, performance_theatre, theatre WHERE performance.perf_id = performance_theatre.perf_id AND performance_theatre.theatre_id = theatre.theatre_id AND theatre.theatre_id = %s  group by perf_name", (temp,), False)
        temp = CreateQuery(connection,"SELECT MAX(ticket_id) FROM ticket", None, False)[0]
        
        i = 1
        for elem in elems:
            markup.add(telebot.types.InlineKeyboardButton(text=elem, callback_data=i))
            i+=1
        bot.send_message(call.from_user.id, text="Оберіть виставу", reply_markup=markup)
        handler_item = 'Buy_Ticket_Row'

    elif handler_item == 'Buy_Ticket_Row':
        perf_id_temp = CreateQuery(connection,"SELECT perf_id FROM performance WHERE perf_name = %s", (elems[int(call.data)-1],), False)[0]
        CreateQuery(connection,"UPDATE ticket SET perf_id = %s WHERE ticket_id = %s", (perf_id_temp, temp))       
        bot.send_photo(call.from_user.id, 'https://vernik03.ml/host_images/gladacka-zala.png')
        bot.send_message(call.from_user.id, "Введіть номер ряду:")
        menu_item = 'Buy_Ticket_Place'


def Root_menu(message):
    global menu_item, handler_item, elems, temp, answer

    if message.text.strip() == '<- Назад':
        menu_item = 'Main'
        markup=Make_Main()
        bot.send_message(message.chat.id,'Назад до головного меню', reply_markup=markup)
    elif message.text.strip() == 'Додати виставу' :
        menu_item = 'Add_Perf'
        answer = 'Введіть назву вистави'
    elif message.text.strip() == 'Додати співробітника' :
        query_markup(message, "SELECT theatre_name FROM theatre", "Оберіть назву театру")
        menu_item = 'Add_Staff_Position'
        handler_item = 'Add_Staff'
    elif message.text.strip() == 'Звільнити співробітника' :
        query_markup(message, "SELECT theatre_name FROM theatre", "Оберіть назву театру")
        menu_item = 'Delete_Staff_OK'
        handler_item = 'Delete_Staff'
    elif message.text.strip() == 'Змінити виставу' :
        menu_item = 'Edit_Perf'    
        handler_item = 'Edit_Perf'
        query_markup(message, "SELECT perf_name FROM performance", "Оберіть назву вистави")
    else :
        if message.text.strip() == PASSWORD :
            CreateQuery(connection,"SET SQL_SAFE_UPDATES = 0")
            CreateQuery(connection,"UPDATE visitor SET is_root = TRUE WHERE chat_id = %s", (message.chat.id,))
        elif message.text.strip() != PASSWORD and CreateQuery(connection,"SELECT EXISTS(SELECT visitor_id FROM visitor WHERE chat_id = %s AND is_root = FALSE)", (message.chat.id,), False) :
            menu_item = 'Main'
            markup=Make_Main()
            bot.send_message(message.chat.id,'Невірный пароль', reply_markup=markup) 

        if CreateQuery(connection,"SELECT EXISTS(SELECT visitor_id FROM visitor WHERE chat_id = %s)", (message.chat.id,)):
            markup=Make_Root()
            if message.text.strip() == 'Адміністрування' or message.text.strip() == PASSWORD:
                bot.send_message(message.chat.id, '`<- Now you are root ->`', reply_markup=markup, parse_mode='MarkdownV2')
                answer = ''
            elif message.text.strip() != 'Back': 
                bot.send_message(message.chat.id, '`' + CreateQuery(connection,message.text) + '`', parse_mode='MarkdownV2')    
                answer = ''  
            else:
                answer = '' 

def Main_menu(message):
    global menu_item, handler_item, elems, temp, answer

    if message.text.strip() == 'Адміністрування' :
        if CreateQuery(connection,"SELECT EXISTS(SELECT visitor_id FROM visitor WHERE chat_id = %s AND is_root = TRUE)", (message.chat.id,)):                
            menu_item = 'Root'
            markup=Make_Root()
            bot.send_message(message.chat.id, '`<- Now you are root ->`', reply_markup=markup, parse_mode='MarkdownV2')
            answer = ''
        else :
            menu_item = 'Root'
            answer = 'Введите пароль'
    elif message.text.strip() == 'Афіша' :
        query_markup(message, "SELECT theatre_name FROM theatre", "Оберіть назву театру")
        handler_item = 'Poster'
    elif message.text.strip() == 'Купити квиток' :
        query_markup(message, "SELECT theatre_name FROM theatre", "Оберіть назву театру")
        handler_item = 'Buy_Ticket_Theatre'
        menu_item = 'Buy_Ticket'
    elif message.text.strip() == 'Мої квитки' :
        temp = CreateQuery(connection,"SELECT visitor_id FROM visitor WHERE chat_id = %s", (message.chat.id,), False)[0]
        bot.send_message(message.chat.id, '`' + CreateQuery(connection,"SELECT * FROM ticket WHERE visitor_id = %s",(temp,)) + '`', parse_mode='MarkdownV2')  
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
    global menu_item, handler_item, elems, temp, answer

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
        
        if menu_item == 'Add_Staff_Position':
            CreateQuery(connection,"SET foreign_key_checks = 0",None)
            CreateQuery(connection,"INSERT INTO staff (staff_name, theatre_id, position, hirirng_date) VALUES (%s, %s, Null, %s)", (message.text, temp, date.today()))
            temp = CreateQuery(connection,"SELECT staff_id FROM staff WHERE staff_name = %s", (message.text,), False)[0]
            bot.send_message(message.chat.id,'Введіть посаду співробітника')
            menu_item = 'Add_Staff_Salary'
        elif menu_item == 'Add_Staff_Salary':            
            CreateQuery(connection,"UPDATE staff SET position = %s WHERE staff_id = %s", (message.text, temp))
            bot.send_message(message.chat.id,'Введіть заробітну плату співробітника')
            menu_item = 'Add_Staff_OK'
        elif menu_item == 'Add_Staff_OK':
            CreateQuery(connection,"INSERT INTO salary (staff_id, salary) VALUES (%s, %s)", (temp, message.text))
            CreateQuery(connection,"SET foreign_key_checks = 1",None)
            bot.send_message(message.chat.id,'Співробітника додано')
            menu_item ='Root'
            return
        elif menu_item == 'Buy_Ticket_Place' :
            CreateQuery(connection,"UPDATE ticket SET row_num = %s WHERE ticket_id = %s", (int(message.text.strip()), temp))       
            bot.send_message(message.chat.id,'Введіть номер місця')
            menu_item = 'Buy_Ticket_OK'
        elif menu_item == 'Buy_Ticket_OK' :
            CreateQuery(connection,"UPDATE ticket SET place_number = %s WHERE ticket_id = %s", (int(message.text.strip()), temp))       
            bot.send_message(message.chat.id,'Ваш квиток додано до бази даних театру (візуальна версія у розробці)')
            menu_item = 'Main'
            handler_item = ' '
            
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
                query_markup(message, "SELECT theatre_name FROM theatre", "Оберіть назву театру")
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
                markup=Make_Root()
                bot.send_message(message.chat.id,'Назад до консолі керування', reply_markup=markup)
                message.text = 'Back'
            else:
                markup=Make_Edit_Perf()
                bot.send_message(message.chat.id,'Виберіть дію', reply_markup=markup)
        
        if menu_item == 'Add_Perf_OK':
            if message.text.strip() == 'Додати персонажа' :
                menu_item ='Add_Perf_Person'
                answer = "Введіть ім'я персонажа"
            elif message.text.strip() == 'Додати театр' :
                handler_item = 'Edit_Perf_Theatre'
                query_markup(message, "SELECT theatre_name FROM theatre", "Оберіть назву театру")
            elif message.text.strip() == '<- Назад' :
                menu_item ='Root'
                markup=Make_Root()
                bot.send_message(message.chat.id,'Назад до консолі керування', reply_markup=markup)
                message.text = 'Back'
            else:
                markup=Make_Add_Perf()
                bot.send_message(message.chat.id,'Оберіть дію', reply_markup=markup)

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