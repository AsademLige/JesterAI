from features.bestiary.data.repository.gino_bestiary_repository import GinoBestiaryRepository
from features.user.data.repository.gino_user_repository import GinoUserRepository
from apps.tg_bot.keyboards.bestiary_keyboard import BestiaryKeyboard
from aiogram.types import CallbackQuery, InlineKeyboardMarkup
from apps.tg_bot.keyboards.callback_fabrics import BestiaryCF
from features.user.data.dtos.user_dto import User
from aiogram.exceptions import TelegramAPIError
from core.consts.dictionary import Dictionary
from aiogram.enums import ParseMode
from aiogram import Router, F
from typing import Optional

rt = Router()
dict = Dictionary()
bestiary_repo = GinoBestiaryRepository()
bestiary_kb = BestiaryKeyboard()
user_repo = GinoUserRepository()


async def _get_user(callback: CallbackQuery, callback_data: BestiaryCF) -> Optional[User]:
    """Пользователь из кэша; чужие нажатия на кнопки отбрасываются."""
    user = await user_repo.get_user(callback.from_user.id)
    if not user or user.tg_id != callback_data.user_id:
        return None
    return user

async def _edit(callback: CallbackQuery, text: str, markup: InlineKeyboardMarkup) -> None:
    try:
        await callback.message.edit_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)
    except TelegramAPIError:
        await callback.answer("Экран устарел, открой /me заново", show_alert=True)
        return
    await callback.answer()

@rt.callback_query(BestiaryCF.filter(F.action.in_({"open", "menu"})))
async def on_bestiary_menu(callback: CallbackQuery, callback_data: BestiaryCF):
    user = await _get_user(callback, callback_data)
    if not user:
        return

    sections = await bestiary_repo.get_bestiary(user)
    await _edit(callback, dict.bestiary_menu(user, sections), bestiary_kb.menu(user))

@rt.callback_query(BestiaryCF.filter(F.action == "section"))
async def on_bestiary_section(callback: CallbackQuery, callback_data: BestiaryCF):
    user = await _get_user(callback, callback_data)
    if not user:
        return

    sections = await bestiary_repo.get_bestiary(user)
    await _edit(callback, dict.bestiary_section(callback_data.kind, sections.get(callback_data.kind) or []),
                bestiary_kb.section(user))

@rt.callback_query(BestiaryCF.filter(F.action == "close"))
async def on_bestiary_close(callback: CallbackQuery, callback_data: BestiaryCF):
    user = await _get_user(callback, callback_data)
    if not user:
        return

    try:
        await callback.message.delete()
    except TelegramAPIError:
        pass
    await callback.answer()
