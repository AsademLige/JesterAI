from src.domain.controllers.rights_controller import RightsController
from src.keyboards.interactive_keyboard import InteractiveKeyboard
from src.domain.states.dice_game_set import DiceGameSet
from src.keyboards.callback_fabrics import DiceGameCF
from src.handlers.commands import Commands as cn
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from src.services.data_base.db import DataBase
from src.models.user_model import User
from src.models.user_stats_model import UserStats
from aiogram.fsm.context import FSMContext
from src.data.dictionary import Dictionary
from datetime import timedelta, datetime
from src.domain.utils.utils import Utils
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