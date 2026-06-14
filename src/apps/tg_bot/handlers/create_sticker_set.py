from aiogram.types import Message, InputSticker, FSInputFile, ReplyKeyboardRemove
from apps.tg_bot.keyboards.create_sticker_set_keyboard import CreateStickerSetKeyboard
from apps.tg_bot.states.create_sticker_set import CreateStickerSet
from aiogram.types import Message, CallbackQuery, StickerSet
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, StateFilter
from apps.tg_bot.commands import Commands as cn
from core.data.datasource import DataBase
from typing import Optional, Dict, Any, List
from aiogram.fsm.context import FSMContext
from core.consts.dictionary import Dictionary
import core.utils.media as media
from core.consts.config import Prefs
from aiogram import Router, F
from aiogram import Bot

prefs = Prefs()
dict = Dictionary()
kb = CreateStickerSetKeyboard()
bot = Bot(token=prefs.bot_token)
db = DataBase()
rt = Router()

### Выбор названия набора стикеров
@rt.message(StateFilter(None), Command(cn.create_sticker_set))
async def create_sticker_set_short_name_handler(message: Message, state: FSMContext):
    # await bot.delete_sticker_set("zip_zap_media_by_ChamomileJesterBot")
    if (not await db.is_admin(message.from_user.id)):
        await message.answer("Не по масти тебе такие команды мне давать... ")    
        return

    await message.answer("✏️ Введи короткое название стикер-пака латиницей: ")
    await state.set_state(CreateStickerSet.set_title)

### Выбор заголовка набора стикеров
@rt.message(CreateStickerSet.set_title)
async def create_sticker_set_title_handler(message: Message, state: FSMContext):
    if not (await validate_name(message, state)): 
        await message.answer("🔻 Недопустимые символы в названии, попробуй другое название")
        return
    await state.update_data(user_id = message.from_user.id, short_name = message.text)

    await message.answer("✏️ Введи Заголовок набора стикеров: ")
    await state.set_state(CreateStickerSet.set_sticker_emoji)

### Создание стикера, выбор эмодзи
@rt.message(CreateStickerSet.set_sticker_emoji)
async def create_sticker_set_first_sticker_emoji_handler(message: Message, state: FSMContext):
    await state.update_data(title = message.text)

    await message.answer("✏️ Теперь создадим первый стикер\n Отправь эмодзи, который будет ассоциирован с стикером: ")
    await state.set_state(CreateStickerSet.set_sticker)

### Создание стикера, выбор стикера
@rt.message(CreateStickerSet.set_sticker)
async def create_sticker_set_first_sticker_file_handler(message: Message, state: FSMContext):
    await state.update_data(sticker_emoji = message.text)

    await message.answer("✏️ отправь видео в формате mp4 или webm, которое станет стикером: ")
    await state.set_state(CreateStickerSet.add_text_to_sticker_clip)

### Создание стикера, текстовой надпись в стикере
@rt.message(CreateStickerSet.add_text_to_sticker_clip)
async def create_sticker_set_add_text_to_clip_handler(message: Message, state: FSMContext):
    if (message.video is None):
        await message.answer("Формат не подходящий, попробуй еще что-нибудь отправить")
        return
    
    await state.update_data(sticker_file_id = message.video.file_id)

    await message.answer("✏️ Можешь добавить короткую надпись, которая будет отображена поверх стикера: ", 
                         reply_markup=kb.clip_text_choice)
    await state.set_state(CreateStickerSet.set_sticker_media)

### Создание стикера, выбор медиа файла для подмены
@rt.message(CreateStickerSet.set_sticker_media)
async def create_sticker_set_media_choice_file_handler(message: Message, state: FSMContext):
    await state.update_data(clip_text = message.text)
    await message.answer("✏️ Можешь отправить видео, которое будет привязано к стикеру или использовать текущее: ", 
                         reply_markup=kb.media_choice)
    await state.set_state(CreateStickerSet.complete)

### Создание стикера, выбор медиа файла для подмены
@rt.callback_query(CreateStickerSet.set_sticker_media)
async def create_sticker_set_media_choice_file_callback_handler(callback: CallbackQuery, state: FSMContext):
    if (callback.data == "skip"):
        await state.update_data(clip_text = "")
        await callback.message.edit_text("✏️ Можешь отправить видео, которое будет привязано к стикеру или использовать текущее: ", 
                         reply_markup=kb.media_choice)
        await state.set_state(CreateStickerSet.complete)
    else:
        state.clear()

@rt.message(CreateStickerSet.set_sticker_media)
async def create_sticker_set_handler(message: Message, state: FSMContext):
    state_data = await state.get_data()
    if (message.video is None):
            await message.edit_text("Формат не подходящий, попробуй еще что-нибудь отправить")
            return
    sticker_media_id = message.video.file_id

    await message.edit_text("Обрабатываю...")
    await message.edit_text(await create_set(state_data, sticker_media_id),)

### Завершение создания набора стикеров
@rt.callback_query(CreateStickerSet.complete)
async def create_sticker_set_callback_handler(callback: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    sticker_media_id: str = state_data["sticker_file_id"]
    
    await callback.message.edit_text("Обрабатываю...")
    await callback.message.edit_text(await create_set(state_data, sticker_media_id))
        
    await state.clear()

async def create_set(state_data: Dict[str, Any], sticker_media_id:int) -> str:
    video_paths:List[str] = await media.make_sticker_webm_video(bot, 
                                                                    state_data["sticker_file_id"], 
                                                                    state_data["clip_text"])
    if (video_paths is None):
        return "Ошибка во время конвертации, закрываем лавочку..."

    raw_sticker = InputSticker(sticker=FSInputFile(path=video_paths[0]), 
                               format="video", emoji_list=[state_data["sticker_emoji"]])


    bot_info = await bot.get_me()
    sticker_set_name:str = f"{state_data['short_name']}_by_{bot_info.username}"

    try:
        if (await bot.create_new_sticker_set(state_data["user_id"], 
                                         sticker_set_name, 
                                         state_data['title'], [raw_sticker],
                                         None, None, "video")):
            sticker_set:StickerSet = await bot.get_sticker_set(sticker_set_name)

            await db.add_sticker_set(sticker_set_name, state_data['title'])

            sticker_path = media.save_file(open(video_paths[1], "rb").read(), 
                                                          sticker_set.stickers[0].file_unique_id)
            if (sticker_path):
                await db.add_custom_sticker(sticker_path, sticker_set.stickers[0].file_unique_id, sticker_set_name)
            return dict.sticker_set_create_success(sticker_set_name)
        else:
            return dict.error_sticker_set_create
    except Exception as e:
        print(f"Ошибка создания стикера: {e}")
        return dict.error_sticker_set_create

async def validate_name(message: Message, state: FSMContext) -> str:
    valid = True
    for c in message.text:
        if (c in ['/', '\\', '*', '(', ')', '.', '@', '`', ]): valid = False

    return valid