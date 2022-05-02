def handle_message(message):
    global menu_item
    global handler_item
    global elems
    global temp
    answer = ''

    from root import Root_menu
    from main import Main_menu
    
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
                elems = CreateQuery(connection,"SELECT theatre_name FROM theatre, performance_theatre WHERE performance_theatre.perf_id = %s AND performance_theatre.theatre_id = theatre.theatre_id group by theatre_name;", (message.chat.id,), False)
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
                print(temp)
                elems = CreateQuery(connection,"SELECT theatre_name FROM theatre", None, False)
                print(elems)
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
            Root_menu()

        if menu_item == 'Main':  
            Main_menu()      
            
        if answer != '':
            bot.send_message(message.chat.id, answer)