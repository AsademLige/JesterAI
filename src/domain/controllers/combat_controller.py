from src.domain.utils.text_processing import TextProcessing as tp
from src.services.data_base.db import DataBase
from aiogram.types import Message, User, Chat
from src.data.dictionary import Dictionary
from typing import List, Optional, Union
from src.models.monster_model import Monster
from src.data.config import Prefs
from random import Random
from aiogram import Bot
from enum import Enum

class CombatMode(Enum):
    HUNT = 0
    DUEL = 1

class CombatController():
    db = DataBase()
    dict = Dictionary()
    prefs = Prefs()
    bot = Bot(token=prefs.bot_token)
    members:List[Union[Monster, User]]

    history:List[Message] = []

    

    def __init__(self, members:List[Union[Monster, User]]):
        self.members = members
        pass

    def health_bar(self, current, maximum, length=10):
        """Создает полоску здоровья"""
        filled_bars = int((current / maximum) * length)
        filled_bars = min(filled_bars, length)
        return "▰" * filled_bars + "□" * (length - filled_bars)