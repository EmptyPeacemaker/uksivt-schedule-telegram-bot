import telebot
from telebot import types

bot = telebot.TeleBot("5752620985:AAHJD-DldTcy0ZfAgJoixYUinkgUAV5gfvc", parse_mode=None)


@bot.message_handler(commands=['start'])
def start_work(message):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    markup.add(
        types.KeyboardButton('Группа')
    )
    bot.reply_to(message, "Добрый день, выберите тип подписки", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "Группа")
def foo(message):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    markup.add(
        types.KeyboardButton('19П-1'),
        types.KeyboardButton('19П-2')
    )
    bot.reply_to(message, "Выберите группу", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "19П-1" or message.text == "19П-2")
def foo(message):
    bot.reply_to(message, "Вы успешно подписались")



bot.polling(none_stop=True)
