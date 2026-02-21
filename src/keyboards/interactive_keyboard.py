from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.keyboards.callback_fabrics import DiceGameCF
from aiogram.types import InlineKeyboardMarkup
from aiogram.types import InlineKeyboardButton
from src.data.dictionary import Dictionary
from src.data.config import Prefs

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
    
    def get_pagination_keyboard(self, current_page: int, total_pages: int, 
                            callback_prefix: str = "page") -> InlineKeyboardMarkup:
        """Создать клавиатуру для пагинации"""
        builder = InlineKeyboardBuilder()
        
        # Кнопка "Назад"
        if current_page > 1:
            builder.add(InlineKeyboardButton(
                text = "◀️ Назад", 
                callback_data = f"{callback_prefix}_{current_page-1}"
            ))
        
        # Информация о текущей странице
        builder.add(InlineKeyboardButton(
            text = f"{current_page}/{total_pages}", 
            callback_data="current_page"
        ))
        
        # Кнопка "Вперед"
        if current_page < total_pages:
            builder.add(InlineKeyboardButton(
                text = "Вперед ▶️", 
                callback_data=f"{callback_prefix}_{current_page+1}"
            ))

        builder.add(InlineKeyboardButton(text = "❌ Закрыть", 
                                         callback_data="close_pagination"))
        
        builder.adjust(3, 1) 
        
        return builder.as_markup()