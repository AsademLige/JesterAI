from src.domain.states.create_sticker_set import CreateStickerSet
from aiogram.types import Message, InputSticker, InputFile
from src.domain.utils.media import create_input_file
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, StateFilter
from src.handlers.commands import Commands as cn
from src.services.data_base.db import DataBase
from aiogram.types import StickerSet, Message
from aiogram.fsm.context import FSMContext
from src.data.dictionary import Dictionary
from src.data.config import Prefs
from aiogram import Router, F
from typing import Optional
from aiogram import Bot


prefs = Prefs()
bot = Bot(token=prefs.bot_token)
db = DataBase()
rt = Router()

# if (await bot.delete_sticker_set("test_misha_by_ChamomileJesterBot"))

### Выбор названия набора стикеров
@rt.message(StateFilter(None), Command(cn.create_sticker_set))
async def create_sticker_set_short_name_handler(message: Message, state: FSMContext):
    await state.set_state(CreateStickerSet.set_title)
    await message.answer("✏️ Введи короткое название стикер-пака латиницей: ")

### Выбор заголовка набора стикеров
@rt.message(CreateStickerSet.set_title)
async def create_sticker_set_title_handler(message: Message, state: FSMContext):
    if not (await validate_name(message, state)): 
        await message.answer("🔻 Недопустимые символы в названии, попробуй другое название")
        return
    await state.update_data(user_id = message.from_user.id, short_name = message.text)
    await state.set_state(CreateStickerSet.set_sticker_emoji)
    await message.answer("✏️ Введи Заголовок набора стикеров: ")

### Создание стикера, выбор эмодзи
@rt.message(CreateStickerSet.set_sticker_emoji)
async def create_sticker_set_first_sticker_emoji_handler(message: Message, state: FSMContext):
    await state.update_data(title = message.text)
    await state.set_state(CreateStickerSet.set_sticker)
    await message.answer("✏️ Отправь эмодзи, который будет ассоциирован со стикером: ")

### Создание стикера, выбор стикера
@rt.message(CreateStickerSet.set_sticker)
async def create_sticker_set_first_sticker_file_handler(message: Message, state: FSMContext):
    await state.update_data(sticker_emoji = message.text)
    await state.set_state(CreateStickerSet.complete)
    await message.answer("✏️ отправь видео в формате mp4 или webm, которое станет стикером: ")

### Завершение создания набора стикеров
@rt.message(CreateStickerSet.complete)
async def create_sticker_set_format_handler(message: Message, state: FSMContext):
    answer = await message.answer("Обрабатываю...")

    state_data = await state.get_data()

    if (message.video is None):
        await answer.delete()
        await message.answer("Формат не подходящий, попробуй еще что-нибудь отправить")
        return
    
    video:Optional[InputFile] = await create_input_file(bot, message.video.file_id)

    if (video is None):
        await answer.delete()
        await message.answer("Ошибка во время конвертации")
        return
    
    # await bot.send_video(message.chat.id, video)

    sticker = InputSticker(sticker=video, format="video", emoji_list=[state_data["sticker_emoji"]])


    bot_info = await bot.get_me()
    bot_name:str = f"{state_data['short_name']}_by_{bot_info.username}"

    try:
        if (await bot.create_new_sticker_set(message.from_user.id, 
                                         bot_name, 
                                         state_data['title'], [sticker],
                                         None, None, "video")):
            await answer.delete()
            await message.answer(Dictionary.sticker_set_create_success(bot_name))

        else:
            await answer.delete()
            await message.answer(Dictionary.error_sticker_set_create)
    except:
        await answer.delete()
        await message.answer(Dictionary.error_sticker_set_create)
        
    await state.clear()

# ### Создание стикера, выбор медиа файла замены
# @rt.message(CreateStickerSet.set_sticker_media)
# async def create_sticker_set_media_choice_file_handler(message: Message, state: FSMContext):
#     await state.update_data(sticker_emoji = message.text)
#     await state.set_state(CreateStickerSet.complete)
#     await message.answer("✏️ отправь видео в формате mp4 или webm, которое станет стикером: ")

async def validate_name(message: Message, state: FSMContext) -> str:
    valid = True
    for c in message.text:
        if (c in ['/', '\\', '*', '(', ')', '.', '@', '`', ]): valid = False

    return valid

async def pack_exists(get_sticker_set, pack_id: str) -> bool:
    try:
        await get_sticker_set(pack_id)
    except TelegramBadRequest:
        return False
    return True