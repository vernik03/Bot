def Root_menu():
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