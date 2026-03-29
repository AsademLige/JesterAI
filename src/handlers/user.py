from src.domain.controllers.items_controller import ItemsController
from src.models.user_inventory_item_model import UserInventoryItem
from src.keyboards.interactive_keyboard import InteractiveKeyboard
from src.keyboards.callback_fabrics import InventoryCF
from src.models.user_stats_model import UserStats
from src.handlers.commands import Commands as cn
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from src.services.data_base.db import DataBase
from aiogram.fsm.context import FSMContext
from src.data.dictionary import Dictionary
from src.domain.utils.utils import Utils
from src.models.item_model import Item
from src.models.user_model import User
from aiogram.enums import ParseMode
from src.data.config import Prefs
from aiogram.types import Message
from typing import List, Tuple
from datetime import timedelta
import math

from aiogram import Router, F
from aiogram import Bot

prefs = Prefs()
dict = Dictionary()
bot = Bot(token=prefs.bot_token)
interactive_kb = InteractiveKeyboard()
db = DataBase()
rt = Router()

###Получение информации о пользователе
@rt.message(StateFilter(None), Command(cn.me))
async def user_information(message: Message, state: FSMContext):
    user: User = await db.get_user_by_chat_id(message.from_user.id, message.chat.id)
    place_in_top:int = await db.get_place_in_top_by_member(user.tg_id, user.chat_id)
    user_stats:UserStats = await db.get_user_stats(user)

    await state.update_data(user=user)
    
    # Получаем оставшееся время до возможности использовать pencil
    delta_pencil:timedelta = Utils.get_time_delta(user.last_length_check)
    # Если оставшееся время отрицательное, значит можно использовать команду
    if math.floor(delta_pencil.total_seconds() / 3600) < 0:
        time_to_pencil = Utils.timedelta_to_hhmm(delta_pencil)
    else:
        time_to_pencil = "Готов"
    
    # Получаем оставшееся время до возможности использовать dice_game
    delta_dice:timedelta = Utils.get_time_delta(user.last_dice_play, 1)
    # Если оставшееся время отрицательное, значит можно использовать команду
    if math.floor(delta_dice.total_seconds() / 3600) < 0:
        time_to_dice = Utils.timedelta_to_hhmm(delta_dice)
    else:
        time_to_dice = "Готов"
    
    await message.delete()
    answer = await bot.send_message(user.chat_id, dict.user_information(user, place_in_top, 
                                                                        user_stats,
                                                                        time_to_pencil, 
                                                                        time_to_dice),
                         reply_markup=interactive_kb.user_information_buttons(user),
                         parse_mode=ParseMode.HTML)
    await Utils.delete_old_message([answer], 60)

###Открытие инвентаря
@rt.callback_query(InventoryCF.filter(F.action == "inventory"))
async def on_inventory_open(callback: CallbackQuery, callback_data: InventoryCF, state: FSMContext):
    state_data = await state.get_data()
    if (not 'user' in state_data): return
    user: User = state_data["user"]

    if (user.tg_id != callback_data.user_id):
        return
    
    inventory:List[Tuple[UserInventoryItem, Item]] = await db.get_user_inventory(user)
    await state.update_data(inventory=inventory)
    await callback.message.edit_text(dict.user_inventory(user, inventory),
                                        reply_markup=interactive_kb.inventory_items(inventory, user),
                                         parse_mode=ParseMode.HTML)
    
###Выбор предмета в инвентаре
@rt.callback_query(InventoryCF.filter(F.action == "inventory_choice"))
async def on_inventory_item_select(callback: CallbackQuery, callback_data: InventoryCF, state: FSMContext):
    state_data = await state.get_data()
    if (not 'user' in state_data): return
    user: User = state_data["user"]

    if (user.tg_id != callback_data.user_id):
        return

    inventory: List[Tuple[UserInventoryItem, Item]] = state_data["inventory"]
    item:Tuple[UserInventoryItem, Item] = next((p for p in inventory if p[1].id == callback_data.item_id), None)
    await state.update_data(item=item)
    await callback.message.edit_text(dict.inventory_item_info(item),
                                        reply_markup=interactive_kb.item_keyboard(user, item[1]),
                                        parse_mode=ParseMode.HTML)  
    
###Применение предмета на себя
@rt.callback_query(InventoryCF.filter(F.action == "use_myself"))
async def on_item_use_myself(callback: CallbackQuery, callback_data: InventoryCF, state: FSMContext):
    state_data = await state.get_data()
    if (not 'user' in state_data): return
    user: User = state_data["user"]

    if (user.tg_id != callback_data.user_id):
        return

    item:Tuple[UserInventoryItem, Item] = state_data["item"]

    use_status:str = await ItemsController.use_item(user, item)
    if (use_status):
        await callback.message.delete()
        await bot.send_message(user.chat_id, use_status, parse_mode=ParseMode.HTML)
    await Utils.delete_old_message([callback.message],5)

###Выбор цели для использования предмета
@rt.callback_query(InventoryCF.filter(F.action == "select_target"))
async def on_item_target_select(callback: CallbackQuery, callback_data: InventoryCF, state: FSMContext):
    state_data = await state.get_data()
    if (not 'user' in state_data): return
    user: User = state_data["user"]

    if (user.tg_id != callback_data.user_id):
        return
    
    users: List[User] = await db.get_all_users_by_chat(user.chat_id)
    await callback.message.edit_text(dict.select_target,
                                        reply_markup=interactive_kb.select_target(users, user),
                                        parse_mode=ParseMode.HTML)

###Цель выбрана, применяем на нее предмет
@rt.callback_query(InventoryCF.filter(F.action == "inventory_target_selected"))
async def on_item_target_selected(callback: CallbackQuery, callback_data: InventoryCF, state: FSMContext):
    state_data = await state.get_data()
    if (not 'user' in state_data): return
    user: User = state_data["user"]

    if (user.tg_id != callback_data.user_id):
        return
    
    target: User = await db.get_user_by_id(callback_data.item_id)
    item:Tuple[UserInventoryItem, Item] = state_data["item"]
    use_status:str = await ItemsController.use_item(user, item, target)
    if (use_status):
        await callback.message.delete()
        await bot.send_message(user.chat_id, use_status, parse_mode=ParseMode.HTML)
    await Utils.delete_old_message([callback.message],5)

###Отмена выбора цели
@rt.callback_query(InventoryCF.filter(F.action == "target_select_cancel"))
async def on_target_select_cancel(callback: CallbackQuery, callback_data: InventoryCF, state: FSMContext):
    state_data = await state.get_data()
    if (not 'user' in state_data): return
    user: User = state_data["user"]

    if (user.tg_id != callback_data.user_id):
        return
    
    inventory: List[Tuple[UserInventoryItem, Item]] = state_data["inventory"]
    user: User = state_data["user"]
    await callback.message.edit_text(dict.user_inventory(user, inventory),
                                        reply_markup=interactive_kb.inventory_items(inventory, user),
                                        parse_mode=ParseMode.HTML)
    
###Закрытие /me
@rt.callback_query(InventoryCF.filter(F.action == "me_close"))
async def on_me_exit(callback: CallbackQuery, callback_data: InventoryCF, state: FSMContext):
    state_data = await state.get_data()
    if (not 'user' in state_data): return
    user: User = state_data["user"]

    if (user.tg_id != callback_data.user_id):
        return
    
    await callback.message.delete()

            