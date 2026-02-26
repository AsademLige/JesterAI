from src.models.bot_settings_model import BotSettings
from src.services.data_base.db import DataBase
from src.data.config import Prefs
from aiogram.types import Chat
from aiogram import Bot

db = DataBase()
prefs = Prefs()
bot = Bot(token=prefs.bot_token)

class SettingsController():
    @staticmethod
    async def get_settings(chat:Chat) -> BotSettings:
      return await db.get_settings(chat)
        