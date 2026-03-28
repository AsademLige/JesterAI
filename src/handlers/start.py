from src.keyboards.callback_fabrics import HelpCF
from src.keyboards.system_keyboard import SystemKeyboard
from aiogram.types import CallbackQuery, Message
from src.handlers.commands import Commands as cn
from src.services.data_base.db import DataBase
from src.data.dictionary import Dictionary
from aiogram.filters import Command
from aiogram.enums import ParseMode
from src.data.config import Prefs
from aiogram import Router, F
from aiogram import Bot

prefs = Prefs()
bot = Bot(token=prefs.bot_token)
system_kb = SystemKeyboard()
dict = Dictionary()
db = DataBase()
rt = Router()

### Запустить бота
@rt.message(Command(cn.start))
async def start_handler(message: Message):
    await message.answer(dict.bot_description)

### Что умеет бот
@rt.message(Command(cn.help))
async def help_handler(message: Message):
    await message.answer(dict.bot_description, 
                         reply_markup=system_kb.help_btns(),
                         parse_mode=ParseMode.HTML)
    
###Действие защиты
@rt.callback_query(HelpCF.filter(F.action == "hunt"))
async def on_turn_defense(callback: CallbackQuery):
    await callback.message.edit_text("УЭЭЭЭЭЭЭЭЭЭЭ",
                                     reply_markup=system_kb.help_hunt_btns(),
                                     parse_mode=ParseMode.HTML)

    