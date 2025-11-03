from src.domain.utils.text_processing import TextProcessing as tp
from aiogram.types import Message, CallbackQuery
from src.handlers.commands import Commands as cn
from aiogram.filters import Command, StateFilter
from src.services.data_base.db import DataBase
from typing import List, Any, Dict, Optional
from src.models.user_model import UserModel
from aiogram.fsm.context import FSMContext
from src.data.dictionary import Dictionary
from datetime import timedelta, datetime
from aiogram.enums import ParseMode
from aiogram.types import Message
from src.data.config import Prefs
import random
import math

from aiogram import Router, F
from aiogram import Bot

prefs = Prefs()
dict = Dictionary()
bot = Bot(token=prefs.bot_token)
db = DataBase()
rt = Router()

member_change_reset_time:int = 24

###Получение информации о пользователе
@rt.message(StateFilter(None), Command(cn.me))
async def user_information(message: Message, state: FSMContext):
    user: UserModel = await db.get_user(message.from_user.id)
    print(user.last_length_check)
    await message.answer(dict.user_information(user),
                         parse_mode=ParseMode.HTML)
    
###Попробовать изменить текущий member размер 
@rt.message(StateFilter(None), Command(cn.pencil))
async def pencil_change(message: Message, state: FSMContext):
    user: UserModel = await db.get_user(message.from_user.id)
    last_member_check_delta:int = get_last_member_check_delta(user.last_length_check)
    if (last_member_check_delta < 0):
        await message.answer(dict.member_change_not_reset(last_member_check_delta * -1), 
                             parse_mode=ParseMode.HTML)
        return

    action:int = random.randrange(0, 2)
    length_change:int = (random.randrange(1, 4) * -1) if (action == 1) else random.randrange(1, 7)

    if (await db.update_user_member(user, user.length + length_change)):
        await message.answer(dict.length_change(user.tg_name, length_change),
                            parse_mode=ParseMode.HTML)
        
def get_last_member_check_delta(last_length_check: datetime) -> int:
    delta:timedelta = (datetime.now() - (last_length_check + timedelta(hours=member_change_reset_time)))
    return math.floor(delta.total_seconds() /3600)


