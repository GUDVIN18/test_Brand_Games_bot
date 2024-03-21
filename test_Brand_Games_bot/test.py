from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Укажите токен вашего бота
BOT_TOKEN = "7024236686:AAFZUIIE3JoDbBjcu7SyIXcmWVc0GzUNQNU"

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# Создание состояний для FSM (Finite State Machine)
class TestState(StatesGroup):
    Question = State()

# Список вопросов и ответов
questions = [
    {
        "question": "Что такое AI?",
        "options": ["Искусственный Интеллект", "Автоматическая Интеграция", "Альтернативная Информация"],
        "correct_answer": "Искусственный Интеллект"
    },
    {
        "question": "Какой язык программирования вы предпочитаете?",
        "options": ["Python", "Java", "JavaScript"],
        "correct_answer": "Python"
    }
    # добавьте другие вопросы здесь
]

# Обработчик команды /start для начала теста
@dp.message_handler(commands=['start'])
async def start_test(message: types.Message):
    # Начинаем тест с первого вопроса
    await ask_question(message.chat.id, 0)

# Функция для отправки вопроса
async def ask_question(chat_id, question_index):
    question = questions[question_index]
    options = question["options"]

    # Создаем клавиатуру с вариантами ответов
    keyboard = InlineKeyboardMarkup(row_width=1)
    for option in options:
        keyboard.add(InlineKeyboardButton(option, callback_data=option))

    # Отправляем вопрос с вариантами ответов
    await bot.send_message(chat_id, question["question"], reply_markup=keyboard)

    # Переходим в состояние ожидания ответа на вопрос
    await TestState.Question.set()

# Обработчик ответа на вопрос
@dp.callback_query_handler(state=TestState.Question)
async def handle_answer(callback_query: types.CallbackQuery, state: FSMContext):
    # Получаем ответ пользователя и правильный ответ на текущий вопрос
    user_answer = callback_query.data
    question_index = callback_query.message.message_id - 1
    question = questions[question_index]
    correct_answer = question["correct_answer"]

    # Проверяем ответ пользователя
    if user_answer == correct_answer:
        response = "Правильно!"
    else:
        response = "Неправильно. Правильный ответ: " + correct_answer

    # Отправляем ответ пользователю
    await bot.send_message(callback_query.from_user.id, response)

    # Если есть следующий вопрос, отправляем его
    next_question_index = question_index + 1
    if next_question_index < len(questions):
        await ask_question(callback_query.from_user.id, next_question_index)
    else:
        # Если вопросы закончились, завершаем тест
        await state.finish()
        await bot.send_message(callback_query.from_user.id, "Тест завершен.")

# Запуск бота
if __name__ == "__main__":
    import asyncio
    from aiogram import executor
    loop = asyncio.get_event_loop()
    try:
        executor.start_polling(dp, loop=loop, skip_updates=True)
    finally:
        loop.close()
