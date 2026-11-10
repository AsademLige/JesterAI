from features.user.data.repository.gino_user_repository import GinoUserRepository
from apps.tg_bot.keyboards.callback_fabrics import DiceGameCF, InventoryCF
from features.items.data.models.inventory_item_dto import InventoryItem
from aiogram.utils.keyboard import InlineKeyboardBuilder
from features.items.items_manager import ItemsManager, get_item_sell_price
from features.user.data.dtos.user_dto import User
from aiogram.types import InlineKeyboardMarkup
from aiogram.types import InlineKeyboardButton
from core.consts.dictionary import Dictionary, INVENTORY_ROW_SIZE, inventory_page_bounds, group_inventory_items
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
    
    def inventory_items(self, user:User, page:int = 1) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        entries = list(enumerate(group_inventory_items(user.inventory)))
        pages = inventory_page_bounds(len(entries))
        total_pages = len(pages)
        page = max(1, min(page, total_pages))
        start, count = pages[page - 1]
        page_entries = entries[start:start + count]

        for i, item in page_entries:
            meta = item.meta or {}
            weight = meta.get("weight_kg")
            weight_str = f" {float(weight):.1f}кг" if weight else ""
            count_str = f"×{item.quantity}" if meta.get("instance_ids") and item.quantity > 1 else ""
            builder.button(text=f"{i+1} {item.utf8_icon}{weight_str}{count_str}",
                callback_data=InventoryCF(action="inventory_choice", 
                                            item_id=item.id,
                                            instance_id=item.instance_id,
                                            user_id=user.tg_id))

        if total_pages > 1:
            builder.button(text="◀️",
                callback_data=InventoryCF(action="inventory",
                                          page=max(1, page - 1),
                                          user_id=user.tg_id))
            builder.button(text=f"{page}/{total_pages}",
                callback_data=InventoryCF(action="", user_id=user.tg_id))
            builder.button(text="▶️",
                callback_data=InventoryCF(action="inventory",
                                          page=min(total_pages, page + 1),
                                          user_id=user.tg_id))

        builder.button(text=dict.exit,
            callback_data=InventoryCF(action="me_close",
                                      user_id=user.tg_id))
        
        sizes = [INVENTORY_ROW_SIZE] * (len(page_entries) // INVENTORY_ROW_SIZE)
        leftover = len(page_entries) % INVENTORY_ROW_SIZE
        if leftover:
            sizes.append(leftover)
        if total_pages > 1:
            sizes.append(INVENTORY_ROW_SIZE)
        sizes.append(1)
        builder.adjust(*sizes)
        return builder.as_markup()
    
    def item_keyboard(self, user:User, item:InventoryItem, quantity:int) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        grouped = bool((item.meta or {}).get("instance_ids"))
        if grouped:
            quantity = item.quantity
        else:
            minus:int = quantity - 1 if (quantity - 1 >= 1) else quantity
            plus:int = quantity + 1 if (quantity + 1 <= item.quantity) else quantity

            builder.button(text="➖ меньше",
                        callback_data=InventoryCF(action="inventory_choice",
                                                quantity=minus,
                                                item_id=item.id,
                                                instance_id=item.instance_id,
                                                user_id=user.tg_id))

        builder.button(text=f"{quantity}",
                            callback_data=InventoryCF(action = "", user_id=user.tg_id))

        if not grouped:
            builder.button(text="➕ больше",
                                callback_data=InventoryCF(action="inventory_choice",
                                                        quantity=plus,
                                                        item_id=item.id,
                                                        instance_id=item.instance_id,
                                                        user_id=user.tg_id))

        if (item.usable):
            builder.button(text=dict.use_myself,
            callback_data=InventoryCF(action="use_myself",
                                    quantity=quantity,
                                    user_id=user.tg_id))
        
        if (item.usable):
            builder.button(text=dict.select_target,
            callback_data=InventoryCF(action="select_target",
                                    quantity=quantity,
                                    user_id=user.tg_id))

        builder.button(text=f"{dict.sell_item} (+{get_item_sell_price(item, quantity)}💰)",
        callback_data=InventoryCF(action="sell_item",
                                quantity=quantity,
                                user_id=user.tg_id))

        builder.button(text=dict.back,
        callback_data=InventoryCF(action="inventory",
                                  user_id=user.tg_id))
        
        builder.adjust(3, 2, 2)
        return builder.as_markup()
    
    def select_target(self, users:List[User], except_user:User, quantity:int = 1) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        
        for user in users:
            if (not except_user.id == user.id):
                builder.button(text=f"{user.tg_name}-{user.length}см",
                    callback_data=InventoryCF(action="inventory_target_selected",
                                              item_id=user.id,
                                              quantity=quantity,
                                              user_id=except_user.tg_id))
            
        builder.button(text=dict.back,
        callback_data=InventoryCF(action="target_select_cancel",
                                  quantity=quantity,
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