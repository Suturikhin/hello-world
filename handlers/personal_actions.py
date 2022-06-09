from aiogram import types
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from dispatcher import dp, bot
import config
import re
from bot import BotDB
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import asyncio


# создаём класс объектов для администратора
class client:
    def __init__(self, name, ID):
        self.name = name
        self.ID = ID
# sample of client list creation for admin tab:
# clients = [client(name,ID) for name,ID in names,IDs]

# создаём форму и указываем поля
class Form(StatesGroup):
    name = State()

# обработка команды start
@dp.message_handler(commands = "start")
async def start(message: types.Message):
    if(not BotDB.user_exists(message.from_user.id)):
        BotDB.add_user(message.from_user.id)
        await message.bot.send_message(message.from_user.id, "Похоже, вы первый раз здесь. Введите сообщение с названием вашей фирмы и нажмите Enter")
        await Form.name.set()
    else:
        button_docs = KeyboardButton('/Документы')
        button_ball = KeyboardButton('/Мяч')
        button_sent = KeyboardButton('/Отправил(а)')
        markup3 = ReplyKeyboardMarkup(resize_keyboard=True).add(button_docs).add(button_ball).add(button_sent)
        await message.bot.send_message(message.from_user.id, "С возвращением!", reply_markup=markup3)

# обработка введения описания фирмы
@dp.message_handler(state=Form.name)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await state.finish()
    await message.reply(f"Описание Вашей фирмы успешно  добавлено, мы будем идентифицировать вас в базе как {data['name']}.\n\n"
                        f"Уважаемые {data['name']}, прошу обратить Ваше внимание, что взаимодействие с ботом происходит только по нажатию кнопок\n"
                        f"На сообщения бот реагировать пока не умеет 😊")
    BotDB.add_client_info(message.from_user.id, data['name'])

    button_docs = KeyboardButton('/Документы')
    button_ball = KeyboardButton('/Мяч')
    button_sent = KeyboardButton('/Отправил(а)')
    markup3 = ReplyKeyboardMarkup(resize_keyboard=True).add(button_docs).add(button_ball).add(button_sent)
    #greet_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(button_ball)
    await message.bot.send_message(message.from_user.id, f"Добро пожаловать, {data['name']}!", reply_markup=markup3)

@dp.message_handler(commands = "Мяч")
async def start(message: types.Message):
    #await message.bot.send_message(message.from_user.id, "Я проверю в базе")
    dbr = BotDB.get_records(message.from_user.id)

    #создаём кнопку документы в ReplyKeyBoardMarkUp, если мяч на стороне клиента
    button_docs = KeyboardButton('/Документы')
    button_ball = KeyboardButton('/Мяч')
    button_sent = KeyboardButton('/Отправил(а)')


    #формируем раскладки кнопок
    markup3 = ReplyKeyboardMarkup(resize_keyboard=True).add(button_docs).add(button_ball).add(button_sent)

    #print для отладки
    print(dbr)

    #флаг для мяча
    flag = 0

    for i in dbr:
        if i[1] == 1:
            flag = 1

    if flag != 1:
        await message.bot.send_message(message.from_user.id, "Мяч на стороне охотников! 👍", reply_markup = markup3)
    else:
        await message.bot.send_message(message.from_user.id, "Мяч на вашей стороне 👇", reply_markup = markup3 )

@dp.message_handler(commands = "Документы")
async def start(message: types.Message):
    await message.bot.send_message(message.from_user.id, "Я проверяю в базе")
    dbr = BotDB.get_records(message.from_user.id)

    # добавляем флаг = 0, если мяч на стороне бухгалтерии и =1, если мяч на стороне клиента
    flag = 0
    for i in dbr:
        if i[1] == 1:
            flag = 1
            await message.bot.send_message(message.from_user.id, f"Мы ждём от вас {i[0]}")

    button_docs = KeyboardButton('/Документы')
    button_ball = KeyboardButton('/Мяч')
    button_sent = KeyboardButton('/Отправил(а)')
#    markup2 = ReplyKeyboardMarkup().add(button_docs).add(button_ball)
    markup3 = ReplyKeyboardMarkup(resize_keyboard=True).add(button_docs).add(button_ball).add(button_sent)
    if flag == 0:
        await message.bot.send_message(message.from_user.id, "Вам нечего отправлять, мяч на стороне охотников 👌", reply_markup=markup3)
    else:
        await message.bot.send_message(message.from_user.id, "Мяч на вашей стороне 👇", reply_markup=markup3)

