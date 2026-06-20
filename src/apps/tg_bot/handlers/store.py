from features.user.data.repository.gino_user_repository import GinoUserRepository
from apps.tg_bot.keyboards.interactive_keyboard import InteractiveKeyboard
from apps.tg_bot.keyboards.store_keyboard import StoreKeyboard
from aiogram.types import FSInputFile, Message, CallbackQuery
from features.store.domain.store_manager import StoreManager
from apps.tg_bot.keyboards.callback_fabrics import StoreCF
from features.user.data.dtos.user_dto import User
from core.consts.dictionary import Dictionary
from aiogram.fsm.context import FSMContext
from core.data.data_base import DataBase
from aiogram.filters import StateFilter
from core.consts.config import Prefs
from aiogram.enums import ParseMode
from core.utils.utils import Utils
from aiogram.types import Message
from aiogram import Router, F
from typing import Optional
from aiogram import Bot

prefs = Prefs()
dict = Dictionary()
bot = Bot(token=prefs.bot_token)
interactive_kb = InteractiveKeyboard()
user_repo:GinoUserRepository = GinoUserRepository()
store_kb = StoreKeyboard()
db = DataBase()
rt = Router()

store_mr = StoreManager(db, dict)

@rt.callback_query(StateFilter(None), F.data == "hub_store")
async def store(callback_query: CallbackQuery, state: FSMContext):
    message = callback_query.message 
    
    user: User = await user_repo.get_user(callback_query.from_user.id, message.chat.id)
    result = await store_mr.openStore(user)

    if (result["error"]):
        answer = await message.answer(result["error"])
        await Utils.delete_old_message([message, answer], 3)
        await callback_query.answer()
        return

    await callback_query.answer()
    await message.delete()

    photo = FSInputFile(result["photo_path"])
    answer = await bot.send_photo(user.chat_id, photo, caption=dict.store_description(store_mr.products, user),
                                  reply_markup = store_kb.store_products(store_mr.products, user),
                                  parse_mode=ParseMode.HTML)
    
    if (await Utils.delete_old_message([answer], 60)):
        answer = await bot.send_message(user.chat_id, dict.store_exit(user),
                                        parse_mode=ParseMode.HTML)
        await Utils.delete_old_message([answer], 5)
        store_mr.closeStore()
    
@rt.callback_query(StoreCF.filter(F.action == "choice"))
async def choice_product(callback: CallbackQuery, callback_data: StoreCF, state: FSMContext):
    answer:Message = None

    if (store_mr.customer.tg_id != callback.from_user.id):
        return
    
    store_mr.select_product(callback_data.id)

    await callback.message.edit_caption(caption=dict.product_description(store_mr.selected_product),
        reply_markup = store_kb.product_buying(store_mr.selected_product, store_mr.customer),
        parse_mode=ParseMode.HTML
    )
        
    if (answer):
        await Utils.delete_old_message([answer], 5)


@rt.callback_query(StoreCF.filter(F.action == "buy"))
async def buy_product(callback: CallbackQuery, callback_data: StoreCF, state: FSMContext):
    answer:Message = None

    if (store_mr.customer.tg_id != callback.from_user.id):
        return

    await callback.message.delete()

    result = await store_mr.buy_product()

    answer = await bot.send_message(store_mr.customer.chat_id, result["msg"],
                                        parse_mode=ParseMode.HTML)
    store_mr.closeStore()

    if (answer):
        await Utils.delete_old_message([answer], 5)

@rt.callback_query(StoreCF.filter(F.action == "cancel"))
async def cancel_choice_product(callback: CallbackQuery, callback_data: StoreCF, state: FSMContext):
    if (store_mr.customer.tg_id != callback.from_user.id):
        return

    await callback.message.edit_caption(caption=dict.store_description(store_mr.products, store_mr.customer),
        reply_markup = store_kb.store_products(store_mr.products, store_mr.customer),
        parse_mode=ParseMode.HTML
    )

@rt.callback_query(StoreCF.filter(F.action == "exit"))
async def exit_store(callback: CallbackQuery, callback_data: StoreCF, state: FSMContext):
    user:Optional[User] = await user_repo.get_user(store_mr.customer.tg_id, 
                                           callback.message.chat.id)
    answer:Message = None

    await callback.message.delete()
    answer = await bot.send_message(user.chat_id, dict.store_exit(user),
                                    parse_mode=ParseMode.HTML)
    store_mr.closeStore()

    if (answer):
        await Utils.delete_old_message([answer], 5)