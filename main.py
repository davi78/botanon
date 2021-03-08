import logging
import asyncio
import random
import sqlite3
import string

#aiogram и всё утилиты для коректной работы с Telegram API
from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.utils.emoji import emojize
from aiogram.dispatcher import Dispatcher
from aiogram.types.message import ContentType
from aiogram.utils.markdown import text, bold, italic, code, pre
from aiogram.types import ParseMode, InputMediaPhoto, InputMediaVideo, ChatActions
from aiogram.types import ReplyKeyboardRemove,ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import aiogram.utils.exceptions
from aiogram.types.message import ContentTypes

#конфиг с настройками
import config
from database import dbworker


#инициализируем базу данных
db = dbworker('db dumb1.db')
print('[i] Bot Succes')

#инициализируем бота
bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot,storage=MemoryStorage())

#логирование
logging.basicConfig(filename="all_log.log", level=logging.INFO, format='%(asctime)s - %(levelname)s -%(message)s')
warning_log = logging.getLogger("warning_log")
warning_log.setLevel(logging.WARNING)

fh = logging.FileHandler("warning_log.log")

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)


warning_log.addHandler(fh)

#хендлер команды /start
@dp.message_handler(commands=['start'],state='*')
async def start(message : types.Message, state: FSMContext):

    await state.finish()

    button_search = KeyboardButton('Cari pasangan🔍')

    button_info_project = KeyboardButton('Backpack👜')

    ranked = KeyboardButton('Chat Teratas⭐️')

    count_users = KeyboardButton(f'В боте уже {int(db.count_user() * 1.5)} пользователей🥳')

    mark_menu = ReplyKeyboardMarkup()

    mark_menu.add(button_search,button_info_project,ranked,count_users)

    await bot.send_message(message.chat.id,'👋 Привет!\n\nЯ Chatium, бот для анонимного общения\nИ чего ты ждёшь,давай начнём!\n\nТыкай на кнопки внизу, а там разберёмся\n\nНовости и мемные переписки - https://t.me/chatium_community \n\nЛамповое общения - https://t.me/chatium_chat',reply_markup=mark_menu)


@dp.message_handler(lambda message : message.text == 'Backpack👜' or message.text == 'О проекте🧑‍💻' or message.text == 'Все ссылки на нас' or message.text == '[ Для разработчиков ]',state='*')
async def about_project(message : types.Message):
    if message.text == 'Backpack👜':

        for_developers = KeyboardButton('[ Для разработчиков ]')

        back = KeyboardButton('Назад')

        rules = KeyboardButton('Правила📖')

        mark_menu = ReplyKeyboardMarkup()

        mark_menu.add(for_developers,rules,back)

        await bot.send_message(message.chat.id,'Вся информация тут👇',reply_markup=mark_menu)

    elif message.text == '[ Для разработчиков ]':
        await message.answer('Если вы разработчик и хотите поучаствовать в разработке проекта то смело контрибутье на гите или пишите на почту - merlinincorp@gmail.com\n\nGithub - https://github.com/RenatYakublevich/AnonymChat')

@dp.message_handler(commands=['rules'],state='*')
@dp.message_handler(lambda message : message.text == 'Правила📖')
async def rules(message : types.Message):
    await message.answer('''📌Правила общения в @Chatium_Bot\n1. Любые упоминания психоактивных веществ. (наркотиков)\n2. Детская порнография. ("ЦП")\n3. Мошенничество. (Scam)\n4. Любая реклама, спам.\n5. Продажи чего либо. (например - продажа интимных фотографий, видео)\n6. Любые действия, нарушающие правила Telegram.\n7. Оскорбительное поведение.\n8. Обмен, распространение любых 18+ материалов\n\n''')

@dp.message_handler(commands=['search'],state='*')
@dp.message_handler(lambda message: message.text == 'Cari pasangan🔍',state='*')
async def search(message : types.Message):
    try:
        if(not db.user_exists(message.from_user.id)): #если пользователя с таким telegram id не найдено
            db.add_user(message.from_user.username,message.from_user.id) #добавляем юзера в табличку дб

        male = KeyboardButton('Laki-Laki')

        wooman = KeyboardButton('Perempuan')

        back = KeyboardButton('Back')

        sex_menu = ReplyKeyboardMarkup(one_time_keyboard=True)

        sex_menu.add(male,wooman,back)

        await message.answer('Pilih jenis kelamin pasangan Anda!\nSiapa yang kamu cari?',reply_markup=sex_menu)
    except Exception as e:
        warning_log.warning(e)


