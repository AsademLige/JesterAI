from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.keyboards.callback_fabrics import DiceGameCF
from aiogram.types import InlineKeyboardMarkup
from aiogram.types import InlineKeyboardButton
from src.data.dictionary import Dictionary
from src.data.config import Prefs
from typing import List, Any

prefs = Prefs()
dict = Dictionary()

class InteractiveKeyboard():
    def __init__(self):
        pass
    
    def dice_choice(self) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.add(InlineKeyboardButton(text=dict.dice_smaller,
                callback_data=DiceGameCF(action="smaller").pack()))

        builder.add(InlineKeyboardButton(text=dict.dice_equal,
            callback_data=DiceGameCF(action="equal").pack()))

        builder.add(InlineKeyboardButton(text=dict.dice_bigger,
            callback_data=DiceGameCF(action="bigger").pack()))
    
        builder.add(InlineKeyboardButton(text=dict.rules,
            callback_data=DiceGameCF(action="rules").pack()))

        builder.add(InlineKeyboardButton(text=dict.exit,
            callback_data=DiceGameCF(action="exit").pack()))
        
        builder.adjust(3, 2) 
        
        return builder.as_markup()