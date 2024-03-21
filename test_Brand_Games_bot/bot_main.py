from aiogram import types, Bot, executor, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import time
import json
import requests
from bs4 import BeautifulSoup
import re
import logging
from cny_gaspr import cny_run
import asyncio
from pyppeteer import launch
from edit_photo import *
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize FSM storage
memory_storage = MemoryStorage()
current_connection = None  # None или (admin_id, user_id)

from dotenv import load_dotenv
import os

load_dotenv()
bot = Bot(os.getenv('TOKEN'))
# Initialize bot and dispatcher
# bot = Bot(token="6974765983:AAFiWlYGZcrz_1o62Vw_RghDRsCe10HB-BU")
dp = Dispatcher(bot, storage=memory_storage)

start_time = datetime.now().strftime("%Y-%m-%d %H:%M")




class InputUserData(StatesGroup):
    step_3 = State()
    inline_clothing_step_1 = State()
    inline_shoes_step_2 = State()
    inline_accessories_step_3 = State()
    #Админка
    inline_сall_admin_step_4 = State()
    #Отслеживание заказа
    inline_order_chack_step_5 = State()

        

def category_orders():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Курс юаня", callback_data="inline_curce"))
    markup.add(types.InlineKeyboardButton("Изменение фотографии", callback_data="inline_photo"))
    markup.add(types.InlineKeyboardButton("Прохождение теста", callback_data="inline_test"))
    markup.add(types.InlineKeyboardButton("Закрыть", callback_data="inline_close"))
    return markup


# def parcer_cny_tinkoff():
#     start_time = time.time()
#     url = 'https://www.tinkoff.ru/invest/currencies/CNYRUB/'
#     response = requests.get(url)
#     if response.status_code == 200:
#         html = response.text
#         soup = BeautifulSoup(html, 'html.parser')
#         try:
#             price_cny = soup.find('span', class_="Money-module__money_p_VHJ").text
#             price_cny = re.sub(r'[^\d.,]', '', price_cny)
#             price_cny = round(float(price_cny.replace(',', '.')), 2)
#             price_cny = price_cny + float(0.7)
#         except AttributeError:
#              price_cny = 'Ошибка при получении курса!'
#         print('CNY Tinkoff биржа ', price_cny)
#         end_time = time.time()
#         execution_time = end_time - start_time
#         print(f'Время выполнения : {execution_time} сек')   
#         return round((price_cny), 2)
    



async def result_cny():
    price_cny = await cny_run()  # Асинхронный вызов cny_run для получения curce_now
    print(f"Текущий курс: {price_cny}")
    price_cny = round(price_cny, 2)
    return price_cny

    



@dp.message_handler(commands=["start",])
async def start(message: types.Message):
    markupes = category_orders()
    await bot.send_message(message.chat.id, "Добро пожаловать, {0.first_name}!\nВыберете действие.".format(message.from_user, bot.get_me()),
        parse_mode='html', reply_markup=markupes)
        

@dp.message_handler(commands=["help",])
async def help_command(message: types.Message):
    keyboard_markup = types.InlineKeyboardMarkup()
    support = types.InlineKeyboardButton('Позвать администратора', callback_data='support')
    back_btn = types.InlineKeyboardButton('Назад', callback_data='inline_close_admin_panel')
    keyboard_markup.row(support, back_btn)
    await message.reply(f'🤔 <b>Возникли вопросы?</b> Служба поддержки поможет Вам!\nМы на связи <b>24/7</b>❗️', parse_mode='html', reply_markup=keyboard_markup)



@dp.message_handler(commands=["info",])
async def cmd_info(message: types.Message):
    # Используем переменную start_time в ответе
    await message.answer(f"Бот запущен {start_time}")








@dp.message_handler(lambda message: message.text == "Назад")
async def functions_back_btn(message: types.Message):
    btn = category_orders()
    await bot.send_message(message.chat.id, f"<b>Возвращаю</b>", parse_mode='html', reply_markup=btn)


#Вызов админа НАЧ
# Создайте словарь для отслеживания состояний подключения
connected_users = {}


