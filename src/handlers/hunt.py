from src.keyboards.combat_keyboard import CombatKeyboard
from src.domain.controllers.combat_controller import CombatController
from src.models.user_stats_model import UserStats
from src.handlers.commands import Commands as cn
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from src.services.data_base.db import DataBase
from src.models.monster_model import Monster
from aiogram.fsm.context import FSMContext
from src.data.dictionary import Dictionary
from datetime import timedelta, datetime
from src.domain.utils.utils import Utils
from src.models.user_model import User
from aiogram.enums import ParseMode
from src.data.config import Prefs
from aiogram.types import Message
from typing import Any, Dict, List
import asyncio
import random
import math

from aiogram import Router, F
from aiogram import Bot

prefs = Prefs()
dict = Dictionary()
bot = Bot(token=prefs.bot_token)
combat_kb = CombatKeyboard()
db = DataBase()
rt = Router()

started_fights:Dict[int, CombatController] = {}

###Отправиться на охоту
@rt.message(StateFilter(None), Command(cn.hunt))
async def hunt_start(message: Message, state: FSMContext):
    user:User = await db.get_user_by_chat_id(message.from_user.id, message.chat.id)
    await message.delete()

    monster:Monster = await db.get_random_monster()

    global started_fights
    started_fights[user.tg_id] = CombatController([user, monster])

    answer = await bot.send_message(user.chat_id, dict.monster_meeting(monster),
                                    reply_markup=combat_kb.hunt_start(user),
                                    parse_mode=ParseMode.HTML)
    
