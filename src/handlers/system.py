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

from aiogram import Router, F
from aiogram import Bot

prefs = Prefs()
dict = Dictionary()
bot = Bot(token=prefs.bot_token)
db = DataBase()
rt = Router()

