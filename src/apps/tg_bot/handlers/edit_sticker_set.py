from apps.tg_bot.keyboards.create_sticker_set_keyboard import CreateStickerSetKeyboard
from apps.tg_bot.keyboards.edit_sticker_set_keyboard import EditStickerSetKeyboard
from core.data.models.custom_sticker_model import CustomSticker
from apps.tg_bot.states.edit_sticker_set import EditStickerSet
from aiogram.types import Message, InputSticker, FSInputFile
from aiogram.types import Message, CallbackQuery, StickerSet
from core.data.models.sticker_set_model import StickerSet
from apps.tg_bot.keyboards.callback_fabrics import StickerSetCF
from apps.tg_bot.commands import Commands as cn
from aiogram.filters import Command, StateFilter
from core.data.data_base import DataBase
from typing import List, Any, Dict, Optional
from aiogram.fsm.context import FSMContext
from core.consts.dictionary import Dictionary
import core.utils.media as media
from core.consts.config import Prefs
from aiogram import Router, F
from aiogram import Bot

prefs = Prefs()
dict = Dictionary()
bot = Bot(token=prefs.bot_token)
db = DataBase()
rt = Router()
edit_kb = EditStickerSetKeyboard()
create_kb = CreateStickerSetKeyboard()

### Список доступных наборов стикеров
@rt.message(StateFilter(None), Command(cn.edit_sticker_set))
async def sticker_set_choice_handler(message: Message, state: FSMContext):
    if (not await db.is_admin(message.from_user.id)):
        await message.answer("Не по масти тебе такие команды мне давать... ")    
        return
    await state.update_data(user_id = message.from_user.id)
    
    await state.set_state(EditStickerSet.edit_sticker_set)
    sticker_set_list:List[StickerSet] = await db.get_all_sticker_sets()
    if (sticker_set_list):
        await message.answer(dict.choice_sticker_set, 
                         reply_markup = edit_kb.sticker_set_list_button(sticker_set_list))
    else:
        await message.answer(dict.sticker_set_list_is_empty)
        await state.clear()

### Выбор действия
@rt.callback_query(EditStickerSet.edit_sticker_set, StickerSetCF.filter())
async def edit_sticker_set_handler(callback: CallbackQuery, callback_data: StickerSetCF, state: FSMContext):
    state_data = await state.get_data()
    if (callback_data.action == "choice"):
        await callback.message.edit_text(dict.sticker_edit_variants, 
                                                       reply_markup = edit_kb.edit_sticker_set_command_button(callback_data.id))
        await state.update_data(set_id = callback_data.id)
    elif (callback_data.action == "delete_set"):
        await callback.message.edit_text("⚠️ Ты уверен, что хочешь УДАЛИТЬ набор?", 
                                         reply_markup=edit_kb.confirm_delete(state_data["set_id"]))
    elif (callback_data.action == "confirm_delete_set"):
        await callback.message.edit_text(await delete_sticker_set(state_data["set_id"]))
        await state.clear()
    elif (callback_data.action == "add_sticker"):
        await callback.message.edit_text("Отправь эмодзи, который будет ассоциирован с стикером:")
        await state.set_state(EditStickerSet.add_sticker_set_sticker)
    elif (callback_data.action == "delete_sticker"):
        await callback.message.edit_text("Отправь стикер, который хочешь удалить:", 
                                         reply_markup=edit_kb.back(state_data["set_id"]))
        await state.set_state(EditStickerSet.delete_sticker_from_set)
    elif (callback_data.action == "exit"):
        await callback.message.delete()
        await state.clear()

### Создание стикера, выбор эмодзи
@rt.message(EditStickerSet.delete_sticker_from_set)
async def delete_sticker_from_set_handler(message: Message, state: FSMContext):
    if (message.sticker is not None):
         custom_sticker : Optional[CustomSticker] = await db.\
            get_custom_sticker_by_id(message.sticker.file_unique_id)
         if (custom_sticker is not None):
            if (await bot.delete_sticker_from_set(message.sticker.file_id)
                and media.delete_file(custom_sticker.media_path)
                and await db.delete_custom_sticker_by_id(custom_sticker.sticker_id)):
                await message.answer("🟢 Удалили успешно!")
            else:
                await message.answer("🔴 Что-то пошло не так при удалении...")
            await state.clear()
         else:
             await message.answer("Это не мой стикер!")
    else:
        await message.answer("Это не стикер, дурья твоя бошка!")    
    

