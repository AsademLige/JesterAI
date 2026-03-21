from src.domain.controllers.rights_controller import RightsController
from src.keyboards.interactive_keyboard import InteractiveKeyboard
from src.keyboards.callback_fabrics import DiceGameCF
from src.models.user_stats_model import UserStats
from src.handlers.commands import Commands as cn
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from src.services.data_base.db import DataBase
from aiogram.fsm.context import FSMContext
from src.data.dictionary import Dictionary
from datetime import timedelta, datetime
from src.domain.utils.utils import Utils
from src.models.user_model import User
from aiogram.enums import ParseMode
from src.data.config import Prefs
from aiogram.types import Message
from typing import List
import asyncio
import random
import math

from aiogram import Router, F
from aiogram import Bot

prefs = Prefs()
dict = Dictionary()
bot = Bot(token=prefs.bot_token)
interactive_kb = InteractiveKeyboard()
db = DataBase()
rt = Router()

member_change_reset_time:int = 24
    
###Попробовать изменить текущий member размер 
@rt.message(StateFilter(None), Command(cn.pencil))
async def pencil_change(message: Message, state: FSMContext):
    user: User = await db.get_user_by_chat_id(message.from_user.id, message.chat.id)
    await message.delete()
    delta:timedelta = Utils.get_last_member_check_delta(user.last_length_check)

    if (math.floor(delta.total_seconds() / 3600) < 0):
        answer = await bot.send_message(user.chat_id, 
                                        dict.timer_message(user, Utils.timedelta_to_hhmm(delta)), 
                             parse_mode=ParseMode.HTML)
        await Utils.delete_old_message([answer], 10)
        return

    length_change:int = random.choice([-4, -3, -2, - 1, 1, 2, 3, 4, 5, 6])

    if (await db.update_user(user, {
        "length": user.length + length_change,
        "last_length_check" : datetime.now()
    })):
        answer = await bot.send_message(user.chat_id, dict.length_change(user.tg_name, length_change),
                            parse_mode=ParseMode.HTML)

###Команда отображения таблицы лидеров
@rt.message(StateFilter(None), Command(cn.leaderboard))
async def leaderboard(message: Message, state: FSMContext):
    users: List[User] = await db.get_all_users_by_chat(message.chat.id)
    sorted_users: List[User] = sorted(users, 
                                            key=lambda u: u.length,
                                            reverse=True)
    await message.delete()
    answer = await bot.send_message(users[0].chat_id, dict.leaderboard(sorted_users),
                        parse_mode=ParseMode.HTML)
    await Utils.delete_old_message([answer], 15)

###Команда отображения списка выигрышей
@rt.message(StateFilter(None), Command(cn.winners_log))
async def winners_log(message: Message, state: FSMContext):
    logs, total_pages, users = await db.get_winners_logs_page(message.chat.id, 1)
    chat_id:int = message.chat.id
    await message.delete()

    if not logs:
        await bot.send_message(chat_id, "📭 Записей пока нет")
        return
    
    await bot.send_message(chat_id, dict.winners_logs(logs, users), 
                         reply_markup=interactive_kb.get_pagination_keyboard(1, total_pages), 
                         parse_mode=ParseMode.HTML)
    
# Обработчик нажатий на кнопки пагинации
@rt.callback_query(lambda c: c.data.startswith('page_'))
async def process_pagination(callback: CallbackQuery):
    page = int(callback.data.split('_')[1])

    logs, total_pages, users = await db.get_winners_logs_page(callback.message.chat.id, page)

    await callback.message.edit_text(dict.winners_logs(logs, users), 
                         reply_markup=interactive_kb.get_pagination_keyboard(page, total_pages), 
                         parse_mode=ParseMode.HTML)
    await callback.answer()

@rt.callback_query(lambda c: c.data.startswith('close_pagination'))
async def delete_winners_log_table(callback: CallbackQuery):
    await callback.message.delete()
    


