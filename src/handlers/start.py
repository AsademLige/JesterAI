from src.domain.states.create_sticker_set import CreateStickerSet
from src.domain.controllers.user_controller import UserController
from aiogram.filters import Command, StateFilter
from src.handlers.commands import Commands as cn
from src.services.data_base.db import DataBase
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from src.data.config import Prefs
from aiogram import Router, F
from aiogram import Bot

prefs = Prefs()
bot = Bot(token=prefs.bot_token)
db = DataBase()
rt = Router()

### Запустить бота
@rt.message(Command(cn.start))
async def start_handler(message: Message):
    await message.answer("Я тебе не какая-то бездушная машина, конкретнее вопрос задавай!")

### Что умеет бот
@rt.message(Command(cn.help))
async def help_handler(message: Message):
    await show_help(message)

### Методы
async def show_help(message: Message):
    await message.answer("Я пока нихуя не умею")