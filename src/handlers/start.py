from src.handlers.commands import Commands as cn
from src.services.data_base.db import DataBase
from src.data.dictionary import Dictionary
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.types import Message
from src.data.config import Prefs
from aiogram import Router, F
from aiogram import Bot

prefs = Prefs()
bot = Bot(token=prefs.bot_token)
dict = Dictionary()
db = DataBase()
rt = Router()

### Запустить бота
@rt.message(Command(cn.start))
async def start_handler(message: Message):
    await message.answer(dict.bot_description)

### Что умеет бот
@rt.message(Command(cn.help))
async def help_handler(message: Message):
    if (await db.is_admin(message.from_user.id)):
        await message.answer("Вот список доступных тебе специальных команд: \n" \
        "/create_sticker_set - Создать набор стикеров\n" \
        "/edit_sticker_set - Изменить набор стикеров")
    else:
        await message.answer(dict.bot_description, parse_mode=ParseMode.HTML)

    