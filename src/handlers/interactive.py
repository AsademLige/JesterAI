from src.domain.utils.text_processing import TextProcessing as tp
from aiogram.types import Message, CallbackQuery
from src.handlers.commands import Commands as cn
from aiogram.filters import Command, StateFilter
from src.services.data_base.db import DataBase
from typing import List, Any, Dict, Optional
from src.models.user_model import UserModel
from aiogram.fsm.context import FSMContext
from src.data.dictionary import Dictionary
from aiogram.enums import ParseMode
from aiogram.types import Message
from src.data.config import Prefs
import random

from aiogram import Router, F
from aiogram import Bot

prefs = Prefs()
dict = Dictionary()
bot = Bot(token=prefs.bot_token)
db = DataBase()
rt = Router()

###Получение информации о пользователе
@rt.message(StateFilter(None), Command(cn.me))
async def user_information(message: Message, state: FSMContext):
    await message.answer(dict.user_information(await db.get_user(message.from_user.id)),
                         parse_mode=ParseMode.MARKDOWN_V2)
    
###Попробовать изменить текущий member размер 
@rt.message(StateFilter(None), Command(cn.pencil))
async def pencil_change(message: Message, state: FSMContext):
    action:int = random.randrange(0, 2)
    print(f"{action}")
    length_change:int = (random.randrange(1, 4) * -1) if (action == 1) else random.randrange(1, 7)
    
    user: UserModel = await db.get_user(message.from_user.id)

    if (await db.update_user_member(user, user.length + length_change)):
        await message.answer(dict.length_change(user.tg_name, length_change),
                            parse_mode=ParseMode.MARKDOWN_V2)


