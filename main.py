import logging
from os import getenv

import telebot
from telebot import types

logger = logging.Logger("main")

bot = telebot.TeleBot(getenv("TG_KEY"), parse_mode=None)

user_status = {}

GROUPS = requests.get('https://back.uksivt.com/api/v1/college_group').json()
TEACHERS = requests.get('https://back.uksivt.com/api/v1/teacher').json()


def status__set_select_subscription(user_id, text="На какое расписание хотите подписаться?"):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    markup.add(
        types.KeyboardButton('Группа'),
        types.KeyboardButton('Преподователь')
    )
    bot.send_message(user_id, text, reply_markup=markup)
    user_status[user_id]['status'] = "select_subscription"


def status__get_select_subscription(text, user_id):
    if text == 'Группа':
        status__set_select_subscription__group(user_id)
    elif text == 'Преподователь':
        status__set_select_subscription__teacher(user_id)
    elif text == 'Кабинет':
        pass
    else:
        status__set_select_subscription(user_id, "Выберите кнопку")


def status__set_select_subscription__group(user_id, text="Напишите название группы, например 19П-1"):
    bot.send_message(user_id, text)
    user_status[user_id]['status'] = "select_subscription__group"
    user_status[user_id]['subscription']['type'] = 'college_group'


def status__get_select_subscription__group(text, user_id):
    if text in GROUPS:
        user_status[user_id]['subscription']['value'] = text
        status__set_menu(user_id, "Подписка оформленна")
    else:
        status__set_select_subscription__group(user_id, "Не удалось найти совпадение, попробуйте еще раз")


def status__set_select_subscription__teacher(user_id, text="Напишите ФИО преподователя, например Каримова Р Ф"):
    bot.send_message(user_id, text)
    user_status[user_id]['status'] = "select_subscription__teacher"
    user_status[user_id]['subscription']['type'] = 'teacher'


def status__get_select_subscription__teacher(text, user_id):
    if text in TEACHERS:
        user_status[user_id]['subscription']['value'] = text
        status__set_menu(user_id, "Подписка оформленна")
    else:
        status__set_select_subscription__teacher(user_id, "Не удалось найти совпадение, попробуйте еще раз")


def status__set_menu(user_id, text="Используйте кнопки для навигации"):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    markup.add(types.KeyboardButton('Расписание'))
    if user_status[user_id].get('subscription', {}).get('type') is None:
        markup.add(types.KeyboardButton('Подписаться'))
    else:
        markup.add(
            types.KeyboardButton('Переподписаться'),
            types.KeyboardButton('Отменить подписку')
        )
    bot.send_message(user_id, text, reply_markup=markup)
    user_status[user_id]['status'] = "menu"


def status__get_menu(text, user_id):
    if text == 'Расписание':
        status__set_timetable(user_id)
    elif text == 'Подписаться' or text == 'Переподписаться':
        status__set_select_subscription(user_id)
    elif text == 'Отменить подписку':
        user_status[user_id]['subscription'] = {
            'type': None,
            'value': None
        }
        status__set_menu(user_id, 'Подписка отменена')
    else:
        status__set_menu(user_id)


def status__set_timetable(user_id, text="Чье рассписание показать?"):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    markup.add(
        types.KeyboardButton('Группы'),
        types.KeyboardButton('Преподователя'),
        # types.KeyboardButton('Кабинета')
    )
    bot.send_message(user_id, text, reply_markup=markup)
    user_status[user_id]['status'] = "timetable"


def status__get_timetable(text, user_id):
    if text == 'Группы':
        user_status[user_id]['timetable']['type'] = 'college_group'
        status__set_timetable__select(user_id)
    elif text == 'Преподователя':
        user_status[user_id]['timetable']['type'] = 'teacher'
        status__set_timetable__select(user_id)
    elif text == 'Кабинета':
        pass
    else:
        status__set_timetable(user_id)


def status__set_timetable__select(user_id, text=""):
    status = user_status[user_id].get('timetable', {}).get('type')
    if text == "":
        if status == 'college_group':
            text = "Напишите название группы, например 19П-1"
        elif status == 'teacher':
            text = "Напишите ФИО преподователя, например Каримова Р Ф"

    bot.send_message(user_id, text)
    user_status[user_id]['status'] = "timetable_select"


