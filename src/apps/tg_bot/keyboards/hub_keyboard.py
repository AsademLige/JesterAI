from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_hub_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text="⚔️ Охота", 
                             callback_data="hub_hunt"))
    
    builder.add(InlineKeyboardButton(text="🛒 Торгомат DICKSI", 
                                     callback_data="hub_store"))
    
    builder.add(InlineKeyboardButton(text="🎣 Рыбалка", 
                                     callback_data="fishing"))
    
    builder.adjust(2, 2) 
    return builder.as_markup()