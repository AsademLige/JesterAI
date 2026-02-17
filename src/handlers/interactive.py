from src.domain.utils.text_processing import TextProcessing as tp
from src.handlers.commands import Commands as cn
from aiogram.filters import Command, StateFilter
from src.services.data_base.db import DataBase
from src.models.user_model import UserModel
from aiogram.fsm.context import FSMContext
from src.data.dictionary import Dictionary
from datetime import timedelta, datetime
from aiogram.enums import ParseMode
from aiogram.types import Message
from src.data.config import Prefs
from aiogram.types import Message
from typing import List
import asyncio
import random
import math
import sys

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
    user: UserModel = await db.get_user_by_chat_id(message.from_user.id, message.chat.id)
    place_in_top:int = await db.get_place_in_top_by_member(user.tg_id, user.chat_id)
    await message.answer(dict.user_information(user, place_in_top),
                         parse_mode=ParseMode.HTML)
    
###Попробовать изменить текущий member размер 
@rt.message(StateFilter(None), Command(cn.pencil))
async def pencil_change(message: Message, state: FSMContext):
    user: UserModel = await db.get_user_by_chat_id(message.from_user.id, message.chat.id)
    last_member_check_delta:int = get_last_member_check_delta(user.last_length_check)

    if (last_member_check_delta < 0):
        await message.answer(dict.member_change_not_reset(last_member_check_delta * -1), 
                             parse_mode=ParseMode.HTML)
        return

    action:int = random.randrange(0, sys.maxsize)
    length_change:int = (random.randrange(1, 4) * -1) if (action % 2 == 0) else random.randrange(1, 7)

    if (await db.update_user(user, {
        "length": user.length + length_change,
        "last_length_check" : datetime.now()
    })):
        await message.answer(dict.length_change(user.tg_name, length_change),
                            parse_mode=ParseMode.HTML)

###Команда отображения таблицы лидеров
@rt.message(StateFilter(None), Command(cn.leaderboard))
async def leaderboard(message: Message, state: FSMContext):
    users: List[UserModel] = await db.get_all_users_by_chat(message.chat.id)
    sorted_users: List[UserModel] = sorted(users, 
                                            key=lambda u: u.length,
                                            reverse=True)
    await message.answer(dict.leaderboard(sorted_users),
                        parse_mode=ParseMode.HTML)
        
###Бесполезная трата денег
@rt.message(StateFilter(None), Command(cn.trash_loto))
async def trash_loto(message: Message, state: FSMContext):
    user: UserModel = await db.get_user_by_chat_id(message.from_user.id, message.chat.id)
    if (user.money < 10):
        await message.answer(dict.not_enough_money,
                            parse_mode=ParseMode.HTML)
        return
    
    result = await message.answer_dice(emoji='🎰')
    
    await asyncio.sleep(3) 
    
    value = result.dice.value - 1

    # Индексы: 0=BAR, 1=🍒, 2=🍋, 3=777
    left = value % 4
    middle = (value // 4) % 4
    right = value // 16

    is_minor_win = (left == middle or middle == right)
    is_major_win = (left == middle == right)

    # 777
    if value == 63:
        award =  random.randrange(100, 200)
        if (await db.update_user(user, {"money" : user.money + award - 10})):
            await message.answer(dict.trash_loto_jackpot_money_award(user.tg_name, user.tg_id, award),
                                parse_mode=ParseMode.HTML)
        else: message.answer(dict.trash_loto_error, parse_mode=ParseMode.HTML)
    #тройная комбинаций
    elif is_major_win:
        action = random.choices([1, 2])
        if (action[0] == 1):
            length = random.randrange(5, 10)
            if (await db.update_user(user, {"length": user.length + length, "money" : user.money - 10})):
                await message.answer(dict.trash_loto_major_length_award(user.tg_name, user.tg_id, length),
                                    parse_mode=ParseMode.HTML)
            else: message.answer(dict.trash_loto_error, parse_mode=ParseMode.HTML)
        else:
            award =  random.randrange(50, 100)
            if (await db.update_user(user, {"money" : user.money + award - 10})):
                await message.answer(dict.trash_loto_major_money_award(user.tg_name, user.tg_id, award),
                                    parse_mode=ParseMode.HTML)
            else: message.answer(dict.trash_loto_error, parse_mode=ParseMode.HTML)
    # Проверка на любые две одинаковые подряд
    elif is_minor_win:
        action = random.choices([1, 2])
        if (action[0] == 1):
            length = random.randrange(1, 5)
            if (await db.update_user(user, {"length": user.length + length, "money" : user.money - 10})):
                await message.answer(dict.trash_loto_minor_length_award(user.tg_name, user.tg_id, length),
                                    parse_mode=ParseMode.HTML)
            else: message.answer(dict.trash_loto_error, parse_mode=ParseMode.HTML)
        else:
            award =  random.randrange(10, 20)
            if (await db.update_user(user, {"money" : user.money + award - 10})):
                await message.answer(dict.trash_loto_minor_money_award(user.tg_name, user.tg_id, award),
                                    parse_mode=ParseMode.HTML)
            else: message.answer(dict.trash_loto_error, parse_mode=ParseMode.HTML)
    else:
        if (await db.update_user(user, {"money" : user.money - 10})):
            await message.answer(dict.trash_loto_lose(user.tg_name, user.tg_id),
                                parse_mode=ParseMode.HTML)
        else: message.answer(dict.trash_loto_error, parse_mode=ParseMode.HTML)


        
def get_last_member_check_delta(last_length_check: datetime) -> int:
    delta:timedelta = (datetime.now() - (last_length_check + timedelta(hours=member_change_reset_time)))
    return math.floor(delta.total_seconds() / 3600)


