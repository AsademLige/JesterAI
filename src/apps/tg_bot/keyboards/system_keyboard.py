from apps.tg_bot.keyboards.callback_fabrics import HelpCF, JobsCF
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup
from core.consts.dictionary import Dictionary
from core.consts.config import Prefs
from apscheduler.job import Job
from typing import List

prefs = Prefs()
dict = Dictionary()

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