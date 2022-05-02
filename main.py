def Main_menu():
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