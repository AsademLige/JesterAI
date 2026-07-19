from features.items.data.models.store_item_dto import StoreItem
from apps.tg_bot.keyboards.callback_fabrics import StoreCF
from aiogram.utils.keyboard import InlineKeyboardBuilder
from features.user.data.dtos.user_dto import User
from aiogram.types import InlineKeyboardMarkup
from core.consts.dictionary import Dictionary
from core.consts.config import Prefs
from typing import List, Tuple

prefs = Prefs()
dict = Dictionary()

class StoreKeyboard():
    def __init__(self):
        pass

    def store_products(self, products: List[StoreItem], user:User) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        for i, product in enumerate(products):
            builder.button(text=f"({i+1}) {product.utf8_icon} " + ("%" if product.is_discount_active else "$"),
                callback_data=StoreCF(action="choice", 
                                      id=product.id,
                                      user_id=user.tg_id))
            
        builder.button(text=dict.exit,
            callback_data=StoreCF(action="exit",
                                  user_id=user.tg_id))
        
        builder.adjust(2)
        
        return builder.as_markup()
    
    def product_buying(self, product:StoreItem, user:User) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        if (product.warehouse_quantity > 0):
            builder.button(text="💰 Беру!",
                callback_data=StoreCF(action="buy", 
                                      id=product.id,
                                      user_id=user.tg_id))
        
        builder.button(text=dict.back,
            callback_data=StoreCF(action="cancel",
                                  user_id=user.tg_id))
        
        builder.adjust(2)
        
        return builder.as_markup()
