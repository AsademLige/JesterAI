from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.data.dictionary import Dictionary
from src.data.config import Prefs

prefs = Prefs()
dict = Dictionary()

class CreateStickerSetKeyboard():
    def __init__(self):
        pass

    # @property
    # def project_create_cancel(self) -> ReplyKeyboardMarkup:
    #     return ReplyKeyboardMarkup(
    #             keyboard=[
    #                     [KeyboardButton(text=Dictionary.use_this)],
    #         ],
    #         resize_keyboard=True,
    #         one_time_keyboard=True,
    #         input_field_placeholder=Dictionary.send_sticker_placeholder
    #     )

    @property
    def clip_text_choice(self) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        
        builder.add(InlineKeyboardButton(
                text=dict.skip,
                callback_data="skip")
            )
            
        builder.adjust(1)
        
        return builder.as_markup()
    
    @property
    def media_choice(self) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        
        builder.add(InlineKeyboardButton(
                text=dict.use_this,
                callback_data="use_this")
            )
            
        builder.adjust(1)
        
        return builder.as_markup()