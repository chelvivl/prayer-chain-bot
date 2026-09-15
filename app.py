import datetime
import os
import random
from dataclasses import dataclass
from pathlib import Path
from time import sleep

import telebot
from telebot import types
from telebot.types import InputMediaPhoto, ReactionTypeEmoji

sleep(3)
print("Started")
bot = telebot.TeleBot(os.environ["BOT_TOKEN"])
dir_path = 'data'
is_auth = False

peoples = []
superuser_id = 707824866
# superuser_id = 707824868
current_group_id = -4159440907
test_group_id = -4159440907
# main_group_id = -4159440907
main_group_id = -971031541
result = ""
is_message_for_group_mode = False
is_delete_mode = False
message_for_group = ""
auto_mode = True
ready_to_change_auto_mode = True
edit_message_mode = False
current_history_message_id = 0
message_last_id = []


@dataclass
class Person:
    username: str
    first_name: str
    last_name: str


@dataclass
class CustomMessage:
    id: int
    text: str


def load_test_data():
    peoples.append(Person("username1", "Кирилл", "Сергеев"))
    peoples.append(Person("username2", "Иван", "Фомин"))
    peoples.append(Person("username3", "Сергей", "Ивацевич"))


poll_id_in_group = 0
is_open_poll = False
is_open_close = False


def automatic():
    global is_open_close, ready_to_change_auto_mode
    while auto_mode:
        current_day = get_current_day_of_week()
        now = datetime.datetime.now().strftime('%H:%M:%S')
        # now = datetime.datetime.now().strftime('%S')
        sleep(1)
        if (now == "19:00:00") and current_day == 5 and not is_open_poll:
        # if now == "00" and not is_open_poll:
            print(f'Создан опрос: {now}')
            send_answer()
        if is_open_poll and now == "18:58:50" and current_day == 6:
        # if is_open_poll and now == "40":
            print(f'Закрыт опрос: {now}')
            close_answer()
            is_open_close = True
        if not is_open_poll and is_open_close and now == "18:59:52" and current_day == 6:
        # if not is_open_poll and is_open_close and now == "55":
            print(f'Сформирован список: {now}')
            formed_list()
            print(f'Отправлен список: {now}')
            send_list_people()
            is_open_close = False
            ready_to_change_auto_mode = True


def add_to_history_message_array(element):
    if len(message_last_id) >= 50:
        message_last_id.pop(0)
    message_last_id.append(CustomMessage(id=element.id, text=element.text))


def get_digit(counter):
    match counter:
        case 1:
            return "1⃣"
        case 2:
            return "2⃣"
        case 3:
            return "3⃣"
        case 4:
            return "4⃣"
        case _:
            return "5⃣"


def send_list_people():
    # counter = 5
    # message_id_for_delete = [bot.send_message(current_group_id, f'Молитвенная цепочка будет сформирована через...').id]
    # while counter > 0:
    #     message_id_for_delete.append(bot.send_message(current_group_id, f'{get_digit(counter)}').id)
    #     counter = counter - 1
    #     sleep(1)
    add_to_history_message_array(
        CustomMessage(bot.send_message(current_group_id, result, parse_mode='html').id, result))
    # bot.delete_messages(current_group_id, message_id_for_delete)


@bot.message_handler(commands=['start'])
def main(message):
    global is_auth
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton("Отправить опрос")
    btn2 = types.KeyboardButton("Закрыть опрос")
    btn3 = types.KeyboardButton("Сформировать список")
    btn4 = types.KeyboardButton("Сообщение группе")
    btn8 = types.KeyboardButton("Автоматический режим")
    btn9 = types.KeyboardButton("Текущая группа")
    btn10 = types.KeyboardButton("Переключить группу")
    btn11 = types.KeyboardButton("Последние 50 сообщений")
    markup.add(btn1)
    markup.add(btn2)
    markup.add(btn3)
    markup.add(btn4)
    markup.add(btn8)
    markup.add(btn9)
    markup.add(btn10)
    markup.add(btn11)

    if message.chat.id == superuser_id:
        is_auth = True
        bot.send_message(message.chat.id, "Вы вошли в систему", reply_markup=markup)
        automatic()


@bot.poll_answer_handler()
def handle_poll_answer(answer):
    global peoples
    print(answer)
    if len(answer.option_ids) == 1:
        if answer.option_ids[0] == 0:
            peoples.append(Person(answer.user.username, answer.user.first_name, answer.user.last_name))
            bot.send_message(superuser_id,
                             f"Будет участвовать: @{answer.user.username} ({answer.user.first_name} {answer.user.last_name})")
        else:
            bot.send_message(superuser_id,
                             f"Не будет участвовать: @{answer.user.username} ({answer.user.first_name} {answer.user.last_name})")
    else:
        if check_element({answer.user.username, answer.user.first_name, answer.user.last_name}):
            peoples.remove(Person(answer.user.username, answer.user.first_name, answer.user.last_name))
            bot.send_message(superuser_id,
                             f"Отменил голос: @{answer.user.username} ({answer.user.first_name} {answer.user.last_name})")
    print(peoples)


