from typing import List, Tuple

from src.models.user_model import User
from src.models.store_item_model import StoreItem
from src.models.user_inventory_item_model import UserInventoryItem
from src.keyboards.callback_fabrics import DiceGameCF, InventoryCF
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup
from aiogram.types import InlineKeyboardButton
from src.data.dictionary import Dictionary
from src.data.config import Prefs

prefs = Prefs()
dict = Dictionary()

class InteractiveKeyboard():
    def __init__(self):
        pass

    def user_information_buttons(self, user:User) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(text="🎒 Инвентарь",
                callback_data=InventoryCF(action="inventory", 
                                          user_id=user.tg_id).pack()))
        builder.add(InlineKeyboardButton(text=dict.exit,
                callback_data=InventoryCF(action="me_close", 
                                          user_id=user.tg_id).pack()))
        builder.adjust(2) 
        return builder.as_markup()
    
    def inventory_items(self, items: List[Tuple[UserInventoryItem, StoreItem]], user:User) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        for i, item in enumerate(items):
            if (item[0].quantity > 0):
                builder.button(text=f"{i+1}",
                    callback_data=InventoryCF(action="inventory_choice", 
                                                item_id=item[1].id,
                                                user_id=user.tg_id))
            
        builder.button(text=dict.exit,
            callback_data=InventoryCF(action="me_close",
                                      user_id=user.tg_id))
        
        builder.adjust(2)
        return builder.as_markup()
    
    def item_keyboard(self, user:User) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.button(text=dict.use_myself,
        callback_data=InventoryCF(action="use_myself",
                                  user_id=user.tg_id))

        builder.button(text=dict.select_target,
        callback_data=InventoryCF(action="select_target",
                                  user_id=user.tg_id))

        builder.button(text=dict.back,
        callback_data=InventoryCF(action="inventory",
                                  user_id=user.tg_id))
        
        builder.adjust(2)
        return builder.as_markup()
    
    def select_target(self, users:List[User], except_user:User) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        
        for user in users:
            if (not except_user.id == user.id):
                builder.button(text=f"{user.tg_name}-{user.length}см",
                    callback_data=InventoryCF(action="inventory_target_selected",
                                              item_id=user.id,
                                              user_id=except_user.tg_id))
            
        builder.button(text=dict.back,
        callback_data=InventoryCF(action="target_select_cancel",
                                  user_id=except_user.tg_id))

        builder.adjust(2)
        return builder.as_markup()
    
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