### Создание стикера, выбор эмодзи
@rt.message(EditStickerSet.add_sticker_set_sticker)
async def add_sticker_set_emoji_handler(message: Message, state: FSMContext):
    await state.update_data(sticker_emoji = message.text)
    await message.answer("✏️ отправь видео в формате mp4 или webm, которое станет стикером: ")
    await state.set_state(EditStickerSet.add_sticker_set_text_to_sticker_clip)

### Создание стикера, текстовой надпись в стикере
@rt.message(EditStickerSet.add_sticker_set_text_to_sticker_clip)
async def add_sticker_set_text_to_clip_handler(message: Message, state: FSMContext):
    if (message.video is None):
        await message.answer("Формат не подходящий, попробуй еще что-нибудь отправить")
        return
    
    await state.update_data(sticker_file_id = message.video.file_id)

    await message.answer("✏️ Можешь добавить короткую надпись, которая будет отображена поверх стикера: ", 
                         reply_markup=create_kb.clip_text_choice)
    await state.set_state(EditStickerSet.add_sticker_set_sticker_media)

### Создание стикера, выбор медиа файла для подмены
@rt.message(EditStickerSet.add_sticker_set_sticker_media)
async def add_sticker_set_media_choice_file_handler(message: Message, state: FSMContext):
    await state.update_data(clip_text = message.text)
    await message.answer("✏️ Можешь отправить видео, которое будет привязано к стикеру или использовать текущее: ", 
                         reply_markup=create_kb.media_choice)
    await state.set_state(EditStickerSet.add_sticker_complete)

### Создание стикера, выбор медиа файла для подмены
@rt.callback_query(EditStickerSet.add_sticker_set_sticker_media)
async def add_sticker_set_media_choice_file_callback_handler(callback: CallbackQuery, state: FSMContext):
    if (callback.data == "skip"):
        await state.update_data(clip_text = "")
        await callback.message.edit_text("✏️ Можешь отправить видео, которое будет привязано к стикеру или использовать текущее: ", 
                         reply_markup=create_kb.media_choice)
        await state.set_state(EditStickerSet.add_sticker_complete)
    else:
        await state.clear()

### Завершение создания стикера
@rt.message(EditStickerSet.add_sticker_complete)
async def create_sticker_set_handler(message: Message, state: FSMContext):
    state_data = await state.get_data()
    if (message.video is None):
            await message.edit_text("🟠 Формат не подходящий, попробуй еще что-нибудь отправить")
            return

    await message.edit_text("Обрабатываю...")
    await message.edit_text(await create_sticker(state_data))
    await state.clear()

### Завершение создания стикера
@rt.callback_query(EditStickerSet.add_sticker_complete)
async def create_sticker_set_complete_callback_handler(callback: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    
    await callback.message.edit_text("Обрабатываю...")
    await callback.message.edit_text(await create_sticker(state_data))
    await state.clear()

###-----------------------------------
###Методы
###-----------------------------------
async def delete_sticker_set(set_id:int) -> str:
    db_set:StickerSet = await db.get_sticker_set_by_id(set_id)
    custom_stickers: List[CustomSticker] = await db.get_custom_stickers_by_set_name(db_set.short_name)
    if (await db.delete_sticker_set_by_name(db_set.short_name)):
        for custom_sticker in custom_stickers:
            media.delete_file(custom_sticker.media_path)
        await bot.delete_sticker_set(db_set.short_name)
        return dict.delete_sticker_set_success
    else:
        return dict.error
    
async def create_sticker(state_data: Dict[str, Any]) -> str:
    video_paths:List[str] = await media.make_sticker_webm_video(bot, 
                                                                    state_data["sticker_file_id"], 
                                                                    state_data["clip_text"])
    if (video_paths is None):
        return "🔴 Ошибка во время конвертации, закрываем лавочку..."

    raw_sticker = InputSticker(sticker=FSInputFile(path=video_paths[0]), 
                               format="video", emoji_list=[state_data["sticker_emoji"]])
    
    db_set:StickerSet = await db.get_sticker_set_by_id(state_data["set_id"])
    
    if (await bot.add_sticker_to_set(state_data["user_id"], db_set.short_name, raw_sticker)):
        sticker_set: StickerSet = await bot.get_sticker_set(db_set.short_name)
        sticker_path = media.save_file(open(video_paths[1], "rb").read(), 
                                                          sticker_set.stickers[-1].file_unique_id)
        if (sticker_path):
            await db.add_custom_sticker(sticker_path, sticker_set.stickers[-1].file_unique_id, db_set.short_name)
        return dict.sticker_add_to_set_success(db_set.short_name)
    else:
        return "🔴 Ошибка при добавлении стикера"

    
    