@dp.message_handler(lambda message : message.text == 'Chat Teratas⭐️')
async def ranked(message : types.Message, state: FSMContext):
    ''' Функция для вывода рейтинга '''
    try:
        final_top = ''
        top_count = 0
        for i in db.top_rating():
            for d in i:
                top_count +=1
                if db.get_name_user(d) == None:
                    rofl_list = ['\nебааа#ь ты жёсткий😳','\nвасап👋','\nбро полегче там😮','\nгений🧠','\nреспект🤟']
                    final_top = final_top + str(top_count) + ' Juara - :(нету ника' + ' - ' + str(db.get_count_all_msg(d)) + ' Pesan' + rofl_list[top_count-1] + '\n'
                else:
                    rofl_list = ['\n Bagus Bisa Mencapai Rekor😳','\n Lumayan Lah🙈','\n Sedikit Menarik😮','\n Jenius Kayanya🧠','\n Jomblo pasti😂']
                    final_top = final_top + 'Rangking' + str(top_count) + ' - @' + str(db.get_name_user(d)) + ' - ' + str(db.get_count_all_msg(d)) + ' Pesan' + rofl_list[top_count-1]  + '\n'
        await message.answer(f'Peringkat Teratas Untuk saat ini\nDalam menggunakan bot😎 :\n\n{final_top}')
    except Exception as e:
        warning_log.warning(e)

#класс машины состояний
class Chating(StatesGroup):
	msg = State()

@dp.message_handler(lambda message: message.text == 'Laki-Laki' or message.text == 'Perempuan',state='*')
async def chooce_sex(message : types.Message, state: FSMContext):
    ''' Выбор пола для поиска '''
    try:
        if db.queue_exists(message.from_user.id):
            db.delete_from_queue(message.from_user.id)
        if message.text == 'Laki-Laki':
            db.edit_sex(True,message.from_user.id)
            db.add_to_queue(message.from_user.id,True)
        elif message.text == 'Perempuan':
            db.edit_sex(False,message.from_user.id)
            db.add_to_queue(message.from_user.id,False)
        else:
            db.add_to_queue(message.from_user.id,db.get_sex_user(message.from_user.id)[0])
        await message.answer('Tunggu Sebentar..Kami Sedang mencari Pasanganmu')

        #кнопки
        stop = KeyboardButton('❌Hentikan Obrolan')

        share_link = KeyboardButton('Kirim ID kamu kepasanganmu😜')

        coin = KeyboardButton('Подбросить монетку🎲')

        menu_msg = ReplyKeyboardMarkup()

        menu_msg.add(stop,share_link,coin)

        while True:
            await asyncio.sleep(0.5)
            if db.search(db.get_sex_user(message.from_user.id)[0]) != None: #если был найден подходящий юзер в очереди
                try:
                    db.update_connect_with(db.search(db.get_sex_user(message.from_user.id)[0])[0],message.from_user.id) #обновляем с кем общается юзер
                    db.update_connect_with(message.from_user.id,db.search(db.get_sex_user(message.from_user.id)[0])[0])
                    break
                except Exception as e:
                    print(e)

        while True:
            await asyncio.sleep(0.5)
            if db.select_connect_with(message.from_user.id)[0] != None: #если пользователь законектился


                break


        try:
            db.delete_from_queue(message.from_user.id)  #удаляем из очереди
            db.delete_from_queue(db.select_connect_with(message.from_user.id)[0])
        except:
            pass

        await Chating.msg.set()


        await bot.send_message(db.select_connect_with(message.from_user.id)[0],'Pasangan Ditemukan.., Silahkan mulai Obrolan💬',reply_markup=menu_msg)
        await message.answer('Pasangan Ditemukan..., Silahkan mulai Obrolan💬',reply_markup=menu_msg)
        return
    except Exception as e:
        warning_log.warning(e)
        await send_to_channel_log_exception(message,e)