def check_element(element):
    for item in peoples:
        if element == item:
            return True
    return False


def send_answer():
    global poll_id_in_group, is_open_poll, peoples, ready_to_change_auto_mode
    ready_to_change_auto_mode = False
    is_open_poll = True
    peoples = []
    if current_group_id == test_group_id:
        load_test_data()
    bot.send_message(superuser_id, 'Опрос в группе открыт')
    questions = ["Участвую", "Не участвую"]
    poll_id_in_group = bot.send_poll(
        current_group_id,
        f'Молитвенная цепочка {get_date()} (голосование до 21:59 завтрашнего дня)',
        questions,
        is_anonymous=False,
        allows_multiple_answers=False,
    ).id


def check_pair(pairs):
    is_good = True
    for pair in pairs:
        if pair[0].username == pair[1].username and pair[0].first_name == pair[1].first_name and pair[0].last_name == \
                pair[1].last_name:
            is_good = False
            break
    return is_good


def formed_list():
    global result
    if not is_open_poll:
        if len(peoples) > 1:
            result = f'<b>Молитвенная цепочка {get_date()}:</b>\n\n'
            pairs = distributed(peoples)
            for pair in pairs:
                if pair[0].first_name == pair[1].first_name and pair[0].last_name == pair[
                    1].last_name and \
                        pair[0].username == pair[1].username:
                    result += f'{pair[0].first_name} {pair[0].last_name}\n🆘🆘🆘🆘🆘🆘\n{pair[1].first_name} {pair[1].last_name}\n\n'
                else:
                    who_first_name = pair[0].first_name

                    who_last_name = ""
                    if pair[0].last_name is None:
                        who_last_name = ""
                    else:
                        who_last_name = pair[0].last_name

                    for_whom_first_name = pair[1].first_name

                    for_whom_last_name = ""
                    if pair[1].last_name is None:
                        for_whom_last_name = ""
                    else:
                        for_whom_last_name = pair[1].last_name
                    result += f'{who_first_name} {who_last_name}↩️\n  👇👇👇\n  🙏🔥{for_whom_first_name} {for_whom_last_name}🔥🙏\n\n'

            is_good = check_pair(pairs)
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Отправить", callback_data='send_to_group'))
            if not is_good:
                markup.add(types.InlineKeyboardButton("Переформировать", callback_data='reformed'))
                if auto_mode:
                    print("Идет переформирования, то что есть не годится")
                    formed_list()
            bot.send_message(superuser_id, result, reply_markup=markup, parse_mode='html')
        elif len(peoples) == 1:
            result = f'<b>Молитвенная цепочка {get_date()}:</b>\n\n'
            result += 'К сожалению, цепочку сформировать не удалось, так как участвовать согласился всего 1 человек.'
            bot.send_message(superuser_id,
                             'В списке желающих участвовать всего 1 человек. Смысла в этом нет.')
        else:
            result = f'<b>Молитвенная цепочка {get_date()}:</b>\n\n'
            result += 'К сожалению, цепочку сформировать не удалось, так как никто не захотел участвовать.'
            bot.send_message(superuser_id, 'В списке желающих участвовать нет ни одного человека')
    else:
        bot.send_message(superuser_id,
                         "Опрос еще не завершен. Для формирования списка людей необходимо сначала завершить голосование.")


def delete_poll():
    # counter = 5
    # message_id_for_delete = [bot.send_message(current_group_id, f'Опрос будет закрыт через...').id]
    # while counter > 0:
    #     message_id_for_delete.append(bot.send_message(current_group_id, f'{get_digit(counter)}').id)
    #     counter = counter - 1
    #     sleep(1)
    bot.delete_message(current_group_id, poll_id_in_group)
    # bot.delete_messages(current_group_id, message_id_for_delete)


def close_answer():
    global is_open_poll
    if is_open_poll:
        list_prayer_people = "Список участников в молитвенной цепочке:\n\n"
        if len(peoples) > 0:
            index = 1
            for people in peoples:
                list_prayer_people += f'{index}) {people.first_name} {people.last_name}\n'
                index += 1
        else:
            list_prayer_people += "Нет участников"
        bot.send_message(superuser_id, f'{list_prayer_people}')
        is_open_poll = False
        delete_poll()
    else:
        bot.send_message(superuser_id, 'Опрос и так закрыт на данный момент')


