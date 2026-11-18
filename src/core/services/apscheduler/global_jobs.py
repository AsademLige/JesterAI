from features.game_engine.data.repository.bot_settings_repository import IBotSettingsRepository
from features.store.data.repository.store_repository import IStoreRepository
from features.user.data.repository.user_repository import IUserRepository
from features.game_engine.data.models.bot_settings_dto import BotSettings
from features.battles.data.repository.gino_battle_repository import GinoBattleRepository
from features.battles.data.repository.gino_monsters_repository import GinoMonstersRepository
from features.gamba_house.data.repository.gino_winners_log_repository import GinoWinnersLogRepository
from features.newspaper.data.repository.gino_newspaper_repository import GinoNewspaperRepository
from features.items.data.models.store_item_dto import StoreItem
from core.services.newspaper.humor_provider import HumorProvider
from features.user.data.dtos.user_dto import User
from core.consts.dictionary import Dictionary
from core.utils.app_herald import AppHerald
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
import random
import time

NEWSPAPER_FISH_REWARD = 50
NEWSPAPER_MONSTER_REWARD = 50

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
        self.dict = Dictionary()

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

    async def weekly_newspaper(self, notifier_func):
        """
        Еженедельный выпуск газеты «Чумные вести».
        Победители выбираются среди всех игроков (без привязки к чату),
        готовый выпуск сохраняется в БД и рассылается в чаты с events_enabled.
        """
        winners_log_repo = GinoWinnersLogRepository()
        newspaper_repo = GinoNewspaperRepository()
        battle_repo = GinoBattleRepository()
        humor = HumorProvider()

        try:
            cutoff_ts = int(time.time()) - 7 * 24 * 3600
            since_date = datetime.now() - timedelta(days=7)

            # Самая тяжёлая выловленная рыба за неделю + суммарный улов (глобально)
            fish_stats = await battle_repo.get_week_fishing_stats(cutoff_ts)
            fish = fish_stats["best"]
            total_fish_weight: float = fish_stats["total_weight"]
            fish_winner: Optional[User] = None
            fish_name: Optional[str] = None
            fish_weight: Optional[float] = None
            if fish:
                fish_winner = await self.user_repo.get_user(tg_id=fish["tg_id"])
                fish_name = fish.get("fish_name")
                fish_weight = fish.get("weight_kg")
                if fish_winner is not None:
                    await self.user_repo.update(fish_winner, money=fish_winner.money + NEWSPAPER_FISH_REWARD)

            # Охота: сколько монстров убито всеми игроками + лучший охотник (глобально)
            monster_stats = await battle_repo.get_week_monster_kills(cutoff_ts)
            total_monster_kills: int = monster_stats["total_kills"]
            monster_killer: Optional[User] = None
            if monster_stats["top"]:
                monster_killer = await self.user_repo.get_user(tg_id=monster_stats["top"]["tg_id"])
                if monster_killer is not None:
                    await self.user_repo.update(monster_killer, money=monster_killer.money + NEWSPAPER_MONSTER_REWARD)

            monster_name: Optional[str] = None
            monster_names = monster_stats["monster_names"]
            if monster_names:
                monster_name = random.choice(monster_names)
            else:
                rnd_monsters = await GinoMonstersRepository().get_random_monsters_by_tag(1, "mob")
                if rnd_monsters:
                    monster_name = rnd_monsters[0].name

            # Игрок, потративший больше всего монет в гамба-хаусе + общие траты (глобально)
            spender: Optional[User] = None
            spent: int = 0
            spender_row = await winners_log_repo.get_top_spender(since_date)
            if spender_row:
                spender_id, spent = spender_row
                spender = await self.user_repo.get_user(id=spender_id)
            total_spent: int = await winners_log_repo.get_total_spent(since_date)

            humor_blocks = await humor.get_blocks(2)

            number = await newspaper_repo.get_next_issue_number()
            date_str = datetime.now().strftime("%d.%m.%Y")
            text = self.dict.newspaper(number, date_str,
                                       fish_winner=fish_winner, fish_name=fish_name,
                                       fish_weight=fish_weight, total_fish_weight=total_fish_weight,
                                       fish_reward=NEWSPAPER_FISH_REWARD if fish_winner else 0,
                                       monster_killer=monster_killer, total_monster_kills=total_monster_kills,
                                       monster_name=monster_name,
                                       monster_reward=NEWSPAPER_MONSTER_REWARD if monster_killer else 0,
                                       spender=spender, spent=spent, total_spent=total_spent,
                                       humor_blocks=humor_blocks)

            await newspaper_repo.create_issue(number, text)

            chat_settings: List[BotSettings] = await self.settings_repo.get_all()
            for settings in chat_settings:
                if (not settings.events_enabled): continue
                await notifier_func(settings.chat_id, "newspaper", {"text": text, "number": number})
        except Exception as e:
            self.logger.send_log("apscheduler", logging.WARNING, f"weekly_newspaper - {e}")

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
        chat_settings:List[BotSettings] = await self.settings_repo.get_all()

        for settings in chat_settings:
            try:
                if (not settings.events_enabled): continue
                await self.user_repo.update_users_money_by_chat(settings.chat_id, money)
            
                await notifier_func(settings.chat_id, event, {"money": money})
            except Exception as e:
                    self.logger.send_log("apscheduler", logging.WARNING, f"day_salary - {e}")
    
    async def day_draw(self, notifier_func):
        """
        Ежедневный розыгрыш мази увеличения {{pencil_accu}}
        Каждая группа получает своего победителя
        """
        users: List[User] = await self.user_repo.get_users(last_daily_draw_winner=False)
        chat_settings:List[BotSettings] = await self.settings_repo.get_all()
                       
        for settings in chat_settings:
            try:
                if (not settings.events_enabled): continue

                sorted_users: List[User] = sorted(users, 
                                                key=lambda u: u.length,
                                                reverse=True)
                
                draw_winner_index:int = 0
                
                if (len(sorted_users) <= 3):
                    draw_winner_index = random.randrange(0, len(sorted_users))
                else:
                    draw_winner_index = random.randrange(2, len(sorted_users))
                
                last_winner:Optional[User] = await self.user_repo.get_user(last_daily_draw_winner=True)

                length_change:int = random.randrange(1, 3)
                
                await self.user_repo.update(sorted_users[draw_winner_index],
                                       last_daily_draw_winner = True,
                                       length = sorted_users[draw_winner_index].length + length_change)
                
                if (last_winner is not None):
                    await self.user_repo.update(last_winner, last_daily_draw_winner = False)
                
                await notifier_func(settings.chat_id, "day_draw", {"winner": sorted_users[draw_winner_index], "length_change": length_change})
            except Exception as e:
                self.logger.send_log("apscheduler", logging.WARNING, f"day_draw - {e}")

    async def warehouse_update(self, notifier_func):
        """
        Ежедневное пополнение остатков магазина
        """
        try:
            out_of_stock = await self.store_repo.update_warehouse(out_of_stock_count=2)
            if (out_of_stock):
                await self.store_repo.deactivate_discounts()
                items_discounts:List[StoreItem] = await self.store_repo.create_random_discount(2)

                chat_settings:List[BotSettings] = await self.settings_repo.get_all()
               
                for settings in chat_settings:
                    if (not settings.events_enabled): continue
                    
                    await notifier_func(settings.chat_id, "warehouse_update", {"discounts": items_discounts, "out_of_stock" : out_of_stock})

        except Exception as e:
            self.logger.send_log("apscheduler", logging.WARNING, f"warehouse_update - {e}")

                
