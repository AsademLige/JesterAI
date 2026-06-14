from apps.tg_bot.keyboards.callback_fabrics import DiceGameCF, GambaChoiceCF, GladiatorsCF, TrashLotoCF
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup
from aiogram.types import InlineKeyboardButton
from core.consts.dictionary import Dictionary
from core.data.models.user_model import User
from core.consts.config import Prefs
from typing import List, Tuple

prefs = Prefs()
dict = Dictionary()

class GambaHouseKeyboard():
    def __init__(self):
        pass

    def gamba_choice(self, user:User) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.add(InlineKeyboardButton(text="🎰 Треш-лото",
                callback_data=TrashLotoCF(action="trash_loto",
                                         user_id=user.tg_id).pack()))
        
        builder.add(InlineKeyboardButton(text="🎲 Кубики",
                callback_data=DiceGameCF(action="dice_game",
                                         user_id=user.tg_id).pack()))
        
        builder.add(InlineKeyboardButton(text="🏟️ Арена",
                callback_data=GladiatorsCF(action="gladiators",
                                         user_id=user.tg_id).pack()))
        
        builder.add(InlineKeyboardButton(text=dict.exit,
                callback_data=GambaChoiceCF(action="exit",
                                         user_id=user.tg_id).pack()))

        builder.adjust(2, 2) 
        return builder.as_markup()
    
    def dice_choice(self, user:User) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.add(InlineKeyboardButton(text=dict.dice_smaller,
                callback_data=DiceGameCF(action="smaller",
                                         user_id=user.tg_id).pack()))

        builder.add(InlineKeyboardButton(text=dict.dice_equal,
            callback_data=DiceGameCF(action="equal",
                                     user_id=user.tg_id).pack()))

        builder.add(InlineKeyboardButton(text=dict.dice_bigger,
            callback_data=DiceGameCF(action="bigger",
                                     user_id=user.tg_id).pack()))
    
        builder.add(InlineKeyboardButton(text=dict.rules,
            callback_data=DiceGameCF(action="rules",
                                     user_id=user.tg_id).pack()))

        builder.add(InlineKeyboardButton(text=dict.exit,
            callback_data=DiceGameCF(action="exit",
                                     user_id=user.tg_id).pack()))
        
        builder.adjust(3, 2) 
        return builder.as_markup()