def distributed(people):
    result_list = []
    distributed_people = []
    for i in range(len(people)):
        pair = get_pair(i, distributed_people, people)
        result_list.append(pair)
        selected_index = peoples.index(pair[1])
        distributed_people.append(selected_index)
    return result_list


def get_pair(current_index, distributed_people, people):
    mutable_people = []
    for index, person in enumerate(people):
        if index != current_index and index not in distributed_people:
            mutable_people.append(person)
    if len(mutable_people) > 0:
        random_index = random.randint(0, len(mutable_people) - 1)
        return people[current_index], mutable_people[random_index]
    else:
        return people[current_index], people[current_index]


def send_message_mode():
    global is_message_for_group_mode, message_for_group
    is_message_for_group_mode = True
    message_for_group = ""
    bot.send_message(superuser_id, 'Введите сообщение')


def send_message(message):
    global message_for_group, is_message_for_group_mode
    message_for_group = message.text
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Отправить", callback_data='send_to_group_message'))
    bot.send_message(message.chat.id, message_for_group, reply_markup=markup)
    is_message_for_group_mode = False


def change_auto_mode():
    global auto_mode
    if auto_mode:
        if ready_to_change_auto_mode:
            auto_mode = not auto_mode
            bot.send_message(superuser_id, 'Автоматический режим отключен')
        else:
            bot.send_message(superuser_id,
                             'Невозможно отключить автоматический режим. Механизм формирования молитвенной цепочки уже запущен. Поробуйте после окончания формирования молитвенной цепочки.')
    else:
        auto_mode = not auto_mode
        bot.send_message(superuser_id, 'Автоматический режим включен')
        automatic()


def last_messages():
    for message_from_chat in message_last_id:
        bot.send_message(superuser_id, f'{message_from_chat.id} - {message_from_chat.text}')


def get_from_history(id):
    for mes in message_last_id:
        try:
            if mes.id == int(id):
                return mes
        except:
            return CustomMessage(id=0, text="Пусто")
    return CustomMessage(id=0, text="Пусто")


def action_with_message(history):
    global current_history_message_id
    markup = types.InlineKeyboardMarkup()
    current_history_message_id = history.id
    markup.add(types.InlineKeyboardButton("Удалить", callback_data='delete_history_message'))
    markup.add(types.InlineKeyboardButton("Редактировать", callback_data='edit_history_message'))
    markup.row(types.InlineKeyboardButton("🔥", callback_data='fire_reaction'))
    markup.row(types.InlineKeyboardButton("👍", callback_data='good_reaction'))
    markup.row(types.InlineKeyboardButton("❤", callback_data='love_reaction'))
    markup.row(types.InlineKeyboardButton("🙏", callback_data='pray_reaction'))
    markup.row(types.InlineKeyboardButton("🤡", callback_data='clown_reaction'))
    bot.send_message(superuser_id, history.text, reply_markup=markup)


@bot.message_handler()
def info(message):
    global is_open_poll, is_message_for_group_mode, result, message_for_group, auto_mode, current_group_id
    print(f'{message.chat.id}: {message.text}')
    # bot.send_message(superuser_id, message)
    if is_auth:
        if message.chat.id == superuser_id:

            history = get_from_history(message.text)

            if history.id != 0:
                action_with_message(history)
            elif edit_message_mode:
                edit_history_message(message.text)
            else:
                if not is_message_for_group_mode and not is_delete_mode:
                    match message.text.lower():
                        case "отправить опрос":
                            if not auto_mode:
                                send_answer()
                            else:
                                bot.send_message(message.chat.id, 'Недоступно в автоматическом режиме')
                        case "сформировать список":
                            if not auto_mode:
                                formed_list()
                            else:
                                bot.send_message(message.chat.id, 'Недоступно в автоматическом режиме')
                        case "закрыть опрос":
                            if not auto_mode:
                                close_answer()
                            else:
                                bot.send_message(message.chat.id, 'Недоступно в автоматическом режиме')
                        case "сообщение группе":
                            send_message_mode()
                        case "автоматический режим":
                            change_auto_mode()
                        case "последние 50 сообщений":
                            last_messages()
                        case "текущая группа":
                            if current_group_id == main_group_id:
                                bot.send_message(message.chat.id, 'Основная группа')
                            else:
                                bot.send_message(message.chat.id, 'Тестовая группа')
                        case "переключить группу":
                            if current_group_id == main_group_id:
                                current_group_id = test_group_id
                                bot.send_message(message.chat.id, 'Переключено на тестовую группу')
                            else:
                                current_group_id = main_group_id
                                bot.send_message(message.chat.id, 'Переключено на основную группу')
                        case _:
                            bot.send_message(message.chat.id, 'Я вас не понимаю.....\nНет такой команды')
                elif is_message_for_group_mode and not is_delete_mode:
                    send_message(message)
                elif not is_message_for_group_mode and is_delete_mode:
                    remove_file(message.text)
        elif message.chat.id == current_group_id:
            add_to_history_message_array(message)


