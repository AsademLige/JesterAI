from src.domain.controllers.battle_controller import BattlePhases
from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.models.battle_member_model import BodyParts
from src.keyboards.callback_fabrics import BattleCF
from aiogram.types import InlineKeyboardMarkup
from aiogram.types import InlineKeyboardButton
from src.data.dictionary import Dictionary
from src.models.user_model import User
from src.data.config import Prefs
from typing import List, Tuple

prefs = Prefs()
dict = Dictionary()

class BattleKeyboard():
    def __init__(self):
        pass

    def hunt_start(self, user:User) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(text="⚔️ Резня!",
                callback_data=BattleCF(action="fight",
                                        style="danger",
                                        user_id=user.tg_id).pack()))
        builder.add(InlineKeyboardButton(text="💨 Побег",
                callback_data=BattleCF(action="escape", 
                                        user_id=user.tg_id).pack()))
        builder.adjust(2) 
        return builder.as_markup()
    
    def parts_selector(self, user:User, phase:BattlePhases) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        phase_icon:str = '🗡' if phase == BattlePhases.ATTACK else '🛡'
        action:str = "attack" if phase == BattlePhases.ATTACK else "defense"
        
        builder.add(InlineKeyboardButton(text=f"{phase_icon} Тыква",
                callback_data=BattleCF(action=action, part=BodyParts.HEAD.value,
                                       user_id=user.tg_id).pack()))
        
        builder.add(InlineKeyboardButton(text=f"{phase_icon} Грудь",
                callback_data=BattleCF(action=action, part=BodyParts.CHEST.value,
                                       user_id=user.tg_id).pack()))
        
        builder.add(InlineKeyboardButton(text=f"{phase_icon} Ноги",
                callback_data=BattleCF(action=action, part=BodyParts.KNEES.value,
                                       user_id=user.tg_id).pack()))

        builder.adjust(3) 
        return builder.as_markup()