@dp.message_handler(commands = "Отправил(а)")
async def start(message: types.Message):
    # забираем инфу из базы по клиенту
    dbr = BotDB.get_records(message.from_user.id)

    button_docs = KeyboardButton('/Документы')
    button_ball = KeyboardButton('/Мяч')
    button_sent = KeyboardButton('/Отправил(а)')
    markup3 = ReplyKeyboardMarkup(resize_keyboard=True).add(button_docs).add(button_ball).add(button_sent)

    if dbr == []:
        await message.bot.send_message(message.from_user.id,
                                       "Спасибо за уведомление, но документов на вас в базе ещё не числится, их статус неизвестен, поэтому Вам нечего отправлять 😊\n\nМы добавим необходимые документы и сообщим Вам 🤝",
                                       reply_markup=markup3)
    else:
        for i in dbr:
            if i[1] == 1:
                BotDB.update_side(message.from_user.id, i[0], 0)
                await message.bot.send_message(message.from_user.id,
                                               "Спасибо за уведомление, мы проверим. Теперь мяч на стороне охотников 👍 \n\n Мы обновим статус документов, если от вас потребуется что-то ещё 🤝",
                                               reply_markup=markup3)
                #здесь нужно отправить уведомление администратору, что такой-то клиент выслал документы
                user_name = BotDB.get_client_info(message.from_user.id)
                await message.bot.send_message(457425801, f"Клиент {user_name} сообщил(а), что отправил документы")

            else:
                await message.bot.send_message(message.from_user.id,
                                               "Мы проверили в системе, потому что вы нажали кнопку 'Отправил(а)', но  мяч на нашей стороне, мы ничего от вас не ждём 😊",
                                               reply_markup=markup3)
#            break

    # for i in dbr:
    #     if i[1] == 1:
    #         await message.bot.send_message(message.from_user.id, f"Мы ждём от вас {i[0]}")
    #         flag = 1

    # if flag == 0:
    # else:
    #     button_docs = KeyboardButton('/Документы')
    #     button_ball = KeyboardButton('/Мяч')
    #     button_sent = KeyboardButton('/Отправил')
    #     markup3 = ReplyKeyboardMarkup().add(button_docs).add(button_ball).add(button_sent)
    #     await message.bot.send_message(message.from_user.id, "Мяч на вашей стороне 👇", reply_markup=markup3)

@dp.message_handler(lambda message: message.text and 'hello' in message.text.lower())
async def text_handler(msg: types.Message):
    await msg.reply("Драсьте")

#обработка сообщения с именем админа - выгрузка всех компаний, за которые он ответственнен
@dp.message_handler(commands = "getadmin")
async def start(message: types.Message):
    #нужно прикрутить проверку через пароль для доступа в админ базу
    await message.bot.send_message(message.from_user.id, "Я проверяю всех админов в базе")
    admins_list = BotDB.getadmin_reply()
    print(admins_list)
    #Попытка выгрузить кнопки для админов в чат через динамический список админов
    markup_admins = ReplyKeyboardMarkup(resize_keyboard=True)
    for i in admins_list:
       button = KeyboardButton(f'admin {i[1]}')
       markup_admins = markup_admins.add(button)

    await message.bot.send_message(message.from_user.id, "Текущий список админов", reply_markup=markup_admins)

#Здесь обрабатываем ввод, начинающийся с админа (кнопки после getadmin) и выдаём список возможных действий
@dp.message_handler(lambda message: 'admin ' in message.text.lower() and message.text)
async def start(message: types.Message):
    print(message.text)
    current_admin = message.text.split(' ')[1]
    id = BotDB.get_admin_id(current_admin)
    print(id)

    users_list = BotDB.get_group_by_responsible(current_admin)
    print(users_list)

    #Выгружаем кнопки компаний по данному бухшалтеру в чат через динамический список компаний
    markup_users = ReplyKeyboardMarkup(resize_keyboard=True)
    for i in users_list:
       button = KeyboardButton(f'компания {i[1]}')
       markup_users = markup_users.add(button)

    await message.bot.send_message(message.from_user.id, f"Текущий список компаний бухгалтера {current_admin}", reply_markup=markup_users)


@dp.message_handler()
async def send_message(msg: types.Message):
    await msg.reply("Взаимодействие с ботом только по кнопкам, на сообщения бот реагировать пока не умеет 😊")


# @dp.message_handler(commands = ("sent", "s"), commands_prefix = "/!")
# async def start(message: types.Message):
#     cmd_variants = (('/sent', '/s', '!sent', '!s'))
#     side = False if message.text.startswith(cmd_variants[0]) else True
#
#     note_from_client = str(message.text)
#     data=str(message.text).split(' ')
#     if len(data) < 4:
#         await message.bot.send_message(message.from_user.id, "Мало данных")
#     else:
#         BotDB.update_record(message.from_user.id, data[1], data[2], data[3])
#         await message.bot.send_message(message.from_user.id, "Данные приняты")
#  BotDB.add_record(message.from_user.id, side, note_from_client)



# @dp.message_handler(commands = ("history", "h"), commands_prefix = "/!")
# async def start(message: types.Message):
#     cmd_variants = ('/history', '/h', '!history', '!h')
#     dbr = BotDB.get_records(message.from_user.id)
#     print(dbr)
#     for i in dbr:
#         if i[1] == 1:
#             await message.bot.send_message(message.from_user.id, i[0])
