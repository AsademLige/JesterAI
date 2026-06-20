from core.consts.dictionary import Dictionary
from core.utils.app_herald import AppHerald
from aiogram.enums import ParseMode
from aiogram import Bot
import logging

###TODO: Не хватает абстракции для класса
class TelegramNotificationProvider:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.dict = Dictionary()
        self.logger = AppHerald()

    async def handle_event(self, chat_id: int, event_type: str, data: dict):
        """
        Единая точка входа для всех уведомлений из SchedulerJobs.
        Она распределяет, какой шаблон словаря вызвать.
        """
        try:
            if event_type == "weekly_winners":
                text = self.dict.weekly_winners(data["sorted_users"], data["rewards"])
                await self.bot.send_message(chat_id, text, parse_mode=ParseMode.HTML)

            elif event_type == "day_salary":
                text = self.dict.day_salary(data["money"])
                await self.bot.send_message(chat_id, text, parse_mode=ParseMode.HTML)

            elif event_type == "tech_work_compensation":
                text = self.dict.tech_work_compensation(data["money"])
                await self.bot.send_message(chat_id, text, parse_mode=ParseMode.HTML)

            elif event_type == "day_draw":
                text = self.dict.draw(data["winner"], data["length_change"])
                await self.bot.send_message(chat_id, text, parse_mode=ParseMode.HTML)
                
            elif event_type == "warehouse_update":
                text = self.dict.warehouse_update(data["discounts"])
                await self.bot.send_message(chat_id, text, parse_mode=ParseMode.HTML)

        except Exception as e:
            self.logger.send_log("telegram_scheduler", logging.WARNING, f"Failed to send {event_type}: {e}")