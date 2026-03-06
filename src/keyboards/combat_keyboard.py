from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.keyboards.callback_fabrics import CombatCF
from aiogram.types import InlineKeyboardMarkup
from aiogram.types import InlineKeyboardButton
from src.data.dictionary import Dictionary
from src.models.user_model import User
from src.data.config import Prefs
from typing import List, Tuple

prefs = Prefs()
dict = Dictionary()

class CombatKeyboard():
    def __init__(self):
        pass

    def hunt_start(self, user:User) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(text="⚔️ Резня!",
                callback_data=CombatCF(action="fight", 
                                          user_id=user.tg_id).pack()))
        builder.add(InlineKeyboardButton(text="💨 Побег",
                callback_data=CombatCF(action="escape", 
                                          user_id=user.tg_id).pack()))
        builder.adjust(2) 
        return builder.as_markup()