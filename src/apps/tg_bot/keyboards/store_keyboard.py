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
    
    def product_buying(self, product:StoreItem, user:User, quantity:int = 1) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        minus:int = quantity - 1 if (quantity - 1 >= 1) else quantity
        plus:int = quantity + 1 if (quantity + 1 <= product.warehouse_quantity) else quantity

        full_price = product.price * quantity        
        if (product.is_discount_active):
            full_price:int = round(full_price - (full_price * (product.discount_percent / 100)))

        builder.button(text="➖ меньше",
                    callback_data=StoreCF(action="choice",
                                            quantity=minus,
                                            id=product.id,
                                            user_id=user.tg_id))

        builder.button(text=f"{quantity}",
                            callback_data=StoreCF(action = "", user_id=user.tg_id))

        builder.button(text="➕ больше",
                            callback_data=StoreCF(action="choice",
                                                    quantity=plus,
                                                    id=product.id,
                                                    user_id=user.tg_id))

        if (product.warehouse_quantity > 0):
            builder.button(text=f"💰 Беру! (-{full_price})",
                callback_data=StoreCF(action="buy", 
                                      quantity=quantity,
                                      id=product.id,
                                      user_id=user.tg_id))
        
        builder.button(text=dict.back,
            callback_data=StoreCF(action="cancel",
                                  user_id=user.tg_id))
        
        builder.adjust(3)
        
        return builder.as_markup()

    def buy_more(self) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.button(text="🛒 Купить еще", 
                        callback_data="hub_store")

        builder.adjust(1)
        return builder.as_markup()
        
