from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.keyboards.callback_fabrics import StickerSetCF
from src.models.sticker_set_model import StickerSet
from aiogram.types import InlineKeyboardMarkup
from src.data.dictionary import Dictionary
from src.data.config import Prefs
from typing import List

prefs = Prefs()
dict = Dictionary()

class EditStickerSetKeyboard():
    def __init__(self):
        pass

    def sticker_set_list_button(self, sticker_sets: List[StickerSet]) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        for set in sticker_sets:
            builder.button(text=set.short_name,
                callback_data=StickerSetCF(action="choice", id=set.id))
            
        builder.button(text=dict.exit,
            callback_data=StickerSetCF(action="exit"))
        
        builder.adjust(2)
        
        return builder.as_markup()
    
    def exit(self) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text=dict.exit,
            callback_data=StickerSetCF(action="exit"))
        builder.adjust(1)
        return builder.as_markup()
    
    def back(self, id) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text=dict.back,
            callback_data=StickerSetCF(action="choice", id=id))
        builder.adjust(1)
        return builder.as_markup()
    
    def confirm_delete(self, id) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text=dict.delete_sticker_set,
            callback_data=StickerSetCF(action="confirm_delete_set"))
        builder.button(text=dict.back,
            callback_data=StickerSetCF(action="choice", id=id))
        builder.adjust(2)
        return builder.as_markup()
    
    def edit_sticker_set_command_button(self, id) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        
        builder.button(text=dict.add_sticker_to_set,
            callback_data=StickerSetCF(action="add_sticker", id=id))
        
        builder.button(text=dict.delete_sticker_from_set,
            callback_data=StickerSetCF(action="delete_sticker", id=id))
        
        builder.button(text=dict.delete_sticker_set,
            callback_data=StickerSetCF(action="delete_set", id=id))

        builder.button(text=dict.exit,
            callback_data=StickerSetCF(action="exit"))
        
        builder.adjust(2)
        
        return builder.as_markup()