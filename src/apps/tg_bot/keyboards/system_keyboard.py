from apps.tg_bot.keyboards.callback_fabrics import HelpCF, JobsCF, AdminSettingsCF
from features.game_engine.data.models.bot_settings_dto import BotSettings
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup
from core.consts.dictionary import Dictionary
from core.consts.config import Prefs
from apscheduler.job import Job
from typing import List

prefs = Prefs()
dict = Dictionary()

###Поля BotSettings, доступные для вкл/выкл в админ-панели
ADMIN_TOGGLE_FIELDS:List[tuple] = [
    ("events_enabled", "📅 События"),
    ("me_enabled", "ℹ️ /me"),
    ("hub_enabled", "🪧 /hub"),
    ("pencil_enabled", "🍆 /pencil"),
    ("gamba_house_enabled", "🎰 /gamba_house"),
]

class SystemKeyboard():
    def __init__(self):
        pass

    def help_btns(self) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
            
        builder.button(text="⚔️ Охота",
            callback_data=HelpCF(action="hunt"))
        
        builder.button(text=dict.exit,
            callback_data=HelpCF(action="exit"))
        
        builder.adjust(2)
        
        return builder.as_markup()
    
    def help_hunt_btns(self) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.button(text=dict.exit,
            callback_data=HelpCF(action="exit"))
        
        return builder.as_markup()

    def jobs_list_button(self, jobs: List[Job]) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        for job in jobs:
            builder.button(text=job.id,
                callback_data=JobsCF(action="choice", job_id=job.id))
            
        builder.button(text=dict.exit,
            callback_data=JobsCF(action="exit"))
        
        builder.adjust(2)
        
        return builder.as_markup()
    
    def job_edit_button_list(self) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.button(text=dict.trigger,
            callback_data=JobsCF(action="trigger"))

        builder.button(text=dict.exit,
            callback_data=JobsCF(action="exit"))
        
        builder.adjust(2)
        
        return builder.as_markup()
    
    def admin_main_menu(self) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.button(text="🗑 Сброс кэша",
            callback_data=AdminSettingsCF(action="cache_reset"))

        builder.button(text="💬 Настройки чатов",
            callback_data=AdminSettingsCF(action="chat_list"))

        builder.button(text=dict.exit,
            callback_data=AdminSettingsCF(action="exit"))
        
        builder.adjust(1)
        
        return builder.as_markup()
    
    def admin_chat_list(self, settings: List[BotSettings]) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        for chat_settings in settings:
            builder.button(text=f"{chat_settings.alias or 'Unnamed'} ({chat_settings.chat_id})",
                callback_data=AdminSettingsCF(action="chat_choice", chat_id=chat_settings.chat_id))
            
        builder.button(text=dict.back,
            callback_data=AdminSettingsCF(action="back"))
        
        builder.adjust(1)
        
        return builder.as_markup()
    
    def admin_chat_toggles(self, settings: BotSettings) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        for field, title in ADMIN_TOGGLE_FIELDS:
            icon:str = "✅" if getattr(settings, field) else "❌"
            builder.button(text=f"{icon} {title}",
                callback_data=AdminSettingsCF(action="toggle",
                                              chat_id=settings.chat_id,
                                              field=field))
            
        builder.button(text="💬 Список чатов",
            callback_data=AdminSettingsCF(action="chat_list"))

        builder.button(text=dict.exit,
            callback_data=AdminSettingsCF(action="exit"))
        
        builder.adjust(1)
        
        return builder.as_markup()