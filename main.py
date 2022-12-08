import logging
from os import getenv

import telebot
from telebot import types

logger = logging.Logger("main")

bot = telebot.TeleBot(getenv("TG_KEY"), parse_mode=None)


@bot.message_handler(commands=['start'])
def start_work(message):
    logger.info("the bot is running")
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


if __name__ == '__main__':
    bot.polling(none_stop=True)
