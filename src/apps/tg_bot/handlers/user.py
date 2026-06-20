from apps.tg_bot.keyboards.interactive_keyboard import InteractiveKeyboard
from features.user.data.dtos.inventory_item_dto import InventoryItem
from apps.tg_bot.keyboards.callback_fabrics import InventoryCF
from features.user.data.repository.gino_user_repository import GinoUserRepository
from features.items.items_controller import ItemsController
from features.user.domain.user_manager import UserManager
from features.user.data.dtos.user_dto import User
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from apps.tg_bot.commands import Commands as cn
from core.consts.dictionary import Dictionary
from aiogram.fsm.context import FSMContext
from core.data.data_base import DataBase
from core.consts.config import Prefs
from aiogram.enums import ParseMode
from core.utils.utils import Utils
from aiogram.types import Message
from aiogram import Router, F
from typing import List
from aiogram import Bot

prefs = Prefs()
dict = Dictionary()
bot = Bot(token=prefs.bot_token)
interactive_kb = InteractiveKeyboard()
repository:GinoUserRepository = GinoUserRepository()
user_mr:UserManager = UserManager(repo=repository)
db = DataBase()
rt = Router()

member_change_reset_time:int = 24
    
###Попробовать изменить текущий member размер 
@rt.message(StateFilter(None), Command(cn.pencil))
async def pencil_change(message: Message, state: FSMContext):
    user: User = await repository.get_user(message.from_user.id, message.chat.id)

    await message.delete()
    result = await user_mr.pencil_change(user)
    msg = result["error"] if (result["error"]) else result["msg"]

    await bot.send_message(user.chat_id, msg, parse_mode=ParseMode.HTML)
        

###Получение информации о пользователе
@rt.message(StateFilter(None), Command(cn.me))
async def user_information(message: Message, state: FSMContext):
    await message.delete()
    user: User = await repository.get_user(message.from_user.id, message.chat.id)
    await state.update_data(user=user)

    result = await user_mr.get_menu(user)

    answer = await bot.send_message(user.chat_id, result["msg"],
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

    await callback.message.edit_text(dict.user_inventory(user),
                                        reply_markup=interactive_kb.inventory_items(user),
                                         parse_mode=ParseMode.HTML)
    
###Выбор предмета в инвентаре
@rt.callback_query(InventoryCF.filter(F.action == "inventory_choice"))
async def on_inventory_item_select(callback: CallbackQuery, callback_data: InventoryCF, state: FSMContext):
    state_data = await state.get_data()
    if (not 'user' in state_data): return
    user: User = state_data["user"]

    if (user.tg_id != callback_data.user_id):
        return

    item:InventoryItem = next((p for p in user.inventory if p.product_id == callback_data.item_id), None)

    await state.update_data(item=item)
    await callback.message.edit_text(dict.inventory_item_info(item),
                                        reply_markup=interactive_kb.item_keyboard(user, item),
                                        parse_mode=ParseMode.HTML)  
    
###Применение предмета на себя
@rt.callback_query(InventoryCF.filter(F.action == "use_myself"))
async def on_item_use_myself(callback: CallbackQuery, callback_data: InventoryCF, state: FSMContext):
    state_data = await state.get_data()
    if (not 'user' in state_data): return
    user: User = state_data["user"]

    if (user.tg_id != callback_data.user_id):
        return

    item:InventoryItem = state_data["item"]
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
    
    users: List[User] = await repository.get_users(user.chat_id)
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
    
    target: User = await repository.get_user(id=callback_data.item_id)
    item:InventoryItem = state_data["item"]
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
    
    user: User = state_data["user"]
    await callback.message.edit_text(dict.user_inventory(user),
                                        reply_markup=interactive_kb.inventory_items(user),
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

            