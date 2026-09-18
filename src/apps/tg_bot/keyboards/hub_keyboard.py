from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

from features.user.data.dtos.user_dto import User

def get_hub_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text="⚔️ Охота", 
                             callback_data="hub_hunt"))
    
    builder.add(InlineKeyboardButton(text="🛒 Торгомат DICKSI", 
                                     callback_data="hub_store"))
    
    builder.add(InlineKeyboardButton(text="🎣 Рыбалка", 
                                     callback_data="hub_fishing"))
    
    builder.adjust(2, 2) 
    return builder.as_markup()

def fishing_button(params: str = "") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="Рыбачить",
            url=f"https://t.me/KristAIBot/fishing?startapp={params}"
        )
    )

    return builder.as_markup()

def hunt_button(params: str = "") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="На охоту",
            url=f"https://t.me/KristAIBot/hunt?startapp={params}"
        )
    )

    return builder.as_markup()