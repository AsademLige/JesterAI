from src.models.discounts_model import ProductDiscounts
from src.domain.utils.app_herald import AppHerald
from typing import Dict, List, Optional, Tuple
from src.services.data_base.db import DataBase
from src.data.dictionary import Dictionary
from src.models.item_model import Item
from src.models.user_model import User
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
        users: List[User] = await db.get_all_users()
        indexed_users: Dict[int, List[User]] = {}

        for user in users:
            if (user.chat_id is not None):
                if (user.chat_id not in indexed_users):
                    indexed_users[user.chat_id] = []
                indexed_users[user.chat_id].append(user)

        for chat_id in indexed_users:
            try:
                await bot.get_chat(chat_id)

                rewards: List[int] = [15, 10, 5]
                sorted_users: List[User] = sorted(indexed_users[chat_id], 
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
    async def day_salary():
        """
        Ежедневная получка для работяг
        """
        await SchedulerJobs.give_all(dict.day_salary(10), 10)

    @staticmethod
    async def tech_work_compensation():
        """
        Премия в честь обновления (без таймера, ручной запуск)
        """
        await SchedulerJobs.give_all(dict.tech_work_compensation(15), 15)

    @staticmethod
    async def give_all(message: str, money:int):
        """
        Общий метод выдачи монеток всем игрокам
        """
        users: List[User] = await db.get_all_users()
        indexed_users: Dict[int, List[User]] = {}

        for user in users:
            if (user.chat_id is not None):
                if (user.chat_id not in indexed_users):
                    indexed_users[user.chat_id] = []
                indexed_users[user.chat_id].append(user)

        for chat_id in indexed_users:
            try:
                # Исключение продовых чатов для теста
                # if (chat_id == -1001603124529 or chat_id == -1001710720148): continue

                await db.update_users_money_by_chat(chat_id, money)

                await bot.send_message(chat_id, 
                                    message, 
                                    parse_mode=ParseMode.HTML)
                
            except Exception as e:
                    logger.send_log("apscheduler", logging.WARNING, f"day_salary - {e}")
    
    @staticmethod
    async def day_draw():
        """
        Ежедневный розыгрыш мази увеличения {{pencil_accu}}
        Каждая группа получает своего победителя
        """
        users: List[User] = await db.get_daily_draw_participants()
        indexed_users: Dict[int, List[User]] = {}

        for user in users:
            if (user.chat_id is not None):
                if (user.chat_id not in indexed_users):
                    indexed_users[user.chat_id] = []
                indexed_users[user.chat_id].append(user)

        for chat_id in indexed_users:
            try:
                await bot.get_chat(chat_id)
                if (not indexed_users[chat_id]): continue

                sorted_users: List[User] = sorted(indexed_users[chat_id], 
                                                    key=lambda u: u.length,
                                                    reverse=True)
                
                draw_winner_index:int = 0
                
                if (len(sorted_users) <= 3):
                    draw_winner_index = random.randrange(0, len(sorted_users) - 1)
                else:
                    draw_winner_index = random.randrange(2, len(sorted_users) - 1)
                
                last_winner:Optional[User] = await db.get_last_day_draw_winner_in_chat(chat_id)
                length_change:int = random.randrange(5, 10)
                
                await db.update_user(sorted_users[draw_winner_index],
                                     {"last_daily_draw_winner" : True,
                                      "length" : sorted_users[draw_winner_index].length + length_change})
                
                if (last_winner is not None):
                    await db.update_user(last_winner, {"last_daily_draw_winner":False})
                
                await bot.send_message(chat_id, dict.draw(sorted_users[draw_winner_index], length_change), 
                                    parse_mode=ParseMode.HTML)
            except Exception as e:
                logger.send_log("apscheduler", logging.WARNING, f"day_draw - {e}")

    @staticmethod
    async def warehouse_update():
        """
        Ежедневное пополнение остатков магазина
        """
        try:
            if (await db.update_warehouse()):
                await db.deactivate_discounts()
                discounts:List[Tuple[ProductDiscounts, Item]] = await db.create_random_discount(2)

                users: List[User] = await db.get_all_users()
                indexed_users: Dict[int, List[User]] = {}

                for user in users:
                    if (user.chat_id is not None):
                        if (user.chat_id not in indexed_users):
                            indexed_users[user.chat_id] = []
                        indexed_users[user.chat_id].append(user)

                for chat_id in indexed_users:
                    # Исключение продовых чатов для теста
                    # if (chat_id == -1001603124529 or chat_id == -1001710720148): continue

                    await bot.send_message(chat_id, dict.warehouse_update(discounts), 
                                    parse_mode=ParseMode.HTML)     

        except Exception as e:
            logger.send_log("apscheduler", logging.WARNING, f"warehouse_update - {e}")

                
