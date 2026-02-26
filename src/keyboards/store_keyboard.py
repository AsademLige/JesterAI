from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup
from src.models.store_item_model import StoreItem
from src.keyboards.callback_fabrics import StoreCF
from src.models.warehouse import Warehouse
from src.data.dictionary import Dictionary
from src.data.config import Prefs
from typing import List, Tuple

prefs = Prefs()
dict = Dictionary()

class StoreKeyboard():
    def __init__(self):
        pass

    def store_products(self, products: List[Tuple[Warehouse, StoreItem]]) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        for i, product in enumerate(products):
            builder.button(text=f"{i+1}",
                callback_data=StoreCF(action="choice", id=product[1].id))
            
        builder.button(text=dict.exit,
            callback_data=StoreCF(action="exit"))
        
        builder.adjust(2)
        
        return builder.as_markup()
    
    def product_buying(self, product:Tuple[Warehouse, StoreItem]) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        if (product[0].quantity > 0):
            builder.button(text="💰 Беру!",
                callback_data=StoreCF(action="buy", id=product[1].id))
        
        builder.button(text=dict.back,
            callback_data=StoreCF(action="cancel"))
        
        builder.adjust(2)
        
        return builder.as_markup()