@dp.callback_query_handler(lambda c: c.data == 'support') 
async def handle_channel_message(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text('Админ уже в пути. Введите ваш запрос')
    await InputUserData.inline_сall_admin_step_4.set()


@dp.message_handler(state=InputUserData.inline_сall_admin_step_4)
async def handle_user_message(message: types.Message, state: FSMContext):
    async with state.proxy() as user_data:
        user_data['input_user'] = message.text.replace('\n', ' ')
        
    a = user_data['input_user']
    user_info = f'ID: {message.from_user.id}\nName: {message.from_user.first_name} {message.from_user.last_name}\nUsername: {message.from_user.username}'
    admin_chat_id = 6424595615

    # Извлечение и печать ID
    user_id = message.from_user.id
    print(f"User ID: {user_id}")

    # Уведомление ожидания ответа
    await bot.send_message(user_id, "Спасибо за ваш запрос! Пожалуйста, ожидайте ответа.")

    keyboard_markup = types.InlineKeyboardMarkup()
    chat_message = types.InlineKeyboardButton('Подключиться', callback_data=f'chat_message_connect:{user_id}')
    keyboard_markup.row(chat_message)
    await bot.send_message(admin_chat_id, f'Сообщение в поддержке\n\nID: {user_id}\n\n{a}\n\n{user_info}', reply_markup=keyboard_markup)

    await state.finish()


@dp.callback_query_handler(lambda c: c.data.startswith('chat_message_connect:')) 
async def handle_channel_message(callback_query: types.CallbackQuery):
    # Извлечение user_id из данных колбэка
    user_id = int(callback_query.data.split(':')[-1])

    # Добавление пользователя в словарь подключенных пользователей
    connected_users[user_id] = True

    # Создание клавиатуры для отключения
    keyboard_markup = types.InlineKeyboardMarkup()
    chat_message_unconnect = types.InlineKeyboardButton('Отключиться', callback_data=f'chat_message_unconnect:{user_id}')
    keyboard_markup.row(chat_message_unconnect)
    
    # Отправка сообщения пользователю
    await bot.send_message(user_id, f'Админ подключился')
    await bot.send_message(callback_query.from_user.id, f'Подключение к пользователю {user_id} - успешно!', reply_markup=keyboard_markup)
    connected_users[callback_query.from_user.id] = True






@dp.callback_query_handler(lambda c: c.data.startswith('chat_message_unconnect:')) 
async def handle_channel_unmessage(callback_query: types.CallbackQuery):
    # Извлечение user_id из данных колбэка
    user_id = int(callback_query.data.split(':')[-1])

    # Удаление пользователя из словаря подключенных пользователей
    connected_users[user_id] = None  # или используйте какое-то другое значение вместо None, чтобы обозначить отключение

    # Создание клавиатуры для подключения
    keyboard_markup = types.InlineKeyboardMarkup()
    chat_message_connect = types.InlineKeyboardButton('Подключиться', callback_data=f'chat_message_connect:{user_id}')
    keyboard_markup.row(chat_message_connect)
    
    # Отправка сообщения пользователю
    await bot.send_message(user_id, f'Админ отключился')
    await bot.send_message(callback_query.from_user.id, f'Отключение от пользователя {user_id} - успешно!', reply_markup=keyboard_markup)





@dp.message_handler()
async def handle_all_messages(message: types.Message):
    user_id = message.from_user.id

    # Если пользователь подключен, отправляем сообщение администратору и всем пользователям
    if connected_users.get(user_id, False):
        admin_chat_id = 6424595615  # Замените на ваш реальный идентификатор чата администратора

        # Отправка сообщения администратору
        await bot.send_message(admin_chat_id, f'Пользователь {user_id}: {message.text}')

        # Отправка сообщения всем подключенным пользователям, пока администратор подключен
    
        for user_chat_id, connected in connected_users.items():
            if connected and user_chat_id != user_id and user_chat_id != admin_chat_id:
                await bot.send_message(user_chat_id, f'Администратор: {message.text}')










@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def handle_json_message(message: types.Message):
    try:
        # Пытаемся разобрать JSON из текстового сообщения
        json_data = json.loads(message.text)

        # Проверяем наличие обязательных полей в JSON
        if 'user_id' in json_data and 'message' in json_data:
            user_id = json_data['user_id']
            response_message = json_data['message']

            # Ваша логика обработки сообщения
            # Например, отправка ответа пользователю по user_id
            await bot.send_message(user_id, f"Администратор: {response_message}")

        else:
            await bot.send_message(message.chat.id, "Неверный формат JSON. Пожалуйста, укажите 'user_id' и 'message'.")
    except json.JSONDecodeError:
        await bot.send_message(message.chat.id, "Ошибка при разборе JSON. Пожалуйста, укажите корректный JSON.")



#Вызов админа КОН


@dp.callback_query_handler(lambda c: c.data == 'inline_curce') 
async def handle_chat_message(callback_query: types.CallbackQuery):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Назад", callback_data='go_back'))
    cny = await result_cny()
    await callback_query.message.edit_text(f'Курс <b>¥</b> в данный момент: {cny}', parse_mode="html", reply_markup=markup)
    




@dp.callback_query_handler(lambda c: c.data == 'inline_photo') 
async def handle_chat_message(callback_query: types.CallbackQuery):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Назад", callback_data='go_back'))
    await callback_query.message.edit_text('Отпарвьте <b>Фото</b>:', parse_mode="html", reply_markup=markup)
    print('Получил фото')
    await InputUserData.inline_shoes_step_2.set()


@dp.message_handler(content_types=types.ContentType.PHOTO, state=InputUserData.inline_shoes_step_2)
async def handle_photo(message: types.Message, state: FSMContext):
    # Получаем информацию о фотографии
    photo = message.photo[-1]
    
    # Получаем уникальное имя файла
    file_id = photo.file_id
    file = await bot.get_file(file_id)
    photo_path = file.file_path
    downloaded_file = await bot.download_file(photo_path)
    
    # Определяем путь для сохранения фото
    save_path = f"/var/www/www-root/data/Personal_Folder/tg_bots/test_Brand_Games_bot/photos/{file_id}.jpg"
    
    # Сохраняем фото
    with open(save_path, 'wb') as new_file:
        new_file.write(downloaded_file.read())
    
    # Обновляем текущее сообщение с новой фотографией
    url = save_path
    new_photo = edit_photo_func(url)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Главное меню", callback_data='go_back_to_photo'))
    
    await bot.send_photo(message.chat.id, photo=open(new_photo.name, 'rb'), reply_to_message_id=message.message_id, reply_markup=markup)
    print(f"Фото сохранено и обновлено: {save_path}")
    
    # Очищаем состояние
    await state.finish()






from aiogram import types

questions = [
    {
        "question":"Какой язык программирования вы изучали на курсе?",
        "options":["Python", "Java", "C++", "Mojo"],
        "correct_answer":"Python"
    },
    {
        "question":"Когда SpaceX запустилa Starship?",
        "options":["16.02.2024", "15.03.2024", "14.03.2024", "10.03.2024"],
        "correct_answer":"14.03.2024"
    }
]







# Создаем состояние для отслеживания текущего вопроса
class QuizState(StatesGroup):
    QUESTION = State()

# Определяем обработчик нажатия кнопки "Опрос"
@dp.callback_query_handler(lambda c: c.data == 'inline_test') 
async def start_quiz(callback_query: types.CallbackQuery, state: FSMContext):
    await QuizState.QUESTION.set()  # Устанавливаем состояние на первый вопрос
    await show_question(callback_query.message, 0)  # Отображаем первый вопрос

# Функция для отображения вопроса
async def show_question(message: types.Message, question_index: int):
    question_data = questions[question_index]
    question_text = question_data["question"]
    options = question_data["options"]

    markup = types.InlineKeyboardMarkup()
    for option in options:
        markup.add(types.InlineKeyboardButton(option, callback_data=f'answer_{option}'))

    await message.edit_text(question_text, reply_markup=markup)

# Определяем обработчик ответов на вопросы
@dp.callback_query_handler(state=QuizState.QUESTION)
async def handle_answer(callback_query: types.CallbackQuery, state: FSMContext):
    user_answer = callback_query.data.split('_')[-1]  # Получаем ответ пользователя
    current_state = await state.get_data()
    question_index = current_state.get("question_index", 0)  # Получаем текущий индекс вопроса

    question_data = questions[question_index]
    correct_answer = question_data["correct_answer"]

    if user_answer == correct_answer:
        pass
    else:
        # Обрабатываем неправильный ответ
        pass

    # Переходим к следующему вопросу
    next_question_index = question_index + 1
    if next_question_index < len(questions):
        await show_question(callback_query.message, next_question_index)
        await state.update_data(question_index=next_question_index)  # Обновляем индекс вопроса в состоянии
    else:
        # Если вопросы закончились, выводим результат
        await show_result(callback_query.message, state)


# Функция для отображения результата
async def show_result(message: types.Message, state: FSMContext):
    # Здесь вы можете провести анализ ответов и подсчитать количество правильных и неправильных ответов
    # После этого выведите результат пользователю

    await message.edit_text("Опрос завершен. Вот ваш результат.", reply_markup=None)
    await state.finish()





#Закрытие при кнопке НАЗАД
@dp.callback_query_handler(lambda c: c.data == 'inline_close') 
async def handle_chat_message(callback_query: types.CallbackQuery):
    #Скрываем все меню , Выводим видео и текст Отпарвьте стоимость товара в ¥
    await callback_query.message.edit_text('Стартовое меню <b>закрыто</b>. Всего доброго!', parse_mode='html')
    print('Закрыл')



@dp.callback_query_handler(lambda c: c.data == 'inline_close_admin_panel') 
async def handle_chat_message(callback_query: types.CallbackQuery):
    #Скрываем все меню , Выводим видео и текст Отпарвьте стоимость товара в ¥
    await callback_query.message.edit_text('Админ панель <b>закрыта</b>', parse_mode='html')
    print('Закрыл')

#При передумывании категории
@dp.callback_query_handler(lambda c: c.data == 'go_back', state='*')
async def handle_go_back(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text('<b>Выберете действие: </b>', parse_mode='html', reply_markup=category_orders())
    await state.finish()  # Сброс состояния

#При возвращении к фото 
@dp.callback_query_handler(lambda c: c.data == 'go_back_to_photo', state='*')
async def handle_go_back(callback_query: types.CallbackQuery, state: FSMContext):
        # Получаем текущую разметку сообщения
    current_markup = callback_query.message.reply_markup
    
    # Если разметка существует и содержит кнопки
    if current_markup and current_markup.inline_keyboard:
        # Удаляем кнопки
        current_markup.inline_keyboard.clear()
    
    # Редактируем сообщение, оставляя фотографию и текст, но убирая кнопки
    await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, reply_markup=current_markup)

    
    await callback_query.message.answer('<b>Выберете действие: </b>', parse_mode='html', reply_markup=category_orders())
    await state.finish()  # Сброс состояния








if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)




