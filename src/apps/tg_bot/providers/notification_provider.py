
from core.providers.notification_provider import INotificationProvider
from core.utils.app_herald import AppHerald
from aiogram.enums import ParseMode
from aiogram import Bot
import logging

from core.utils.utils import Utils

class TelegramNotificationProvider(INotificationProvider):
    def __init__(self, bot: Bot):
        self.logger = AppHerald()
        self.bot = bot

    async def notifivcate(self, receiver_id: int, message:str, delete_delay:int = -1) -> bool:
        try:
            notify = await self.bot.send_message(receiver_id, message, parse_mode=ParseMode.HTML)
            if (delete_delay > 0):
                await Utils.delete_old_message([notify], delete_delay)
        except Exception as e:
            self.logger.send_log("telegram_scheduler", logging.ERROR, f"Failed to send message to {receiver_id}: {e}")