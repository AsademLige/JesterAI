from features.battles.data.models.monster_stats_orm import MonsterStatsORM
from features.battles.battle_manager import BattleManager, BattlePhases
from features.user.data.models.user_stats_orm import UserStatsORM
from features.user.data.repository.gino_user_repository import GinoUserRepository
from features.user.data.models.user_model_orm import UserORM
from features.battles.battle_unit_entity import BattleUnit
from features.items.data.models.item_orm import ItemORM
from features.user.data.dtos.user_dto import User
from typing import Dict, List, Optional, Tuple
from core.data.data_base import DataBase
from datetime import datetime, timedelta
from core.utils.enums import BattleMode
from core.consts.config import Prefs
from aiogram.types import Message
from aiogram import Bot
import asyncio

class GameController():
    _instance = None
    db = DataBase()
    prefs = Prefs()
    user_repo:GinoUserRepository = GinoUserRepository()
    bot = Bot(token=prefs.bot_token)
    __battle_timer:timedelta = timedelta(seconds=60)
    __add_time_per_turn:timedelta = timedelta(seconds=15)
    __started_battles:Dict[int, BattleManager] = {}
    __battles_history:Dict[int, List[Message]] = {}
    __battles_tasks:Dict[int, List[asyncio.Task]] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True

    async def prepare_hunt(self, hunter:User) -> Tuple[str, BattleManager]:
        get_boss:bool = False

        heal_item:Optional[ItemORM] = await self.db.get_item_by_id(10)
        if (not await self.db.get_user_heal_items(hunter) and heal_item):
            await self.user_repo.user_item_transaction(hunter, heal_item)

        self.__started_battles[hunter.tg_id] = await BattleManager.hunt(hunter, boss=get_boss)
        return (self.__started_battles[hunter.tg_id].prepare_battle(), self.__started_battles[hunter.tg_id])
    
    async def prepare_gladiators(self, started_by:User):
        self.__started_battles[started_by.tg_id] = await BattleManager.gladiators()
        return self.__started_battles[started_by.tg_id].prepare_battle()
    
    def start_battle(self, started_by:User, init_message:Message):
         if (started_by.tg_id in self.__started_battles):
            self.__create_battle_timer(started_by.tg_id, self.__battle_timer)
            self.__battles_history[started_by.tg_id] = [init_message]
            battle:BattleManager = self.__started_battles[started_by.tg_id].start_battle(self.__battle_timer, 
                                                                                            self.__add_time_per_turn)
            return battle
    
    def get_battle(self, started_by:User) -> Optional[BattleManager]:
        if (started_by.tg_id in self.__started_battles):
            return self.__started_battles[started_by.tg_id]
        else: 
            return None
        
    async def get_battle_status(self, started_by:User) -> Optional[Tuple[str, BattlePhases, Optional[BattleUnit]]]:
        """str: текстовое описание текущего статуса боя
           BattlePhases: статус боя (для кнопок)
           BattleMember: активный в данный момент боец
        """
        if (started_by.tg_id in self.__started_battles):
            battle = self.__started_battles[started_by.tg_id]
            status:Optional[Tuple[str, BattlePhases, Optional[BattleUnit]]] = battle.get_status()
            battle_log:str = ""
            if (status):
                if (status[1] == BattlePhases.BATTLE_END): 
                    if (battle.mode == BattleMode.GLADIATORS and status[2]):
                        battle_log = await self.__gladiators_log(started_by, battle, status)

                    if (battle.mode == BattleMode.HUNT and status[2]):
                        battle_log = await self.__hunt_end_log(started_by, battle, status)

                    await self.delete_battle(started_by.tg_id, False)
                return (status[0] + battle_log, status[1], status[2])
                
            return ("Произошла ошибка", status[1], status[2])
    
    async def __gladiators_log(self, started_by:User, battle:BattleManager, 
                                  status:Optional[Tuple[str, BattlePhases, BattleUnit]]) -> str:
        if (not battle.mode == BattleMode.GLADIATORS): return

        for gladiator in battle.members:
            await self.db.update_monster_status(gladiator.entity.id, 
                {MonsterStatsORM.arena_fights.name : MonsterStatsORM.arena_fights + 1, 
                 MonsterStatsORM.arena_wins.name : MonsterStatsORM.arena_wins + (1 if (status[2] == gladiator) else 0)
                })

        ###TODO:Можно объединить в один метод update_user
        await self.user_repo.update(started_by, {
                UserORM.last_gladiators_bet.name: datetime.now(),
            })

        if (status[2].bet_money > 0):
            if (await self.user_repo.update(started_by, {UserORM.money.name : UserORM.money + status[2].bet_money,
                                                              UserStatsORM.gladiators_bet_win.name :  UserStatsORM.gladiators_bet_win + status[2].bet_money})):
                
                return "<i>\n\nСтавка сыграла! "\
                    f"{battle.dict.get_user_link(started_by.tg_name, started_by.tg_id)} "\
                    f"получает {battle.dict.money_wrapper(status[2].bet_money)}</i>\n"
        return ""
        
    async def __hunt_end_log(self, started_by:User, battle:BattleManager, 
                                  status:Optional[Tuple[str, BattlePhases, BattleUnit]]) -> str:
        if (status[2].is_player):
            monster:BattleUnit = battle.get_opponent()
            
            if ((await self.user_repo.user_item_transaction(started_by, status[2].inventory[0][0]) if (status[2].inventory[0]) else True) and
                await self.user_repo.update(started_by, {
                    UserORM.money.name: UserORM.money + status[2].inventory[1],
                    UserStatsORM.good_hunting_count.name : UserStatsORM.good_hunting_count + 1,
                    UserORM.last_hunt.name: datetime.now(),
                    UserORM.last_boss_hunt.name: datetime.now() + timedelta(hours=12) if monster.is_boss else UserORM.last_boss_hunt,
                })):
                from core.consts.dictionary import Dictionary
                log:str = f"\n\n📦 {Dictionary().hunt_loot(status[2].inventory)}\n" if (status[2].inventory) else ""
                return log + ("\n<i>Вы победили бедствие, и оно отступило на время... Но очень скоро вернется, длинночлен! "\
                              "(Босс не нападет на вас в течение 12 часов)</i>" if monster.is_boss else "")
            else: return f"Ой, ошибочка вышла..."
        elif status[2].is_mob or status[2].is_boss:
            await self.user_repo.update(started_by, {
                UserORM.last_hunt.name: datetime.now(),
            })
        return ""
        
        
    async def escape_battle(self, member:User) -> Optional[str]:
        if (member.tg_id in self.__started_battles):
            status:str = self.__started_battles[member.tg_id].escape()
            monster:BattleUnit = self.__started_battles[member.tg_id].get_opponent()
            await self.db.update_user(member, {
                UserORM.last_hunt.name: datetime.now(),
            })
            await self.delete_battle(member.tg_id, False)
            return status
        else: return None

    def __create_battle_timer(self, battle_key, delay:timedelta):
        """Создает таймер на удаление битвы"""
        if battle_key in self.__battles_tasks:
            old_tasks = self.__battles_tasks[battle_key]
            for old_task in old_tasks:
                if not old_task.done():
                    old_task.cancel()

        new_task = asyncio.create_task(
            self.__create_task_delete_battle(battle_key, delay)
        )
        
        self.__battles_tasks[battle_key] = [new_task]
    
    async def __create_task_delete_battle(self, battle_key, delay:timedelta, additional:timedelta = None):
        """Управляет состоянием задачи на удаление битвы, продлевая таймер при необходимости"""
        await asyncio.sleep(additional.total_seconds() if (additional) else delay.total_seconds())

        if battle_key not in self.__started_battles:
            return

        if (battle_key in self.__started_battles):
            if (self.__started_battles[battle_key].battle_timer > delay):
                await self.__create_task_delete_battle(battle_key, self.__started_battles[battle_key].battle_timer, 
                                        self.__started_battles[battle_key].battle_timer - delay)
                return

        await self.delete_battle(battle_key)

    async def delete_battle(self, battle_key:int, clear_history:bool = True):
        """Удаляет экземпляр битвы через указанный интервал"""
        if battle_key in self.__started_battles:
            if (battle_key in self.__battles_tasks):
                for task in self.__battles_tasks[battle_key]:
                    task.cancel()
                    try:
                        await task
                    except:
                        pass

            if (battle_key in self.__battles_history):
                if (self.__battles_history[battle_key] and self.__started_battles[battle_key].mode == BattleMode.HUNT 
                    and not self.__started_battles[battle_key].phase == BattlePhases.BATTLE_END):
                    user:User = await self.user_repo.get_user(battle_key, 
                                                            self.__battles_history[battle_key][0].chat.id)
                    await self.user_repo.update(user, {
                        UserORM.last_hunt.name: datetime.now(),
                    })
                    await self.bot.send_message(self.__battles_history[battle_key][0].chat.id, 
                                                "💀 Время вышло, охотник пропал без вести!")

            if (clear_history and battle_key in self.__battles_history):
                for message in self.__battles_history[battle_key]:
                    try:
                        await message.delete()
                    except  Exception as e:
                        print(f"delete message error: {e}")

            del self.__started_battles[battle_key]