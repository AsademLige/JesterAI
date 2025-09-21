from src.domain.states.create_sticker_set import CreateStickerSet
from aiogram.filters import Command, StateFilter
from src.services.data_base.db import DataBase
from src.handlers.commands import Commands as cn
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from src.data.config import Prefs
from aiogram import Router, F
from aiogram import Bot

prefs = Prefs()
bot = Bot(token=prefs.bot_token)
db = DataBase()
rt = Router()

@rt.message(StateFilter(None), Command(cn.create_sticker_set))
async def create_project_set_name_handler(message: Message, state: FSMContext):
    await state.set_state(CreateStickerSet.set_short_name)
    await message.answer("✏️ Введи короткое название стикер-пака латиницей: ")

### Выбор репозитория для проекта
@rt.message(CreateStickerSet.set_title)
async def create_project_set_gitlab_handler(message: Message, state: FSMContext):
    if not (await validate_name(message, state)): 
        await message.answer("🔻 Недопустимые символы в названии, попробуй другое название")
        return

async def validate_name(message: Message, state: FSMContext) -> str:
    valid = True
    for c in message.text:
        if (c in ['/', '\\', '*', '(', ')', '.', '@', '`', ]): valid = False

    return valid