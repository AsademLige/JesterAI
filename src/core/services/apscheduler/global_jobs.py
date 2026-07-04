from domain.controllers.bot_settings_controller import SettingsController
from features.items.data.models.store_item_dto import StoreItem
from features.store.data.models.discounts_model_orm import ProductDiscountORM
from features.store.data.repository.gino_store_repository import GinoStoreRepository
from features.user.data.repository.gino_user_repository import GinoUserRepository
from features.items.data.models.item_orm import ItemORM
from features.user.data.dtos.user_dto import User
from typing import Dict, List, Optional, Tuple
from core.utils.app_herald import AppHerald
from core.data.data_base import DataBase
from core.consts.config import Prefs
import logging
import random


logger:AppHerald = AppHerald()
user_repo:GinoUserRepository = GinoUserRepository()
store_repo:GinoStoreRepository = GinoStoreRepository()
db = DataBase()
prefs = Prefs()

class GlobalJobs():
    @staticmethod
    async def weekly_top(notifier_func):
        """
        Еженедельное подведение итогов размера {{pencil_accu}}
        Каждая группа имеет свой топ и своих победителей
        """
        users: List[User] = await user_repo.get_users()
        indexed_users: Dict[int, List[User]] = {}

        for user in users:
            if (user.chat_id is not None):
                if (user.chat_id not in indexed_users):
                    indexed_users[user.chat_id] = []
                indexed_users[user.chat_id].append(user)

        for chat_id in indexed_users:
            try:
                settings = await SettingsController.get_settings(chat_id, "")
                if (not settings.events_enabled): continue
                
                rewards: List[int] = [15, 10, 5]
                sorted_users: List[User] = sorted(indexed_users[chat_id], 
                                                    key=lambda u: u.length,
                                                    reverse=True)
                for index, reward in enumerate(rewards):
                    if (len(sorted_users) > index):
                        await user_repo.update(sorted_users[index], {
                            "money" : reward + sorted_users[index].money
                        })
                
                await notifier_func(chat_id, "weekly_winners", {"sorted_users": sorted_users, "rewards": rewards})
            except Exception as e:
                logger.send_log("apscheduler", logging.WARNING, f"weekly_top - {e}")

    @staticmethod
    async def day_salary(notifier_func):
        """
        Ежедневная получка для работяг
        """
        await GlobalJobs.give_all(10, notifier_func, "day_salary")

    @staticmethod
    async def tech_work_compensation(notifier_func):
        """
        Премия в честь обновления (без таймера, ручной запуск)
        """
        await GlobalJobs.give_all(15, notifier_func, "tech_work_compensation")

    @staticmethod
    async def give_all(money:int, notifier_func, event:str):
        """
        Общий метод выдачи монеток всем игрокам
        """
        users: List[User] = await user_repo.get_users()
        indexed_users: Dict[int, List[User]] = {}

        for user in users:
            if (user.chat_id is not None):
                if (user.chat_id not in indexed_users):
                    indexed_users[user.chat_id] = []
                indexed_users[user.chat_id].append(user)

        for chat_id in indexed_users:
            try:
                settings = await SettingsController.get_settings(chat_id, "")
                if (not settings.events_enabled): continue

                await user_repo.update_users_money_by_chat(chat_id, money)
                
                await notifier_func(chat_id, event, {"money": money})
            except Exception as e:
                    logger.send_log("apscheduler", logging.WARNING, f"day_salary - {e}")
    
    @staticmethod
    async def day_draw(notifier_func):
        """
        Ежедневный розыгрыш мази увеличения {{pencil_accu}}
        Каждая группа получает своего победителя
        """
        users: List[User] = await user_repo.get_users(last_daily_draw_winner=False)
        indexed_users: Dict[int, List[User]] = {}

        for user in users:
            if (user.chat_id is not None):
                if (user.chat_id not in indexed_users):
                    indexed_users[user.chat_id] = []
                indexed_users[user.chat_id].append(user)

        for chat_id in indexed_users:
            try:
                settings = await SettingsController.get_settings(chat_id, "")
                if (not settings.events_enabled): continue

                if (not indexed_users[chat_id]): continue

                sorted_users: List[User] = sorted(indexed_users[chat_id], 
                                                    key=lambda u: u.length,
                                                    reverse=True)
                
                draw_winner_index:int = 0
                
                if (len(sorted_users) <= 3):
                    draw_winner_index = random.randrange(0, len(sorted_users) - 1)
                else:
                    draw_winner_index = random.randrange(2, len(sorted_users) - 1)
                
                last_winner:Optional[User] = await user_repo.get_user(chat_id, last_daily_draw_winner=True)
                length_change:int = random.randrange(5, 10)
                
                await user_repo.update(sorted_users[draw_winner_index],
                                     {"last_daily_draw_winner" : True,
                                      "length" : sorted_users[draw_winner_index].length + length_change})
                
                if (last_winner is not None):
                    await user_repo.update(last_winner, {"last_daily_draw_winner":False})
                
                await notifier_func(chat_id, "day_draw", {"winner": sorted_users[draw_winner_index], "length_change": length_change})
            except Exception as e:
                logger.send_log("apscheduler", logging.WARNING, f"day_draw - {e}")

    @staticmethod
    async def warehouse_update(notifier_func):
        """
        Ежедневное пополнение остатков магазина
        """
        try:
            if (await store_repo.update_warehouse()):
                await store_repo.deactivate_discounts()
                items_discounts:List[StoreItem] = await store_repo.create_random_discount(2)

                users: List[User] = await user_repo.get_users()
                indexed_users: Dict[int, List[User]] = {}

                for user in users:
                    if (user.chat_id is not None):
                        if (user.chat_id not in indexed_users):
                            indexed_users[user.chat_id] = []
                        indexed_users[user.chat_id].append(user)

                for chat_id in indexed_users:
                    settings = await SettingsController.get_settings(chat_id, "")
                    if (not settings.events_enabled): continue
                    
                    await notifier_func(chat_id, "warehouse_update", {"discounts": items_discounts})

        except Exception as e:
            logger.send_log("apscheduler", logging.WARNING, f"warehouse_update - {e}")

                