def remove_file(filename):
    global is_delete_mode
    my_file = Path(f'data/{filename}.jpg')
    if my_file.is_file():
        os.remove(my_file)
        bot.send_message(superuser_id, 'Фото удалено')
        is_delete_mode = False
    else:
        bot.send_message(superuser_id, 'Такого файла не существует')
        is_delete_mode = False


def delete_from_history_array():
    global current_history_message_id
    index = -1
    for i, mes in enumerate(message_last_id):
        if mes.id == current_history_message_id:
            index = i
    if index != -1:
        message_last_id.pop(index)
        current_history_message_id = -1


def delete_history_message():
    global current_history_message_id
    try:
        bot.delete_message(current_group_id, current_history_message_id)
        bot.send_message(superuser_id, 'Сообщение удалено')
        delete_from_history_array()
    except:
        bot.send_message(superuser_id, 'Сообщение не найдено. Возможно оно уже удалено')
        current_history_message_id = -1


def edit_from_history_array(edit_text):
    global current_history_message_id
    index = -1
    for i, mes in enumerate(message_last_id):
        if mes.id == current_history_message_id:
            index = i
    if index != -1:
        old = message_last_id[index]
        message_last_id[index] = CustomMessage(id=old.id, text=edit_text)
        current_history_message_id = -1


def edit_history_message(edit_text):
    global edit_message_mode, current_history_message_id
    try:
        bot.edit_message_text(chat_id=current_group_id, message_id=current_history_message_id, text=edit_text)
        bot.send_message(superuser_id, 'Сообщение отредактировано')
        edit_from_history_array(edit_text)
    except:
        bot.send_message(superuser_id, 'Невозможно отредактировать сообщение')
        current_history_message_id = -1
    edit_message_mode = False


@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    global edit_message_mode
    if callback.data == 'send_to_group':
        send_list_people()
        bot.send_message(superuser_id, "Список отправлен")
    if callback.data == 'send_to_group_message':
        add_to_history_message_array(
            CustomMessage(id=bot.send_message(current_group_id, message_for_group).id, text=message_for_group))
        bot.send_message(superuser_id, "Сообщение отправлено")
    if callback.data == 'reformed':
        formed_list()
    if callback.data == 'delete_history_message':
        delete_history_message()
    if callback.data == 'edit_history_message':
        edit_message_mode = True
        bot.send_message(superuser_id, "Введите отредактированное сообщение")
    if callback.data == 'fire_reaction':
        reaction = ReactionTypeEmoji(type="emoji", emoji="🔥")
        bot.set_message_reaction(chat_id=current_group_id, message_id=current_history_message_id, reaction=[reaction],
                                 is_big=True)
    if callback.data == 'good_reaction':
        reaction = ReactionTypeEmoji(type="emoji", emoji="👍")
        bot.set_message_reaction(chat_id=current_group_id, message_id=current_history_message_id, reaction=[reaction],
                                 is_big=True)
    if callback.data == 'love_reaction':
        reaction = ReactionTypeEmoji(type="emoji", emoji="❤")
        bot.set_message_reaction(chat_id=current_group_id, message_id=current_history_message_id, reaction=[reaction],
                                 is_big=True)
    if callback.data == 'pray_reaction':
        reaction = ReactionTypeEmoji(type="emoji", emoji="🙏")
        bot.set_message_reaction(chat_id=current_group_id, message_id=current_history_message_id, reaction=[reaction],
                                 is_big=True)
    if callback.data == 'clown_reaction':
        reaction = ReactionTypeEmoji(type="emoji", emoji="🤡")
        bot.set_message_reaction(chat_id=current_group_id, message_id=current_history_message_id, reaction=[reaction],
                                 is_big=True)


def get_date():
    today = datetime.date.today()
    added_count_days = 0
    match today.weekday():
        case 0:
            added_count_days = 0
        case 1:
            added_count_days = 6
        case 2:
            added_count_days = 5
        case 3:
            added_count_days = 4
        case 4:
            added_count_days = 3
        case 5:
            added_count_days = 2
        case 6:
            added_count_days = 1
    start_data = today + datetime.timedelta(added_count_days)
    end_date = start_data + datetime.timedelta(6)
    return f'c {start_data.strftime("%d.%m")} по {end_date.strftime("%d.%m")}'


def get_current_day_of_week():
    today = datetime.datetime.today()
    return today.weekday()


bot.infinity_polling()
