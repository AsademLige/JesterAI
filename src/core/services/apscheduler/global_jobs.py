from features.game_engine.data.repository.bot_settings_repository import IBotSettingsRepository
from features.store.data.repository.store_repository import IStoreRepository
from features.user.data.repository.user_repository import IUserRepository
from features.game_engine.data.models.bot_settings_dto import BotSettings
from features.items.data.models.store_item_dto import StoreItem
from features.user.data.dtos.user_dto import User
from core.utils.app_herald import AppHerald
from typing import Dict, List, Optional
import logging
import random

class TestJobTracker:
    def __init__(self):
        self.fired_jobs = {}

    def should_fire(self, job_id: str, current_date: str) -> bool:
        if self.fired_jobs.get(job_id) != current_date:
            self.fired_jobs[job_id] = current_date
            return True
        return False

class GlobalJobs():
    def __init__(self, user_repo:IUserRepository, 
                 store_repo:IStoreRepository, 
                 settings_repo:IBotSettingsRepository):
        
        self.logger:AppHerald = AppHerald()
        self.user_repo = user_repo
        self.store_repo = store_repo
        self.settings_repo = settings_repo

    async def weekly_top(self, notifier_func):
        """
        Еженедельное подведение итогов размера {{pencil_accu}}
        Каждая группа имеет свой топ и своих победителей
        """
        users: List[User] = await self.user_repo.get_users()
        indexed_users: Dict[int, List[User]] = {}

        for user in users:
            if (user.chat_id is not None):
                if (user.chat_id not in indexed_users):
                    indexed_users[user.chat_id] = []
                indexed_users[user.chat_id].append(user)

        for chat_id in indexed_users:
            try:
                settings:BotSettings = await self.settings_repo.get_settings(chat_id, "")
                if (not settings.events_enabled): continue
                
                rewards: List[int] = [15, 10, 5]
                sorted_users: List[User] = sorted(indexed_users[chat_id], 
                                                    key=lambda u: u.length,
                                                    reverse=True)
                for index, reward in enumerate(rewards):
                    if (len(sorted_users) > index):
                        await self.user_repo.update(sorted_users[index], {
                            "money" : reward + sorted_users[index].money
                        })
                
                await notifier_func(chat_id, "weekly_winners", {"sorted_users": sorted_users, "rewards": rewards})
            except Exception as e:
                self.logger.send_log("apscheduler", logging.WARNING, f"weekly_top - {e}")

    async def day_salary(self, notifier_func):
        """
        Ежедневная получка для работяг
        """
        await self.give_all(10, notifier_func, "day_salary")

    async def tech_work_compensation(self, notifier_func):
        """
        Премия в честь обновления (без таймера, ручной запуск)
        """
        await self.give_all(15, notifier_func, "tech_work_compensation")

    async def give_all(self, money:int, notifier_func, event:str):
        """
        Общий метод выдачи монеток всем игрокам
        """
        users: List[User] = await self.user_repo.get_users()
        indexed_users: Dict[int, List[User]] = {}

        for user in users:
            if (user.chat_id is not None):
                if (user.chat_id not in indexed_users):
                    indexed_users[user.chat_id] = []
                indexed_users[user.chat_id].append(user)

        for chat_id in indexed_users:
            try:
                settings:BotSettings = await self.settings_repo.get_settings(chat_id)
                if (not settings.events_enabled): continue

                await self.user_repo.update_users_money_by_chat(chat_id, money)
                
                await notifier_func(chat_id, event, {"money": money})
            except Exception as e:
                    self.logger.send_log("apscheduler", logging.WARNING, f"day_salary - {e}")
    
    async def day_draw(self, notifier_func):
        """
        Ежедневный розыгрыш мази увеличения {{pencil_accu}}
        Каждая группа получает своего победителя
        """
        users: List[User] = await self.user_repo.get_users(last_daily_draw_winner=False)
        indexed_users: Dict[int, List[User]] = {}

        for user in users:
            if (user.chat_id is not None):
                if (user.chat_id not in indexed_users):
                    indexed_users[user.chat_id] = []
                indexed_users[user.chat_id].append(user)

        for chat_id in indexed_users:
            try:
                settings:BotSettings = await self.settings_repo.get_settings(chat_id)
                if (not settings.events_enabled): continue

                if (not indexed_users[chat_id]): continue

                sorted_users: List[User] = sorted(indexed_users[chat_id], 
                                                    key=lambda u: u.length,
                                                    reverse=True)
                
                draw_winner_index:int = 0
                
                if (len(sorted_users) <= 3):
                    draw_winner_index = random.randrange(0, len(sorted_users))
                else:
                    draw_winner_index = random.randrange(2, len(sorted_users))
                
                last_winner:Optional[User] = await self.user_repo.get_user(chat_id=chat_id, last_daily_draw_winner=True)

                length_change:int = random.randrange(1, 3)
                
                await self.user_repo.update(sorted_users[draw_winner_index],
                                       last_daily_draw_winner = True,
                                       length = sorted_users[draw_winner_index].length + length_change)
                
                if (last_winner is not None):
                    await self.user_repo.update(last_winner, last_daily_draw_winner = False)
                
                await notifier_func(chat_id, "day_draw", {"winner": sorted_users[draw_winner_index], "length_change": length_change})
            except Exception as e:
                self.logger.send_log("apscheduler", logging.WARNING, f"day_draw - {e}")

    async def warehouse_update(self, notifier_func):
        """
        Ежедневное пополнение остатков магазина
        """
        try:
            if (await self.store_repo.update_warehouse()):
                await self.store_repo.deactivate_discounts()
                items_discounts:List[StoreItem] = await self.store_repo.create_random_discount(2)

                users: List[User] = await self.user_repo.get_users()
                indexed_users: Dict[int, List[User]] = {}

                for user in users:
                    if (user.chat_id is not None):
                        if (user.chat_id not in indexed_users):
                            indexed_users[user.chat_id] = []
                        indexed_users[user.chat_id].append(user)

                for chat_id in indexed_users:
                    settings = await self.settings_repo.get_settings(chat_id, "")
                    if (not settings.events_enabled): continue
                    
                    await notifier_func(chat_id, "warehouse_update", {"discounts": items_discounts})

        except Exception as e:
            self.logger.send_log("apscheduler", logging.WARNING, f"warehouse_update - {e}")

                
