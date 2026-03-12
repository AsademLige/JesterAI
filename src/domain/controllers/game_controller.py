from src.domain.controllers.battle_controller import BattleController, BattlePhases
from src.models.battle_member_model import BodyParts
from typing import Dict, List, Optional, Tuple
from src.services.data_base.db import DataBase
from src.models.monster_model import Monster
from src.models.user_model import User
from datetime import time, timedelta
from aiogram.types import Message
import asyncio

class GameController():
    _instance = None
    db = DataBase()
    __battle_timer:timedelta = timedelta(seconds=120)
    __started_battles:Dict[int, BattleController] = {}
    __battles_history:Dict[int, List[Message]] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True

    async def prepare_hunt(self, hunter:User):
        monster:Monster = await self.db.get_random_monster()
        self.__started_battles[hunter.tg_id] = BattleController.hunt([hunter, monster])
        return self.__started_battles[hunter.tg_id].prepare_battle()
    
    def start_battle(self, started_by:User, init_message:Message):
         if (started_by.tg_id in self.__started_battles):
            self.__create_battle_timer(started_by.tg_id, self.__battle_timer)
            self.__battles_history[started_by.tg_id] = [init_message]
            battle:BattleController = self.__started_battles[started_by.tg_id].start_battle(self.__battle_timer)
            return battle
    
    def get_battle(self, started_by:User) -> Optional[BattleController]:
        if (started_by.tg_id in self.__started_battles):
            return self.__started_battles[started_by.tg_id]
        else: 
            return None
        
    def get_battle_status(self, started_by:User) -> Optional[Tuple[str, BattlePhases]]:
        if (started_by.tg_id in self.__started_battles):
            return (self.__started_battles[started_by.tg_id].get_turn_ui(), \
                   self.__started_battles[started_by.tg_id].phase)
        else: return None

    def battle_next_phase(self, started_by:User, part:BodyParts) -> Optional[Tuple[str, BattlePhases]]:
        if (started_by.tg_id in self.__started_battles):
            status:Optional[Tuple[str, BattlePhases, User]] = self.__started_battles[started_by.tg_id].turn_loop(part)
            battle_log:str = ""
            if (status):
                if (status[1] == BattlePhases.BATTLE_END): 
                    del self.__started_battles[started_by.tg_id]
                    if (status[2]):
                        ##Подсчитываем награды
                        battle_log = "<i>Мародерим!</i>\n"
                return (status[0] + battle_log, status[1])
                
        return None
        
    def escape_battle(self, member:User) -> Optional[str]:
        if (member.tg_id in self.__started_battles):
            status:str = self.__started_battles[member.tg_id].escape()
            del self.__started_battles[member.tg_id]
            return status
        else: return None


    def __create_battle_timer(self, battle_key, delay:timedelta):
        """Создает таймер на удаление битвы"""
        task = asyncio.create_task(
            self.__delete_battle(battle_key, delay)
        )
        return task
    
    async def __delete_battle(self, battle_key, delay:timedelta):
        """Удаляет экземпляр битвы через указанный интервал"""
        await asyncio.sleep(delay.total_seconds())
        if battle_key in self.__started_battles:
            del self.__started_battles[battle_key]
            for message in self.__battles_history[battle_key]:
                try:
                    await message.delete()
                except  Exception as e:
                    print(f"delete message error: {e}")