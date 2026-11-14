from features.game_engine.data.repository.gino_bot_settings_repository import GinoBotSettingsRepository
from features.game_engine.data.models.bot_settings_dto import BotSettings
from features.user.data.repository.gino_user_repository import GinoUserRepository
from features.store.data.repository.gino_store_repository import GinoStoreRepository
from apps.tg_bot.keyboards.system_keyboard import SystemKeyboard, ADMIN_TOGGLE_FIELDS
from apps.tg_bot.keyboards.callback_fabrics import AdminSettingsCF
from apps.tg_bot.states.system import AdminSettings
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from apps.tg_bot.commands import Commands as cn
from core.consts.dictionary import Dictionary
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from typing import List

from aiogram import Router, F


dict = Dictionary()
system_kb = SystemKeyboard()
user_repo = GinoUserRepository()
store_repo = GinoStoreRepository()
settings_repo = GinoBotSettingsRepository()
rt = Router()

ADMIN_MENU_TEXT:str = "<blockquote>🛠 Панель управления бота</blockquote>\n"\
                      "🗑 <b>Сброс кэша</b> - очистит кэши пользователей, настроек чатов и магазина\n"\
                      "💬 <b>Настройки чатов</b> - включение/выключение событий и фич по чатам"


def chat_settings_text(settings: BotSettings) -> str:
    text:str = f"<blockquote>💬 {settings.alias or 'Unnamed'}</blockquote>\n"\
               f"<code>chat_id: {settings.chat_id}</code>\n\n"
    
    for field, title in ADMIN_TOGGLE_FIELDS:
        icon:str = "✅" if getattr(settings, field) else "❌"
        text += f"{icon} {title}\n"

    return text


async def is_authorized(callback: CallbackQuery) -> bool:
    if (await user_repo.is_admin(callback.from_user.id)): return True
    await callback.answer("⛔️ Не по масти тебе такие кнопки жать...", show_alert=True)
    return False

###Главное меню настроек
@rt.message(StateFilter(None), Command(cn.admin))
async def open_admin_panel(message: Message, state: FSMContext):
    if (not await user_repo.is_admin(message.from_user.id)):
        await message.answer("Не по масти тебе такие команды мне давать... ")
        return

    await state.set_state(AdminSettings.main)
    await message.answer(ADMIN_MENU_TEXT,
                         reply_markup=system_kb.admin_main_menu(),
                         parse_mode=ParseMode.HTML)

###Сброс кэша пользователей, настроек и магазина
@rt.callback_query(AdminSettingsCF.filter(F.action == "cache_reset"))
async def reset_cache(callback: CallbackQuery):
    if (not await is_authorized(callback)): return

    user_repo.clear_cache()
    store_repo.clear_cache()
    settings_repo.clear_cache()

    await callback.answer("🟢 Кэш очищен!", show_alert=True)

###Список чатов с настройками
@rt.callback_query(AdminSettingsCF.filter(F.action == "chat_list"))
async def show_chat_list(callback: CallbackQuery, state: FSMContext):
    if (not await is_authorized(callback)): return

    settings:List[BotSettings] = await settings_repo.get_all()
    if (not settings):
        await callback.answer("❌ Чаты с настройками не найдены", show_alert=True)
        return

    await state.set_state(AdminSettings.chat_list)
    await callback.message.edit_text("<blockquote>💬 Выбери чат для настройки</blockquote>",
                                     reply_markup=system_kb.admin_chat_list(settings),
                                     parse_mode=ParseMode.HTML)

###Меню вкл/выкл фич конкретного чата
@rt.callback_query(AdminSettingsCF.filter(F.action == "chat_choice"))
async def show_chat_toggles(callback: CallbackQuery, callback_data: AdminSettingsCF, state: FSMContext):
    if (not await is_authorized(callback)): return

    settings:BotSettings = await settings_repo.get_settings(callback_data.chat_id)
    if (not settings):
        await callback.answer(dict.error, show_alert=True)
        return

    await state.set_state(AdminSettings.chat_edit)
    await callback.message.edit_text(chat_settings_text(settings),
                                     reply_markup=system_kb.admin_chat_toggles(settings),
                                     parse_mode=ParseMode.HTML)

###Переключение настройки чата
@rt.callback_query(AdminSettingsCF.filter(F.action == "toggle"))
async def toggle_chat_setting(callback: CallbackQuery, callback_data: AdminSettingsCF):
    if (not await is_authorized(callback)): return

    toggle_fields:List[str] = [field for field, _ in ADMIN_TOGGLE_FIELDS]
    if (callback_data.field not in toggle_fields):
        await callback.answer("❌ Неизвестная настройка", show_alert=True)
        return

    settings:BotSettings = await settings_repo.get_settings(callback_data.chat_id)
    if (not settings):
        await callback.answer(dict.error, show_alert=True)
        return

    new_value:bool = not getattr(settings, callback_data.field)
    if (not await settings_repo.update_settings_by_chat_id(callback_data.chat_id,
                                                           {callback_data.field: new_value})):
        await callback.answer(dict.error, show_alert=True)
        return

    settings = await settings_repo.get_settings(callback_data.chat_id)
    await callback.message.edit_text(chat_settings_text(settings),
                                     reply_markup=system_kb.admin_chat_toggles(settings),
                                     parse_mode=ParseMode.HTML)

###Возврат в главное меню
@rt.callback_query(AdminSettingsCF.filter(F.action == "back"))
async def admin_back(callback: CallbackQuery, state: FSMContext):
    if (not await is_authorized(callback)): return

    await state.set_state(AdminSettings.main)
    await callback.message.edit_text(ADMIN_MENU_TEXT,
                                     reply_markup=system_kb.admin_main_menu(),
                                     parse_mode=ParseMode.HTML)

###Выход и очистка состояния
@rt.callback_query(AdminSettingsCF.filter(F.action == "exit"))
async def admin_exit(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
