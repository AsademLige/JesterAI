from aiogram.utils.keyboard import InlineKeyboardBuilder
from features.store.data.models.discounts_model import ProductDiscounts
from apps.tg_bot.keyboards.callback_fabrics import StoreCF
from aiogram.types import InlineKeyboardMarkup
from features.store.data.models.warehouse import Warehouse
from core.consts.dictionary import Dictionary
from features.items.data.models.item_model import Item
from core.data.models.user_model import User
from core.consts.config import Prefs
from typing import List, Tuple

prefs = Prefs()
dict = Dictionary()

class StoreKeyboard():
    def __init__(self):
        pass

    def store_products(self, products: List[Tuple[Warehouse, Item, ProductDiscounts]], user:User) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        for i, product in enumerate(products):
            builder.button(text=f"({i+1}) {product[1].utf8_icon} " + ("%" if product[2] else "$"),
                callback_data=StoreCF(action="choice", 
                                      id=product[1].id,
                                      user_id=user.tg_id))
            
        builder.button(text=dict.exit,
            callback_data=StoreCF(action="exit",
                                  user_id=user.tg_id))
        
        builder.adjust(2)
        
        return builder.as_markup()
    
    def product_buying(self, product:Tuple[Warehouse, Item, ProductDiscounts], user:User) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        if (product[0].quantity > 0):
            builder.button(text="💰 Беру!",
                callback_data=StoreCF(action="buy", 
                                      id=product[1].id,
                                      user_id=user.tg_id))
        
        builder.button(text=dict.back,
            callback_data=StoreCF(action="cancel",
                                  user_id=user.tg_id))
        
        builder.adjust(2)
        
        return builder.as_markup()
