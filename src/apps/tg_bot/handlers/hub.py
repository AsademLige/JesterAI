from features.user.data.repository.gino_user_repository import GinoUserRepository
from apps.tg_bot.keyboards.hub_keyboard import get_hub_keyboard, fishing_button
from apps.tg_bot.handlers.gamba_house import process_gamba_house
from aiogram.types import CallbackQuery, Message, FSInputFile
from features.user.data.dtos.user_dto import User
from aiogram.filters import Command, StateFilter
from core.consts.dictionary import Dictionary
from core.consts.consts import Consts
from core.consts.config import Prefs
from aiogram.enums import ParseMode
from aiogram import F, Bot, Router
from core.utils.utils import Utils
from ssl import SSLContext
import os

rt = Router()
dict = Dictionary()
prefs = Prefs()
bot = Bot(token=prefs.bot_token)
user_repo:GinoUserRepository = GinoUserRepository()

@rt.message(StateFilter(None), Command("hub"))
async def show_hub(message: Message, state: SSLContext):
    await message.delete()
    photo = FSInputFile(os.path.join(Consts.IMAGES_DIR, f"hub.webp"))

    message = await bot.send_photo(message.chat.id, photo, caption="<blockquote>🌳 На перепутье я стою, болт задумчиво чешу...</blockquote>",  
                         reply_markup = get_hub_keyboard(),
                                      parse_mode=ParseMode.HTML)

    await Utils.delete_old_message([message], 30)

@rt.callback_query(StateFilter(None), F.data == "gamba_house")
async def gamba_house_callback(callback: CallbackQuery, state: SSLContext):
    await process_gamba_house(user_tg_id=callback.from_user.id, message=callback.message, state=state)
    await callback.answer()

###Отправиться на Рыбалку
@rt.callback_query(StateFilter(None), F.data == "hub_fishing")
async def fishing_init(callback_query: CallbackQuery, state: SSLContext):
    message = callback_query.message
        
    user: User = await user_repo.get_user(callback_query.from_user.id, message.chat.id)

    await message.delete()
    if (user.energy > 0):
        await user_repo.update(user, energy=user.energy - 1)
    else:
        answer = await bot.send_message(user.chat_id, 
                                        dict.energy_drain(user), 
                                parse_mode=ParseMode.HTML)
        await Utils.delete_old_message([answer], 10)
        return

    link_message = await bot.send_message(callback_query.message.chat.id, f"🎣 <a href='tg://user?id={user.tg_id}'> Вперед, на рыбалку!</a>", 
                                            reply_markup=fishing_button(""),
                                            parse_mode=ParseMode.HTML)

###Выход
@rt.callback_query(StateFilter(None), F.data == "exit")
async def exit(callback_query: CallbackQuery, state: SSLContext):
    await callback_query.message.delete()
