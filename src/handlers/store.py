from src.keyboards.interactive_keyboard import InteractiveKeyboard
from aiogram.types import FSInputFile, Message, CallbackQuery
from src.models.discounts_model import ProductDiscounts
from src.keyboards.store_keyboard import StoreKeyboard
from src.keyboards.callback_fabrics import StoreCF
from src.handlers.commands import Commands as cn
from aiogram.filters import Command, StateFilter
from src.services.data_base.db import DataBase
from src.models.warehouse import Warehouse
from aiogram.fsm.context import FSMContext
from src.domain.utils.consts import Consts
from src.data.dictionary import Dictionary
from typing import List, Optional, Tuple
from src.domain.utils.utils import Utils
from src.models.item_model import Item
from src.models.user_model import User
from aiogram.enums import ParseMode
from src.data.config import Prefs
from aiogram.types import Message
import os

from aiogram import Router, F
from aiogram import Bot

prefs = Prefs()
dict = Dictionary()
bot = Bot(token=prefs.bot_token)
interactive_kb = InteractiveKeyboard()
products:List[Tuple[Warehouse, Item, ProductDiscounts]] = []
store_kb = StoreKeyboard()
db = DataBase()
rt = Router()

@rt.message(StateFilter(None), Command(cn.store))
async def store(message: Message, state: FSMContext):
    global products

    if (products):
        answer = await message.answer("⛔️ Встань в очередь!")
        await Utils.delete_old_message([message, answer], 3)
        return

    user:User = await db.get_user_by_chat_id(message.from_user.id, message.chat.id)
    await state.update_data(user = user)
    photo = FSInputFile(os.path.join(Consts.IMAGES_DIR, f"vendor.webp"))

    await message.delete()

    products = await db.get_store_items_with_quantity()

    answer = await bot.send_photo(user.chat_id, photo, caption=dict.store_description(products, user),
                                  reply_markup = store_kb.store_products(products, user),
                                  parse_mode=ParseMode.HTML)
    
    if (await Utils.delete_old_message([answer], 60)):
        answer = await bot.send_message(user.chat_id, dict.store_exit(user),
                                        parse_mode=ParseMode.HTML)
        await Utils.delete_old_message([answer], 5)
        products.clear()
    
@rt.callback_query(StoreCF.filter(F.action == "choice"))
async def choice_product(callback: CallbackQuery, callback_data: StoreCF, state: FSMContext):
    global products
    state_data = await state.get_data()
    answer:Message = None

    if (not 'user' in state_data): return
    user: User = state_data["user"]

    if (user.tg_id != callback_data.user_id):
        return
    
    product:Tuple[Warehouse, Item, ProductDiscounts] = next((p for p in products if p[1].id == callback_data.id), None)
    await state.update_data(product = product)
    await callback.message.edit_caption(caption=dict.product_description(product),
        reply_markup = store_kb.product_buying(product, user),
        parse_mode=ParseMode.HTML
    )
        
    if (answer):
        await Utils.delete_old_message([answer], 5)


@rt.callback_query(StoreCF.filter(F.action == "buy"))
async def buy_product(callback: CallbackQuery, callback_data: StoreCF, state: FSMContext):
    global products
    state_data = await state.get_data()
    answer:Message = None

    if (not 'user' in state_data): return
    user: User = state_data["user"]

    if (user.tg_id != callback_data.user_id):
        return

    product: Tuple[Warehouse, Item, ProductDiscounts] = state_data["product"]
    await callback.message.delete()

    final_price:int = product[1].price
    if (product[2]):
        final_price = round(final_price - (final_price * (product[2].discount_percent / 100)))

    if (user.money < final_price):
        answer = await bot.send_message(user.chat_id, dict.not_enough_money(user),
                                        parse_mode=ParseMode.HTML)
        products.clear()
        await Utils.delete_old_message([answer], 5)
        return

    if (await db.update_item_quantity_at_warehouse(product) and 
        await db.user_item_transaction(user, product[1]) and
        await db.update_user(user, {
            User.money.name: User.money - final_price,
        })):
        answer = await bot.send_message(user.chat_id, dict.product_buying_thanks(user),
                                        parse_mode=ParseMode.HTML)
    else:
        answer = await bot.send_message(user.chat_id, 
                                        "Мы где-то наебались, мы где-то обсчитались...")
    products.clear()

    if (answer):
        await Utils.delete_old_message([answer], 5)

@rt.callback_query(StoreCF.filter(F.action == "cancel"))
async def cancel_choice_product(callback: CallbackQuery, callback_data: StoreCF, state: FSMContext):
    global products
    state_data = await state.get_data()
    if (not 'user' in state_data): return
    user: User = state_data["user"]

    if (user.tg_id != callback_data.user_id):
        return

    await callback.message.edit_caption(caption=dict.store_description(products, user),
        reply_markup = store_kb.store_products(products, user),
        parse_mode=ParseMode.HTML
    )

@rt.callback_query(StoreCF.filter(F.action == "exit"))
async def exit_store(callback: CallbackQuery, callback_data: StoreCF, state: FSMContext):
    global products
    state_data = await state.get_data()
    if (not 'user' in state_data):
        user:Optional[User] = await db.get_user_by_chat_id(callback_data.user_id, 
                                           callback.message.chat.id)
        if (not user): return
    else:
        user: User = state_data["user"]

    answer:Message = None

    await callback.message.delete()
    answer = await bot.send_message(user.chat_id, dict.store_exit(user),
                                    parse_mode=ParseMode.HTML)
    products.clear()

    if (answer):
        await Utils.delete_old_message([answer], 5)