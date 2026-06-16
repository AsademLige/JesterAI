from apps.tg_bot.keyboards.interactive_keyboard import InteractiveKeyboard
from core.data.data_base import DataBase
from aiogram.fsm.context import FSMContext
from core.consts.dictionary import Dictionary
from core.utils.utils import Utils
from datetime import datetime, timedelta
from aiogram.types import CallbackQuery
from core.consts.config import Prefs

from aiogram import Router, F
from aiogram import Bot

prefs = Prefs()
dict = Dictionary()
bot = Bot(token=prefs.bot_token)
interactive_kb = InteractiveKeyboard()
db = DataBase()
rt = Router()

@rt.callback_query(F.data == "verify_human")
async def verify_human(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await db.update_settings_by_chat_id(callback.message.chat.id, {
        "last_captcha_time" : datetime.now() + timedelta(hours=1)
    })
    answer = await callback.message.edit_text(
        "✅ Проверка пройдена!\n",
        reply_markup=None
    )
    await Utils.delete_old_message([answer], 5)