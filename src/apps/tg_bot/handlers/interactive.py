from apps.tg_bot.keyboards.interactive_keyboard import InteractiveKeyboard
from features.user.data.repository.gino_user_repository import GinoUserRepository
from features.user.data.dtos.user_dto import User
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from apps.tg_bot.commands import Commands as cn
from core.consts.dictionary import Dictionary
from aiogram.fsm.context import FSMContext
from core.data.data_base import DataBase
from typing import Dict, List, Tuple
from core.consts.config import Prefs
from aiogram.enums import ParseMode
from core.utils.utils import Utils
from aiogram.types import Message
from datetime import datetime
from aiogram import Router, F
from aiogram import Bot
import random


prefs = Prefs()
dict = Dictionary()
bot = Bot(token=prefs.bot_token)
interactive_kb = InteractiveKeyboard()
marked_users:Dict[int, Tuple[datetime, datetime]] = {}
user_repo:GinoUserRepository = GinoUserRepository()
db = DataBase()
rt = Router()

###Команда отображения таблицы лидеров
@rt.message(StateFilter(None), Command(cn.leaderboard))
async def leaderboard(message: Message, state: FSMContext):
    users: List[User] = await user_repo.get_users(message.chat.id)
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


