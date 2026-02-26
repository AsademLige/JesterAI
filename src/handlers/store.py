from src.keyboards.interactive_keyboard import InteractiveKeyboard
from aiogram.types import FSInputFile, Message, CallbackQuery
from src.keyboards.store_keyboard import StoreKeyboard
from src.models.store_item_model import StoreItem
from src.keyboards.callback_fabrics import StoreCF
from src.handlers.commands import Commands as cn
from src.domain.states.store_set import StoreSet
from aiogram.filters import Command, StateFilter
from src.services.data_base.db import DataBase
from src.models.warehouse import Warehouse
from aiogram.fsm.context import FSMContext
from src.domain.utils.consts import Consts
from src.data.dictionary import Dictionary
from src.domain.utils.utils import Utils
from src.models.user_model import User
from aiogram.enums import ParseMode
from src.data.config import Prefs
from aiogram.types import Message
from typing import List, Tuple
import os

from aiogram import Router, F
from aiogram import Bot

prefs = Prefs()
dict = Dictionary()
bot = Bot(token=prefs.bot_token)
interactive_kb = InteractiveKeyboard()
products:List[Tuple[Warehouse, StoreItem]] = []
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
    await state.set_state(StoreSet.choice_product)

    products = await db.get_store_goods_with_quantity()

    answer = await bot.send_photo(user.chat_id, photo, caption=dict.store_description(products, user.tg_name, user.tg_id),
                                  reply_markup = store_kb.store_products(products),
                                  parse_mode=ParseMode.HTML)
    
@rt.callback_query(StoreSet.choice_product, StoreCF.filter())
async def choice_product(callback: CallbackQuery, callback_data: StoreCF, state: FSMContext):
    global products
    product:Tuple[Warehouse, StoreItem] = next((p for p in products if p[1].id == callback_data.id), None)
    state_data = await state.get_data()
    user: User = state_data["user"]
    answer:Message

    if (callback_data.action == "choice"):
        await callback.message.edit_caption(caption=dict.product_description(product),
            reply_markup = store_kb.product_buying(product),
            parse_mode=ParseMode.HTML
        )
    elif (callback_data.action == "buy"):
        await callback.message.delete()

        if (user.money < product[1].price):
            answer = await bot.send_message(user.chat_id, dict.not_enough_money(user),
                                            parse_mode=ParseMode.HTML)
            await state.clear()
            products.clear()
            await Utils.delete_old_message([answer], 5)
            return

        if (await db.update_item_quantity(product) and 
            await db.add_to_user_inventory(user, product) and
            await db.update_user(user, {
                User.money.name: User.money - product[1].price,
            })):
            answer = await bot.send_message(user.chat_id, dict.product_buying_thanks(user),
                                            parse_mode=ParseMode.HTML)
        else:
            answer = await bot.send_message(user.chat_id, 
                                            "Мы где-то наебались, мы где-то обсчитались...")
        await state.clear()
        products.clear()
    elif (callback_data.action == "cancel"):
        await callback.message.edit_caption(caption=dict.store_description(products, user.tg_name, user.tg_id),
            reply_markup = store_kb.store_products(products),
            parse_mode=ParseMode.HTML
        )
    elif (callback_data.action == "exit"):
        await callback.message.delete()
        answer = await bot.send_message(user.chat_id, dict.store_exit(user),parse_mode=ParseMode.HTML)
        await state.clear()
        products.clear()

    await Utils.delete_old_message([answer], 5)

