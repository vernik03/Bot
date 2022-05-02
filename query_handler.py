def handle_query(call):
    global menu_item
    global handler_item
    global elems
    global temp
    if handler_item == 'Perf':
        #bot.answer_callback_query(callback_query_id=call.id)
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