def status__get_timetable__select(text, user_id):
    status = user_status[user_id].get('timetable', {}).get('type')
    if status == "college_group" and text in GROUPS or status == "teacher" and text in TEACHERS:
        user_status[user_id]['timetable']['value'] = text
        status__set_timetable__day(user_id)
    else:
        status__set_timetable__select(user_id, "Нечего не найденно, введите еще раз")


def status__set_timetable__day(user_id, text="Выберите тип рассписания"):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    markup.add(
        types.KeyboardButton('На сегодня'),
        types.KeyboardButton('На завтра'),
        types.KeyboardButton('На день X'),
        types.KeyboardButton('На диапазон')
    )
    bot.send_message(user_id, text, reply_markup=markup)
    user_status[user_id]['status'] = "timetable_day"


def status__get_timetable__day(text, user_id):
    if text == 'На сегодня':
        user_status[user_id]['timetable']['day'] = 'now'
        show_timetable(user_id)
    elif text == 'На завтра':
        user_status[user_id]['timetable']['day'] = 'tomorrow'
        show_timetable(user_id)
    elif text == 'На день X':
        user_status[user_id]['timetable']['day'] = 'day_x'
        status__get_timetable__day_select(user_id)
    elif text == 'На диапазон':
        user_status[user_id]['timetable']['day'] = 'range'
        status__get_timetable__day_range__start(user_id)
    else:
        status__set_timetable__day(user_id)


def status__get_timetable__day_select(user_id,
                                      text="Напишите на какую дату необходимо расписание, например 30.12.2022"):
    bot.send_message(user_id, text)
    user_status[user_id]['status'] = "timetable_day_select"


def status__set_timetable__day_select(text, user_id):
    try:
        user_status[user_id]['timetable']['temp'] = str(datetime.datetime.strptime(text, '%d.%m.%Y').date())
        show_timetable(user_id)
    except:
        status__get_timetable__day_select(user_id, "Неверный формат")


def status__get_timetable__day_range__start(user_id, text="С какой даты вывести рассписание, например 30.12.2022"):
    bot.send_message(user_id, text)
    user_status[user_id]['status'] = "timetable_day_range__start"


def status__set_timetable__day_range__start(text, user_id):
    try:
        user_status[user_id]['timetable']['temp'] = {
            'start': str(datetime.datetime.strptime(text, '%d.%m.%Y').date()),
            'end': None
        }
        status__get_timetable__day_range__end(user_id)
    except:
        status__get_timetable__day_range__start(user_id, "Неверный формат")


def status__get_timetable__day_range__end(user_id, text="До даты вывести рассписание, например 30.12.2022"):
    bot.send_message(user_id, text)
    user_status[user_id]['status'] = "timetable_day_range__end"


def status__set_timetable__day_range__end(text, user_id):
    try:
        end = str(datetime.datetime.strptime(text, '%d.%m.%Y').date())
        if user_status.get(user_id).get('timetable').get('temp').get('start') > end:
            user_status[user_id]['timetable']['temp']['end'] = user_status.get(user_id).get('timetable').get(
                'temp').get('start')
            user_status[user_id]['timetable']['temp']['start'] = end
        else:
            user_status[user_id]['timetable']['temp']['end'] = end
        show_timetable(user_id)
    except:
        status__get_timetable__day_range__end(user_id, "Неверный формат")


def get_timetable_text(date, timetable):
    weeks = {
        '1': "ПН",
        '2': "ВТ",
        '3': "СР",
        '4': "ЧТ",
        '5': "ПТ",
        '6': "СБ"
    }
    timetable_text = "{week} {date}\n".format(week=weeks.get(str(date.weekday() + 1)), date=date.strftime('%d.%m.%Y'))
    for el in timetable:
        timetable_text += "-----\nПара #{number} {replace}\n{time}\nГруппа: {group}\n{lesson}\n{teacher}\nКабинет: {cabinet}\n\n".format(
            number=el.get('lesson_number'),
            replace="( Замена )" if el.get('replacement') else "",
            time=el.get('time'),
            group=el.get('college_group'),
            lesson=el.get('lesson'),
            teacher=el.get('teacher'),
            cabinet=el.get('lesson_hall')
        )
    return timetable_text


