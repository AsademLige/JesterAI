from src.domain.utils.app_herald import AppHerald
from src.services.data_base.db import DataBase
from src.models.user_model import UserModel
from src.data.dictionary import Dictionary
from typing import Dict, List, Optional
from aiogram.enums import ParseMode
from src.data.config import Prefs
from aiogram import Bot
import logging
import random

db = DataBase()
dict = Dictionary()
prefs = Prefs()
bot = Bot(token=prefs.bot_token)
logger:AppHerald = AppHerald()

class SchedulerJobs():
    @staticmethod
    async def weekly_top():
        """
        Еженедельное подведение итогов размера {{pencil_accu}}
        Каждая группа имеет свой топ и своих победителей
        """
        users: List[UserModel] = await db.get_all_users()
        indexed_users: Dict[int, List[UserModel]] = {}

        for user in users:
            if (user.chat_id is not None):
                if (user.chat_id not in indexed_users):
                    indexed_users[user.chat_id] = []
                indexed_users[user.chat_id].append(user)

        for chat_id in indexed_users:
            try:
                await bot.get_chat(chat_id)

                rewards: List[int] = [random.randrange(30, 40),
                                random.randrange(15, 25),
                                random.randrange(5, 10)]
                
                sorted_users: List[UserModel] = sorted(indexed_users[chat_id], 
                                                    key=lambda u: u.length,
                                                    reverse=True)
                for index, reward in enumerate(rewards):
                    if (len(sorted_users) > index):
                        await db.update_user(sorted_users[index], {
                            "money" : reward + sorted_users[index].money
                        })

                await bot.send_message(chat_id, 
                                    dict.weekly_winners(
                                        sorted_users,
                                        rewards), 
                                    parse_mode=ParseMode.HTML)
            except Exception as e:
                logger.send_log("apscheduler", logging.WARNING, f"weekly_top - {e}")
    
    @staticmethod
    async def day_draw():
        """
        Ежедневный розыгрыш мази увеличения {{pencil_accu}}
        Каждая группа получает своего победителя
        """
        users: List[UserModel] = await db.get_daily_draw_participants()
        indexed_users: Dict[int, List[UserModel]] = {}

        for user in users:
            if (user.chat_id is not None):
                if (user.chat_id not in indexed_users):
                    indexed_users[user.chat_id] = []
                indexed_users[user.chat_id].append(user)

        for chat_id in indexed_users:
            try:
                await bot.get_chat(chat_id)
                if (not indexed_users[chat_id]): continue

                draw_winner_index:int = 0 if (len(indexed_users[chat_id]) == 1) \
                                        else random.randrange(0, len(indexed_users[chat_id]) - 1)
                
                last_winner:Optional[UserModel] = await db.get_last_day_draw_winner_in_chat(chat_id)
                length_change:int = random.randrange(1, 7)
                
                await db.update_user(indexed_users[chat_id][draw_winner_index],
                                     {"last_daily_draw_winner" : True,
                                      "length" : indexed_users[chat_id][draw_winner_index].length + length_change})
                
                if (last_winner is not None):
                    await db.update_user(last_winner, {"last_daily_draw_winner":False})
                
                await bot.send_message(chat_id, dict.draw(indexed_users[chat_id][draw_winner_index], length_change), 
                                    parse_mode=ParseMode.HTML)
            except Exception as e:
                logger.send_log("apscheduler", logging.WARNING, f"day_draw - {e}")