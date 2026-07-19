from features.user.data.repository.gino_user_repository import GinoUserRepository
from apps.tg_bot.keyboards.callback_fabrics import DiceGameCF, InventoryCF
from features.items.data.models.inventory_item_dto import InventoryItem
from aiogram.utils.keyboard import InlineKeyboardBuilder
from features.items.items_manager import ItemsManager
from features.user.data.dtos.user_dto import User
from aiogram.types import InlineKeyboardMarkup
from aiogram.types import InlineKeyboardButton
from core.consts.dictionary import Dictionary
from core.consts.config import Prefs
from typing import List


prefs = Prefs()
dict = Dictionary()

class InteractiveKeyboard():
    def __init__(self):
        self.user_repo = GinoUserRepository()
        self.items_mg:ItemsManager = ItemsManager(self.user_repo)
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
    
    def inventory_items(self, user:User) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        for i, item in enumerate(user.inventory):
            if (item.quantity > 0):
                builder.button(text=f"{i+1} {item.utf8_icon}",
                    callback_data=InventoryCF(action="inventory_choice", 
                                                item_id=item.id,
                                                user_id=user.tg_id))
            
        builder.button(text=dict.exit,
            callback_data=InventoryCF(action="me_close",
                                      user_id=user.tg_id))
        
        builder.adjust(2)
        return builder.as_markup()
    
    def item_keyboard(self, user:User, item:InventoryItem) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        if (not self.items_mg.is_steal_item(item) and 
            not self.items_mg.is_heal_item(item)):
            builder.button(text=dict.use_myself,
            callback_data=InventoryCF(action="use_myself",
                                    user_id=user.tg_id))
        
        if (not self.items_mg.is_heal_item(item)):
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