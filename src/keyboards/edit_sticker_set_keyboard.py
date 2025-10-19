from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.keyboards.callback_fabrics import StickerSetCF
from src.models.sticker_set_model import StickerSetModel
from aiogram.types import InlineKeyboardMarkup
from src.data.dictionary import Dictionary
from src.data.config import Prefs
from typing import List

prefs = Prefs()

class EditStickerSetKeyboard():
    def __init__(self):
        pass

    def sticker_set_list_button(self, sticker_sets: List[StickerSetModel]) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        for sticker_set in sticker_sets:
            builder.button(text=sticker_set.short_name,
                callback_data=StickerSetCF(action="choice", short_name=sticker_set.short_name))
            
        builder.button(text=Dictionary.exit,
            callback_data=StickerSetCF(action="exit"))
        
        builder.adjust(2)
        
        return builder.as_markup()
    
    def exit(self) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text=Dictionary.exit,
            callback_data=StickerSetCF(action="exit"))
        builder.adjust(1)
        return builder.as_markup()
    
    def back(self, short_name:str) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text=Dictionary.back,
            callback_data=StickerSetCF(action="choice", short_name=short_name))
        builder.adjust(1)
        return builder.as_markup()
    
    def confirm_delete(self, short_name:str) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text=Dictionary.delete_sticker_set,
            callback_data=StickerSetCF(action="confirm_delete_set"))
        builder.button(text=Dictionary.back,
            callback_data=StickerSetCF(action="choice", short_name=short_name))
        builder.adjust(2)
        return builder.as_markup()
    
    def edit_sticker_set_command_button(self, short_name:str) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        
        builder.button(text=Dictionary.add_sticker_to_set,
            callback_data=StickerSetCF(action="add_sticker", short_name=short_name))
        
        builder.button(text=Dictionary.delete_sticker_from_set,
            callback_data=StickerSetCF(action="delete_sticker", short_name=short_name))
        
        builder.button(text=Dictionary.delete_sticker_set,
            callback_data=StickerSetCF(action="delete_set", short_name=short_name))

        builder.button(text=Dictionary.exit,
            callback_data=StickerSetCF(action="exit"))
        
        builder.adjust(2)
        
        return builder.as_markup()