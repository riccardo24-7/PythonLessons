import telebot
from telebot import types
import requests
from collections import Counter
from re import findall, sub
import operator
import nltk

nltk.download('averaged_perceptron_tagger_ru')
bot = telebot.TeleBot('')

# function will be activate after user writes /start
@bot.message_handler(commands=['start'])
def start_bot(message):
	bot.send_message(message.from_user.id, "Привет " + message.from_user.first_name + "!" + " Напиши /choose")

# function will be activate after user writes /choose
@bot.message_handler(commands=['choose'])
def get_choise(message):
    if message.text == "/choose":
        markup_choose = types.ReplyKeyboardMarkup(row_width=2)
        btn_web = types.KeyboardButton("Проверь сайт")
        btn_string = types.KeyboardButton('Проверь предложение')
        btn_calc = types.KeyboardButton('Калькулятор')
        markup_choose.add(btn_web, btn_string, btn_calc)
        bot.send_message(message.chat.id, "Выбери действие:", reply_markup=markup_choose) 
        
        
@bot.message_handler(content_types=['text'])
def get_text_message(message):
    
    if message.text == "Привет":
        bot.send_message(message.from_user.id, "Привет " + message.from_user.first_name + "!" + " Напиши /choose")
             
    elif message.text == "Проверь сайт":
        
        keyboard_web = types.InlineKeyboardMarkup()
        key_google = types.InlineKeyboardButton(text='Google', callback_data='google')
        key_yandex = types.InlineKeyboardButton(text='Yandex', callback_data='yandex')
        key_yahoo = types.InlineKeyboardButton(text='Yahoo', callback_data='yahoo')
        keyboard_web.add(key_google, key_yandex, key_yahoo)
        bot.send_message(message.from_user.id, text='Пока я могу проверить только 3 сайта, выбирай', reply_markup=keyboard_web) 
              
    elif message.text == "Проверь предложение":
        
        msg = bot.send_message(message.from_user.id, "Введите предложение для анализа, либо отмена")
        bot.register_next_step_handler(msg, string_parsing)
        
    elif message.text == "Калькулятор":
        markup_calc = types.ReplyKeyboardRemove(selective=True)
        msg = bot.send_message(message.chat.id, "Введи два числа через пробел, либо отмена ", reply_markup=markup_calc)
        bot.register_next_step_handler(msg, calculator_activate)
        
    else:
        bot.send_message(message.from_user.id, "Неизвестная компанда, введи /help")

# Парсер строки, для создания статистики о введенном предложении
def string_parsing(message):
    
    # Введенная строка пользователем
    user_string = message.text.lower()
    
    if user_string == 'отмена':
        
        bot.send_message(message.from_user.id, 'Как хочешь, я хотел помочь...')
        return
    
    else:
        
        # Сначала сделаем строку без союзов, предлогов и частицы
        words = nltk.word_tokenize(user_string)
        functors_pos = {'CONJ', 'PR', 'PART'}
        without_functors_string = [word for word, pos in nltk.pos_tag(words, lang='rus') if pos not in functors_pos]

        # Фильтруем строку, соединяем список
        filtered_string = ' '.join(without_functors_string)
        # sub - заменяет все совпадения на определенный элемент в данном случае ''
        # проверка идет по не включению любого пробела и любой символ
        final_string = sub(r'[^\w\s]','', filtered_string)
        
        token_words = final_string.split()
        token_dict = dict(Counter(token_words))
        
        most_occur_word = max(token_dict.items(), key = operator.itemgetter(1))[0]
        max_len_key = max(findall(r"\b\w+\b", final_string), key = len)
        
        statistic = f'''Статистика предложения (без предлогов, союзов и знаков препинания)
        Длина предложения: {len(token_words)} слов
        Количество каждого слова: 
        {token_dict}
        Самое частое слово: {most_occur_word}
        Самое длинное слово: {max_len_key}''' 
        
        bot.send_message(message.from_user.id, statistic)

# Дальше идет раздел для калькулятора сначала просто активируется клавиатура для выбора действия
def calculator_activate(message):
    
    global user_num
    user_num = message.text.lower()
    
    if user_num == 'отмена':
        bot.send_message(message.from_user.id, 'Как хочешь, я хотел помочь...')
        return
    else:
        
        markup_calc = types.ReplyKeyboardMarkup(row_width=2)
        btn_sum = types.KeyboardButton("Сложить")
        btn_minus = types.KeyboardButton('Отнять')
        btn_multiply = types.KeyboardButton('Умножить')
        btn_divide = types.KeyboardButton('Делить')
        markup_calc.add(btn_sum, btn_minus, btn_multiply, btn_divide)

        msg = bot.send_message(message.chat.id, " Выбери действие:", reply_markup=markup_calc)
        bot.register_next_step_handler(msg, calculator_operations)

# Далее опредееление операции      
def calculator_operations(message): 
     
    user_numbers = message.text
    
    count_list = user_num.split()
    
    if user_numbers == "Сложить":
        result = int(count_list[0]) + int(count_list[1])
        bot.send_message(message.from_user.id, "Результат сложения: " + str(result))
        
    elif user_numbers == "Отнять":
        result = int(count_list[0]) - int(count_list[1])
        bot.send_message(message.from_user.id, "Результат разности: " + str(result))
        
    elif user_numbers == "Умножить":
        result = int(count_list[0]) * int(count_list[1])
        bot.send_message(message.from_user.id, "Результат умножения: " + str(result))
        
    elif user_numbers == "Делить":
        if int(count_list[1]) != 0:     
            result = round(int(count_list[0]) / int(count_list[1]),2)
            bot.send_message(message.from_user.id, "Результат деления: " + str(result))
            
        else:
            bot.send_message(message.from_user.id, "Не ломай мне бота")
            
    markup_calc = types.ReplyKeyboardRemove(selective=True)
    msg = bot.send_message(message.chat.id, "Введи два числа через пробел: ", reply_markup=markup_calc)
    bot.register_next_step_handler(msg, calculator_activate)          

@bot.callback_query_handler(func=lambda call: True)
def callbackFunction(call):
    
    if call.data == "google": 
        r = requests.get('https://www.google.ru')
        if r.status_code == 200:   
            bot.send_message(call.message.chat.id, "Сайт google доступен")
        else:
            bot.send_message(call.message.chat.id, "Сайт не доступен")
    elif call.data == "yandex":
        r = requests.get('https://www.yandex.ru')
        if r.status_code == 200:   
            bot.send_message(call.message.chat.id, "Сайт yandex доступен")
        else:
            bot.send_message(call.message.chat.id, "Сайт не доступен")
    elif call.data == "yahoo":
        r = requests.get('https://www.yahoo.com')
        if r.status_code == 200:   
            bot.send_message(call.message.chat.id, "Сайт yahoo доступен")
        else:
            bot.send_message(call.message.chat.id, "Сайт не доступен")
    else:
        bot.send_message(call.message.chat.id, "Какая-то ошибка") 

bot.polling(none_stop=True, interval=0)