@dp.message_handler(content_types=ContentTypes.TEXT)
@dp.message_handler(state=Chating.msg)
async def chating(message : types.Message, state: FSMContext):
    ''' Функция где и происходить общения и обмен ТЕКСТОВЫМИ сообщениями '''
    try:

        next = KeyboardButton('➡️Следующий диалог')

        back = KeyboardButton('Назад')

        menu_msg_chating = ReplyKeyboardMarkup()

        menu_msg_chating.add(next,back)

        await state.update_data(msg=message.text)

        user_data = await state.get_data()

        if user_data['msg'] == 'ID kamu Terkirim😜':
            if message.from_user.username == none:
                await bot.send_message(db.select_connect_with_self(message.from_user.id)[0],'Kamu belum mengatur Username, Silahkan atur username kamu...\nDi pengaturan Telegran!')
            else:
                await bot.send_message(db.select_connect_with_self(message.from_user.id)[0],'@' + message.from_user.username)
                await message.answer('@' + message.from_user.username)

        elif user_data['msg'] == '❌Hentikan Obrolan':
            await message.answer('Obrolan dihentikan!',reply_markup=menu_msg_chating)
            await bot.send_message(db.select_connect_with(message.from_user.id)[0],'Obrolan dihentikan!',reply_markup=menu_msg_chating)
            db.update_connect_with(None,db.select_connect_with(message.from_user.id)[0])
            db.update_connect_with(None,message.from_user.id)

        elif user_data['msg'] == '➡️Следующий диалог':
            await chooce_sex(message,state)

        elif user_data['msg'] == 'Подбросить монетку🎲':
            coin = random.randint(1,2)

            if coin == 1:
                coin = text(italic('Решка'))
            else:
                coin = text(italic('Орёл'))

            await message.answer(coin,parse_mode=ParseMode.MARKDOWN)
            await bot.send_message(db.select_connect_with(message.from_user.id)[0],coin,parse_mode=ParseMode.MARKDOWN)

        elif user_data['msg'] == 'Назад':
            await start(message,state)
            await state.finish()

        else:
            await bot.send_message(db.select_connect_with(message.from_user.id)[0],user_data['msg']) #отправляем сообщения пользователя
            db.log_msg(message.from_user.id,user_data['msg']) #отправка сообщений юзеров в бд
            db.add_count_msg(message.from_user.id) #добавление кол-ва сообщений в бд для рейтинга
            await send_to_channel_log(message)

    except aiogram.utils.exceptions.ChatIdIsEmpty:
        await state.finish()
        await start(message,state)
    except aiogram.utils.exceptions.BotBlocked:
        await message.answer('Пользователь вышел из чат бота!')
        await state.finish()
        await start(message,state)
    except Exception as e:
        warning_log.warning(e)
        await send_to_channel_log_exception(message,e)

@dp.message_handler(content_types=ContentTypes.PHOTO,state=Chating.msg)
async def chating_photo(message : types.Message, state: FSMContext):
    ''' Функция где и происходить общения и обмен ФОТОГРАФИЯМИ '''
    try:
        await message.photo[-1].download('photo_user/' + str(message.from_user.id) + '.jpg')
        with open('photo_user/' + str(message.from_user.id) + '.jpg','rb') as photo:
            await bot.send_photo(db.select_connect_with(message.from_user.id)[0],photo,caption=message.text)
    except Exception as e:
        warning_log.warning(e)
        await send_to_channel_log_exception(message,e)

@dp.message_handler(content_types=ContentTypes.STICKER,state=Chating.msg)
async def chating_sticker(message : types.Message, state: FSMContext):
    ''' Функция где и происходить общения и обмен CТИКЕРАМИ '''
    try:
        await bot.send_sticker(db.select_connect_with(message.from_user.id)[0],message.sticker.file_id)
    except Exception as e:
        warning_log.warning(e)
        await send_to_channel_log_exception(message,e)




#хендлер для команды назад
@dp.message_handler(commands=['back'])
@dp.message_handler(lambda message : message.text == 'Назад',state='*')
async def back(message : types.Message, state: FSMContext):
    ''' Функция для команды back '''
    await state.finish()
    await start(message,state)

#логи в телеграм канал
async def send_to_channel_log(message : types.Message):
    await bot.send_message(-1001422742707,f'ID - {str(message.from_user.id)}\nusername - {str(message.from_user.username)}\nmessage - {str(message.text)}')

async def send_to_channel_log_exception(message : types.Message,except_name):
    await bot.send_message(-1001422742707,f'Ошибка\n\n{except_name}')


#админка
@dp.message_handler(lambda message: message.text.startswith('/sendmsg_admin'),state='*')
async def admin_send_msg(message : types.Message):
    if message.from_user.id in config.ADMIN_LIST:
        msg = message.text.split(',')
        await bot.send_message(int(msg[1]),'Cообщение от админа:\n'  + msg[2])
    else:
        await message.answer('Отказано в доступе')

#хендлер который срабатывает при непредсказуемом запросе юзера
@dp.message_handler()
async def end(message : types.Message):
	'''Функция непредсказумогого ответа'''
	await message.answer('Я не знаю, что с этим делать 😲\nЯ просто напомню, что есть команда /start и /help')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True,)
