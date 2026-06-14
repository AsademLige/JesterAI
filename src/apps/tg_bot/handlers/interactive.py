from apps.tg_bot.keyboards.interactive_keyboard import InteractiveKeyboard
from apps.tg_bot.commands import Commands as cn
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from core.data.datasource import DataBase
from aiogram.fsm.context import FSMContext
from core.consts.dictionary import Dictionary
from datetime import timedelta, datetime
from core.utils.utils import Utils
from core.data.models.user_model import User
from aiogram.enums import ParseMode
from typing import Dict, List, Tuple
from core.consts.config import Prefs
from aiogram.types import Message
import random
import math

from aiogram import Router, F
from aiogram import Bot

prefs = Prefs()
dict = Dictionary()
bot = Bot(token=prefs.bot_token)
interactive_kb = InteractiveKeyboard()
marked_users:Dict[int, Tuple[datetime, datetime]] = {}
db = DataBase()
rt = Router()

member_change_reset_time:int = 24
    
###Попробовать изменить текущий member размер 
@rt.message(StateFilter(None), Command(cn.pencil))
async def pencil_change(message: Message, state: FSMContext):
    user: User = await db.get_user_by_chat_id(message.from_user.id, message.chat.id)
    await message.delete()
    delta:timedelta = Utils.get_time_delta(user.last_length_check)

    if (math.floor(delta.total_seconds() / 3600) < 0):
        answer = await bot.send_message(user.chat_id, 
                                        dict.timer_message(user, Utils.timedelta_to_hhmm(delta)), 
                             parse_mode=ParseMode.HTML)
        await Utils.delete_old_message([answer], 10)
        return

    length_change:int = random.choice([-4, -3, -2, - 1, 1, 2, 3, 4, 5, 6])
    length_from_behind:int = 0

    if (await db.get_place_in_top_by_member(user.tg_id, user.chat_id) > 3):
        length_from_behind = random.choice([0, 1])

    if (await db.update_user(user, {
        User.length.name: user.length + length_change + length_from_behind,
        User.last_length_check.name : datetime.now()
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

@rt.message(~F.text.contains("/"))
async def mark_user(message: Message):
    if (message.from_user.id in marked_users):
        if ((datetime.now() - marked_users[message.from_user.id][0]).total_seconds() > 600):
            del marked_users[message.from_user.id]
        else:
            if ((datetime.now() - marked_users[message.from_user.id][1]).total_seconds() > 30):
                marked_users[message.from_user.id] = (marked_users[message.from_user.id][0], datetime.now())
                await message.answer(random.choice(["👆Этот в харче👆", "👆Этот натурал👆", 
                                                    "👆Этот натурал👆", "👆Этот из IBS👆", 
                                                    "👆Этот техник стажер👆", "👆Этого Снежа поцелует👆",
                                                    "👆Этому под хвост накончают👆",
                                                    "👆Этот микрочлен👆"]))


