from src.keyboards.edit_sticker_set_keyboard import EditStickerSetKeyboard
from src.domain.states.edit_sticker_set import EditStickerSet
from src.models.sticker_set_model import StickerSetModel
from src.keyboards.callback_fabrics import StickerSetCF
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from src.handlers.commands import Commands as cn
from src.services.data_base.db import DataBase
from aiogram.types import StickerSet, Message
from aiogram.fsm.context import FSMContext
from src.data.dictionary import Dictionary
from src.data.config import Prefs
from aiogram import Router, F
from aiogram import Bot
from typing import List

prefs = Prefs()
bot = Bot(token=prefs.bot_token)
db = DataBase()
rt = Router()
kb = EditStickerSetKeyboard()

### Список доступных наборов стикеров
@rt.message(StateFilter(None), Command(cn.edit_sticker_set))
async def sticker_set_choice_handler(message: Message, state: FSMContext):
    await state.set_state(EditStickerSet.edit_sticker_set)
    sticker_set_list:List[StickerSetModel] = await db.get_all_sticker_sets()
    if (sticker_set_list):
        last_bot_message:Message = await message.answer(Dictionary.choice_sticker_set, 
                         reply_markup = kb.sticker_set_list_button(sticker_set_list))
    
        await state.update_data(last_bot_message = last_bot_message)
    else:
        await message.answer(Dictionary.sticker_set_list_is_empty)
        await state.clear()

### Выбор действия
@rt.callback_query(EditStickerSet.edit_sticker_set, StickerSetCF.filter())
async def edit_sticker_set_handler(callback: CallbackQuery, callback_data: StickerSetCF, state: FSMContext):
    state_data = await state.get_data()
    last_bot_message:Message = state_data["last_bot_message"]

    if (callback_data.action == "choice"):
       last_bot_message:Message = await callback.message.edit_text(Dictionary.sticker_edit_variants, 
                                                       reply_markup = kb.edit_sticker_set_command_button(callback_data.short_name))
    elif (callback_data.action == "delete"):
        if (await db.delete_sticker_set_by_name(callback_data.short_name)):
            await callback.message.edit_text(Dictionary.delete_sticker_set_success)
        else:
            await callback.message.edit_text(Dictionary.error)
        await state.clear()
    elif (callback_data.action == "exit"):
        await last_bot_message.delete()
        await state.clear()

    await state.update_data(last_bot_message = last_bot_message)

    
    