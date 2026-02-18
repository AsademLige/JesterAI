from src.domain.controllers.rights_controller import RightsController
from src.models.custom_sticker_model import CustomStickerModel
from src.domain.utils.media import get_media_by_custom_sticker
from src.models.sticker_set_model import StickerSetModel
from src.handlers.commands import Commands as cn
from aiogram.filters import Command, StateFilter
from src.services.data_base.db import DataBase
from aiogram.types import Message, InputFile
from src.data.dictionary import Dictionary
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from typing import Optional, List
from src.data.config import Prefs
from aiogram import Router, F
from aiogram import Bot


prefs = Prefs()
dict = Dictionary()
bot = Bot(token=prefs.bot_token)
db = DataBase()
rt = Router()

###Отправляем ссылку на набор стикеров
@rt.message(StateFilter(None), Command(cn.sticker_pack))
async def get_sticker_pack(message: Message, state: FSMContext):
    sets:List[StickerSetModel] = await db.get_all_sticker_sets()
    if sets:
        await message.answer(dict.get_sticker_set_link(sets[0].short_name))
    else:
        await message.answer("Ничего нет...")

@rt.message(F.sticker)
async def get_media_by_sticker(message: Message):
    if (not await RightsController.check_is_admin(message.chat.id)):
        await message.answer("У меня прав меньше чем у посудомойки, дайте админку!")
        return

    if (not await RightsController.check_delete_messages_rights(message.chat.id)):
        await message.answer("Я не могу удалять сообщения, дайте прав!")
        return

    if (message.sticker is None):
        return
    custom_sticker : Optional[CustomStickerModel] = await db.\
        get_custom_sticker_by_id(message.sticker.file_unique_id)
    
    if (custom_sticker is None): return None
    
    user = await db.get_user(message.from_user.id)
    
    try:
        await message.delete()
    except:
        print("delete message error")

    loading_message = await bot.send_message(message.chat.id, "Ждем, пока телега распердится...")
    
    media : Optional[InputFile] = get_media_by_custom_sticker(custom_sticker)

    if (media is None): return None
    
    await bot.send_video(message.chat.id, media,
                         caption=dict.media_caption(user) if (user) else "",
                         parse_mode=ParseMode.HTML)

    await loading_message.delete()
        