def show_timetable(user_id):
    status = user_status[user_id].get('timetable', {}).get('day')
    url = "https://back.uksivt.com/api/v1/{type_el}/{el}/from_date/".format(
        type_el=user_status.get(user_id).get('timetable').get('type'),
        el=user_status.get(user_id).get('timetable').get('value'))

    if status == 'now' or status == 'tomorrow' or status == 'day_x':
        day = datetime.datetime.strptime(user_status.get(user_id).get('timetable').get('temp'),
                                         '%Y-%m-%d').date() if status == 'day_x' else datetime.date.today()
        if status == 'tomorrow':
            day += datetime.timedelta(days=1)
        if datetime.date.today().weekday() == 6:
            day += datetime.timedelta(days=1)

        timetable = requests.get(url + str(day)).json()
        text = get_timetable_text(day, timetable[str(day.weekday() + 1)])

    elif status == 'range':
        days = []
        start = datetime.datetime.strptime(user_status.get(user_id).get('timetable').get('temp').get('start'),
                                           '%Y-%m-%d').date()
        end = datetime.datetime.strptime(user_status.get(user_id).get('timetable').get('temp').get('end'),
                                         '%Y-%m-%d').date()
        tmp_day = start
        tmp_count_weeks = math.ceil((end - start).days / 7)
        for i in range(1, tmp_count_weeks + 1):
            result = requests.get(url + str(tmp_day)).json()
            if i == 1 and i != tmp_count_weeks:
                for day_week in result.keys():
                    if int(day_week) >= start.weekday() + 1:
                        days.append(get_timetable_text(tmp_day, result.get(day_week)))
                    tmp_day += datetime.timedelta(days=1)
            elif i == 1 and i == tmp_count_weeks:
                for day_week in result.keys():
                    if start.weekday() + 1 <= int(day_week) <= end.weekday() + 1:
                        days.append(get_timetable_text(tmp_day, result.get(day_week)))
                        tmp_day += datetime.timedelta(days=1)
            elif i == tmp_count_weeks:
                for day_week in result.keys():
                    if int(day_week) <= end.weekday() + 1:
                        days.append(get_timetable_text(tmp_day, result.get(day_week)))
                        tmp_day += datetime.timedelta(days=1)
            else:
                for day_week in result.keys():
                    days.append(get_timetable_text(tmp_day, result.get(day_week)))
                    tmp_day += datetime.timedelta(days=1)
            tmp_day += datetime.timedelta(days=1)
        text = '\n#####\n\n\n'.join(days)

    bot.send_message(user_id, text)
    status__set_menu(user_id)


@bot.message_handler(content_types=['text'])
def message_handler(message):
    user_id = message.from_user.id
    if message.from_user.id not in user_status:
        user_status[message.from_user.id] = {
            'status': None,
            'subscription': {
                'type': 'college_group',
                'value': '19П-1'
            },
            'timetable': {
                'type': None,
                'day': None,
                'temp': None,
                'value': None
            }
        }
    status = user_status[user_id].get('status')
    if status == 'menu':
        status__get_menu(message.text, user_id)
    elif status == 'select_subscription':
        status__get_select_subscription(message.text, user_id)
    elif status == 'select_subscription__group':
        status__get_select_subscription__group(message.text, user_id)
    elif status == 'select_subscription__teacher':
        status__get_select_subscription__teacher(message.text, user_id)
    elif status == 'timetable':
        status__get_timetable(message.text, user_id)
    elif status == 'timetable_select':
        status__get_timetable__select(message.text, user_id)
    elif status == 'timetable_day':
        status__get_timetable__day(message.text, user_id)
    elif status == 'timetable_day_select':
        status__set_timetable__day_select(message.text, user_id)
    elif status == 'timetable_day_range__start':
        status__set_timetable__day_range__start(message.text, user_id)
    elif status == 'timetable_day_range__end':
        status__set_timetable__day_range__end(message.text, user_id)
    else:
        status__set_menu(user_id)


if __name__ == '__main__':
    bot.polling(none_stop=True)
