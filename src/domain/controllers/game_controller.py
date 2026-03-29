from src.domain.controllers.battle_controller import BattleController, BattlePhases
from src.models.battle_member_model import BattleMember
from src.models.user_stats_model import UserStats
from src.models.monster_stats import MonsterStats
from typing import Dict, List, Optional, Tuple
from src.services.data_base.db import DataBase
from src.domain.utils.enums import BattleMode
from datetime import datetime, timedelta
from src.domain.utils.utils import Utils
from src.models.user_model import User
from src.models.item_model import Item
from aiogram.types import Message
import asyncio
import math

class GameController():
    _instance = None
    db = DataBase()
    __battle_timer:timedelta = timedelta(seconds=30)
    __add_time_per_turn:timedelta = timedelta(seconds=15)
    __started_battles:Dict[int, BattleController] = {}
    __battles_history:Dict[int, List[Message]] = {}
    __battles_tasks:Dict[int, List[asyncio.Task]] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True

    async def prepare_hunt(self, hunter:User):
        get_boss:bool = False
        
        delta:timedelta = Utils.get_time_delta(hunter.last_boss_hunt, 12)
        if (await self.db.get_place_in_top_by_member(hunter.tg_id, hunter.chat_id) <= 3 and
             math.floor(delta.total_seconds() / 3600) > 0):
            get_boss = True

        heal_item:Optional[Item] = await self.db.get_item_by_id(10)
        if (not await self.db.get_user_heal_items(hunter) and heal_item):
            await self.db.user_item_transaction(hunter, heal_item)

        self.__started_battles[hunter.tg_id] = await BattleController.hunt(hunter, boss=get_boss)
        return self.__started_battles[hunter.tg_id].prepare_battle()
    
    async def prepare_gladiators(self, started_by:User):
        self.__started_battles[started_by.tg_id] = await BattleController.gladiators()
        return self.__started_battles[started_by.tg_id].prepare_battle()
    
    def start_battle(self, started_by:User, init_message:Message):
         if (started_by.tg_id in self.__started_battles):
            self.__create_battle_timer(started_by.tg_id, self.__battle_timer)
            self.__battles_history[started_by.tg_id] = [init_message]
            battle:BattleController = self.__started_battles[started_by.tg_id].start_battle(self.__battle_timer, 
                                                                                            self.__add_time_per_turn)
            return battle
    
    def get_battle(self, started_by:User) -> Optional[BattleController]:
        if (started_by.tg_id in self.__started_battles):
            return self.__started_battles[started_by.tg_id]
        else: 
            return None
        
    async def get_battle_status(self, started_by:User) -> Optional[Tuple[str, BattlePhases, Optional[BattleMember]]]:
        """str: текстовое описание текущего статуса боя
           BattlePhases: статус боя (для кнопок)
           BattleMember: активный в данный момент боец
        """
        if (started_by.tg_id in self.__started_battles):
            battle = self.__started_battles[started_by.tg_id]
            status:Optional[Tuple[str, BattlePhases, Optional[BattleMember]]] = battle.get_status()
            battle_log:str = ""
            if (status):
                if (status[1] == BattlePhases.BATTLE_END): 
                    if (battle.mode == BattleMode.GLADIATORS and status[2]):
                        battle_log = await self.__gladiators_log(started_by, battle, status)

                    if (battle.mode == BattleMode.HUNT and status[2]):
                        battle_log = await self.__hunt_end_log(started_by, battle, status)
                    else:
                        monster:BattleMember = battle.get_opponent()
                        await self.db.update_user(started_by, {
                            User.money.name: User.money + status[2].inventory[1],
                            User.last_hunt.name: datetime.now(),
                        })

                    await self.__delete_battle(started_by.tg_id, False)
                return (status[0] + battle_log, status[1], status[2])
                
        return ("Произошла ошибка", status[1], status[2])
    
    async def __gladiators_log(self, started_by:User, battle:BattleController, 
                                  status:Optional[Tuple[str, BattlePhases, BattleMember]]) -> str:
        if (not battle.mode == BattleMode.GLADIATORS): return

        for gladiator in battle.members:
            await self.db.update_monster_status(gladiator.entity.id, 
                {MonsterStats.arena_fights.name : MonsterStats.arena_fights + 1, 
                 MonsterStats.arena_wins.name : MonsterStats.arena_wins + (1 if (status[2] == gladiator) else 0)
                })

        if (status[2].bet_money):
            if (await self.db.update_user(started_by, {"money" : User.money + status[2].bet_money})):
                await self.db.update_user_status(started_by.id, 
                    {UserStats.gladiators_bet_win.name :  UserStats.gladiators_bet_win + status[2].bet_money})
                return "<i>\n\nСтавка сыграла! "\
                    f"{battle.dict.get_user_link(started_by.tg_name, started_by.tg_id)} "\
                    f"получает {battle.dict.money_wrapper(status[2].bet_money)}</i>\n"
        return ""
        
    async def __hunt_end_log(self, started_by:User, battle:BattleController, 
                                  status:Optional[Tuple[str, BattlePhases, BattleMember]]) -> str:
        if (status[2].is_player):
            monster:BattleMember = battle.get_opponent()
            await self.db.update_user_status(status[2].entity.id, 
                {UserStats.good_hunting_count.name : UserStats.good_hunting_count + 1})
            if ((await self.db.user_item_transaction(started_by, status[2].inventory[0][0]) if (status[2].inventory[0]) else True) and
                await self.db.update_user(started_by, {
                    User.money.name: User.money + status[2].inventory[1],
                    User.last_hunt.name: datetime.now(),
                    User.last_boss_hunt.name: datetime.now() - timedelta(hours=12) if monster.is_boss else User.last_boss_hunt,
                })):
                from src.data.dictionary import Dictionary
                log:str = f"\n\n📦 {Dictionary().hunt_loot(status[2].inventory)}\n" if (status[2].inventory) else ""
                return log + ("\n<i>Вы победили бедствие, и оно отступило на время... Но очень скоро вернется, длинночлен! "\
                              "(Босс не нападет на вас в течение 12 часов)</i>" if monster.is_boss else "")
            else: return f"Ой, ошибочка вышла..."
        return ""
        
        
    async def escape_battle(self, member:User) -> Optional[str]:
        if (member.tg_id in self.__started_battles):
            status:str = self.__started_battles[member.tg_id].escape()
            monster:BattleMember = self.__started_battles[member.tg_id].get_opponent()
            await self.db.update_user(member, {
                User.last_hunt.name: datetime.now(),
            })
            await self.__delete_battle(member.tg_id, False)
            return status
        else: return None

    def __create_battle_timer(self, battle_key, delay:timedelta):
        """Создает таймер на удаление битвы"""
        task = asyncio.create_task(
            self.__create_task_delete_battle(battle_key, delay)
        )
        if (battle_key in self.__battles_tasks):
            self.__battles_tasks[battle_key].append(task)
        else:
            self.__battles_tasks[battle_key] = [task]

        return task
    
    async def __create_task_delete_battle(self, battle_key, delay:timedelta, additional:timedelta = None):
        """Управляет состоянием задачи на удаление битвы, продлевая таймер при необходимости"""
        await asyncio.sleep(additional.total_seconds() if (additional) else delay.total_seconds())

        if (battle_key in self.__started_battles):
            if (self.__started_battles[battle_key].battle_timer > delay):
                await self.__create_task_delete_battle(battle_key, self.__started_battles[battle_key].battle_timer, 
                                        self.__started_battles[battle_key].battle_timer - delay)
                return

        await self.__delete_battle(battle_key)

    async def __delete_battle(self, battle_key, clear_history:bool = True):
        """Удаляет экземпляр битвы через указанный интервал"""
        if battle_key in self.__started_battles:
            if (battle_key in self.__battles_tasks):
                for task in self.__battles_tasks[battle_key]:
                    task.cancel()
                    try:
                        await task
                    except:
                        pass

            if (clear_history):
                for message in self.__battles_history[battle_key]:
                    try:
                        await message.delete()
                    except  Exception as e:
                        print(f"delete message error: {e}")

            del self.__started_battles[battle_key]