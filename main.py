import asyncio
from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import sqlite3
import logging

from config import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

logging.basicConfig(level=logging.INFO)

# Определяем состояние для FSM
class Form(StatesGroup):
    name = State()
    age = State()
    grade = State()

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('school_data.db')
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER NOT NULL,
    grade TEXT NOT NULL)
    ''')
    conn.commit()
    conn.close()

init_db()

@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await message.answer("Привет! Как тебя зовут?")
    await state.set_state(Form.name)

@router.message(Form.name)
async def name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Сколько тебе лет?")
    await state.set_state(Form.age)

@router.message(Form.age)
async def age(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer("В каком классе ты учишься?")
    await state.set_state(Form.grade)

@router.message(Form.grade)
async def grade(message: Message, state: FSMContext):
    await state.update_data(grade=message.text)
    user_data = await state.get_data()

    conn = sqlite3.connect('school_data.db')
    cur = conn.cursor()
    cur.execute('''
       INSERT INTO students (name, age, grade) VALUES (?, ?, ?)''',
                (user_data['name'], user_data['age'], user_data['grade']))
    conn.commit()
    conn.close()

    await message.answer(f"Спасибо! Данные сохранены: Имя - {user_data['name']}, Возраст - {user_data['age']}, Класс - {user_data['grade']}")
    await state.clear()

@router.message(Command("info"))
async def info(message: Message):
    await message.answer(
        "Этот бот собирает информацию о студентах, включая имя, возраст и класс. "
        "Вы можете использовать следующие команды:\n"
        "/start - Начать взаимодействие с ботом\n"
        "/info - Получить информацию о возможностях бота"
    )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())