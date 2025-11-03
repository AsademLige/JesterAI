from src.models.custom_sticker_model import CustomStickerModel
from src.domain.utils.media import get_media_by_custom_sticker
from src.services.data_base.db import DataBase
from aiogram.types import Message, InputFile
from src.data.config import Prefs
from aiogram import Router, F
from typing import Optional
from aiogram import Bot


prefs = Prefs()
bot = Bot(token=prefs.bot_token)
db = DataBase()
rt = Router()

@rt.message(F.sticker)
async def func_name(message: Message):
    if (message.sticker is None):
        return
    custom_sticker : Optional[CustomStickerModel] = await db.\
        get_custom_sticker_by_id(message.sticker.file_unique_id)
    
    if (custom_sticker is None): return None

    media : Optional[InputFile] = get_media_by_custom_sticker(custom_sticker)

    if (media is None): return None

    await message.delete()
    await bot.send_video(message.chat.id, media)
        
        