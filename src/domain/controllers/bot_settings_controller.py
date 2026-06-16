from core.data.models.bot_settings_model import BotSettings
from core.data.data_base import DataBase
from core.consts.config import Prefs
from aiogram import Bot

db = DataBase()
prefs = Prefs()
bot = Bot(token=prefs.bot_token)

class SettingsController():
    @staticmethod
    async def get_settings(chat_id:int, chat_full_name:str) -> BotSettings:
      return await db.get_settings(chat_id, chat_full_name)
        