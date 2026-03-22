from src.models.battle_member_model import AttackStatus, BattleMember, MemberStand, MemberStrategy
from src.domain.utils.enums import BattleMode, BattlePhases, MemberStatus
from src.domain.utils.text_processing import TextProcessing as tp
from typing import Any, Dict, List, Optional, Tuple, Union
from src.services.data_base.db import DataBase
from src.models.monster_model import Monster
from src.data.dictionary import Dictionary
from datetime import datetime, timedelta
from src.models.user_model import User
from src.data.config import Prefs
from random import Random
from aiogram import Bot
from enum import Enum
import random

class BattleController():
    db = DataBase()
    dict = Dictionary()
    prefs = Prefs()
    members:List[BattleMember]
    __mode:BattleMode
    __phase:BattlePhases

    __active_member:Optional[BattleMember] = None
    __round:int = 0
    
    __battle_timer:timedelta
    __add_time_per_turn:timedelta
    battle_started:datetime
    motions_per_turn:int = 2

    @property
    def active_member(self) -> BattleMember:
        return self.__active_member
    
    @property
    def round(self) -> int:
        return self.__round
    
    @property
    def phase(self) -> int:
        return self.__phase
    
    @property
    def battle_timer(self) -> int:
        return self.__battle_timer
    
    @property
    def mode(self) -> int:
        return self.__mode

    def __init__(self, members:List[Union[Monster, User]], mode:BattleMode):
        self.members = [BattleMember(entity) for entity in members]
        self.__mode = mode
        self.__phase = BattlePhases.PREPARE
        pass

    @classmethod
    async def hunt(cls, hunter:User, monster_count:int = 1):
        members:List[Union[Monster, User]] = [hunter]
        monsters:List[Monster] = await cls.db.get_random_monsters(monster_count)
        members.extend(monsters)
        return cls(
            members = members,
            mode = BattleMode.HUNT
        )
    
    @classmethod
    async def gladiators(cls, monster_count:int = 2):
        monsters:List[Monster] = await cls.db.get_random_monsters(monster_count)
        return cls(
            members = monsters,
            mode = BattleMode.GLADIATORS
        )
    
    @classmethod
    def duel(cls, members:List[User]):
        return cls(
            members = members,
            mode = BattleMode.DUEL
        )
    
    def prepare_battle(self):
        if (self.__mode == BattleMode.HUNT):
            #TODO: Можно будет расширить возможности боя на несколько монстров
            self.__active_member = self.members[0]
            return self.dict.monster_meeting(self.members[1].entity)
        if (self.__mode == BattleMode.GLADIATORS):
            self.__active_member = self.members[0]
            return self.dict.gladiators_introduce(self.members, self.__get_ui_data())
        
    def start_battle(self, timer:timedelta = timedelta(seconds=30), 
                     add_time_per_turn:timedelta = timedelta(seconds=15)):
        self.__phase = BattlePhases.MOTION
        self.__round += 1
        self.__battle_timer = timer
        self.__add_time_per_turn = add_time_per_turn
        self.battle_started = datetime.now()
        
    def get_status(self) -> Optional[Tuple[str, BattlePhases, BattleMember]]:
        """str: текстовое описание текущего статуса боя
           BattlePhases: статус боя (для кнопок)
           BattleMember: активный в данный момент боец
        """

        if (self.mode == BattleMode.GLADIATORS and self.__phase == BattlePhases.MOTION):
            return self.__end_turn()

        if (self.__active_member.status == MemberStatus.EXHAUSTED):
            return self.__start_action()
        else:
            self.__phase = BattlePhases.MOTION


        ui:str = tp.text_replacement(self.dict.combat_interface + ("💥 {{turn}}, выбери, куда ударить:" 
                                    if self.__active_member.stand == MemberStand.ATTACK else "🛡 {{turn}}, выбери, что защитить:"),
                                   {
                                       **self.__get_ui_data(),
                                       "timer": f"{round((self.battle_started + self.__battle_timer - datetime.now()).total_seconds())} сек",
                                       "fight_name": f"🏹 <b>ОХОТА!</b>🏹 <code>Раунд: {self.__round}</code>" 
                                            if self.__mode == BattleMode.HUNT else 
                                        f"⚔️ <b>ДРЫНОСТОЯНИЕ!</b>⚔️ <code>Раунд: {self.__round}</code>",
                                   })
        
        if (self.mode == BattleMode.GLADIATORS and self.__phase == BattlePhases.REST):
            self.__phase = BattlePhases.MOTION

        return (ui, self.__phase, self.__active_member)
    
    def __get_ui_data(self) -> Dict[str, str]:
        members_ui:Dict[str, str] = {}

        for i in range(len(self.members)):

            bet:str = f" (<b>{self.members[i].bet_money}💰</b>)" if (self.members[i].bet_money > 0) else ""

            members_ui[f"player{i+1}"] = self.members[i].full_battle_name + bet
            members_ui[f"player{i+1}_icon"] = self.members[i].utf8_icon
            members_ui[f"health{i+1}"] = self.health_bar(self.members[i].hp, self.members[i].max_hp)
            
            if (self.members[i] == self.__active_member):
                members_ui["turn"] = f"<b>({self.__active_member.motions_left}/2)</b> {self.members[i].link}"
            
        return members_ui
        
    def escape(self) -> Optional[str]:
        """Побег из боя участника, которому принадлежит ход"""
        if (self.__active_member):
            self.__phase = BattlePhases.BATTLE_END
            return self.dict.battle_escape(self.__active_member.entity)

    def __start_action(self) -> Tuple[str, BattlePhases, BattleMember]:
        """Основной цикл боя, в котором сменяются фазы, и передается очередность хода"""
        self.__phase = BattlePhases.REST
        self.__active_member.rest()
        self.__round += 1
        
        next_index:int = self.members.index(self.__active_member) + 1
        if (self.__mode == BattleMode.HUNT or next_index > len(self.members) - 1):
            result = self.__end_turn()
            return result
        elif (self.__mode == BattleMode.DUEL):
            self.__active_member = 0 if (next_index > len(self.members) - 1) else self.members[next_index]
        
        return (self.get_status(), self.__phase, self.__active_member)
        
    def __end_turn(self) -> Tuple[str, BattlePhases, Optional[BattleMember]]:
        self.__battle_timer += self.__add_time_per_turn
        self.__simulate_mobs()
        
        opponent:BattleMember = self.__get_opponent()    

        print(f"cdlog {self.active_member.attack_target} : {opponent.attack_target}")

        turn_result:str = ""
        status:Optional[Tuple[AttackStatus, int, bool]] = self.__active_member.attacked(opponent)
        opponent_status:Optional[Tuple[AttackStatus, int, bool]] = opponent.attacked(self.__active_member)

        print(f"cdlog {opponent_status[1]} : {status[1]}")

        if (status[0] == AttackStatus.KILLED and opponent_status[0] == AttackStatus.KILLED):
            self.__phase = BattlePhases.BATTLE_END
            return ("Оба сдохли", self.__phase, None)
        elif (opponent_status and opponent_status[0] == AttackStatus.KILLED):
            self.__phase = BattlePhases.BATTLE_END
            turn_result = self.dict.battle_end(opponent, self.__mode, (opponent_status[1], opponent_status[2]))
            return (turn_result, self.__phase, self.__active_member)
        elif (status[0] == AttackStatus.KILLED):
            self.__phase = BattlePhases.BATTLE_END
            turn_result = self.dict.battle_end(self.__active_member, self.__mode, (status[1], status[2]))
            return (turn_result, self.__phase, opponent)
        if (status[0] == AttackStatus.DEFENDED and opponent_status[0] == AttackStatus.DEFENDED):
            turn_result = self.dict.battle_turn_draft_protected(self.__active_member, 
                                                                opponent)
        elif (status[0] == AttackStatus.DAMAGED and opponent_status[0] == AttackStatus.DEFENDED):
            turn_result = self.dict.battle_turn_first_attacked(self.__active_member, opponent, 
                                                               (status[1], status[2]))

        elif (status[0] == AttackStatus.DEFENDED and opponent_status[0] == AttackStatus.DAMAGED):
            turn_result = self.dict.battle_turn_sec_attacked(self.__active_member, 
                                                             opponent, 
                                                             (opponent_status[1], opponent_status[2]))
            
        elif (status[0] == AttackStatus.DAMAGED and opponent_status[0] == AttackStatus.DAMAGED):
            turn_result = self.dict.battle_turn_both_attacked(self.__active_member, 
                                                              opponent, 
                                                              (opponent_status[1], opponent_status[2]), 
                                                              (status[1], status[2]))

        if (self.__mode == BattleMode.HUNT and not status[0] == AttackStatus.KILLED):
            turn_result += f"\n\n⏳ Таймер: {round((self.battle_started + self.__battle_timer - datetime.now()).total_seconds())} сек"
            if (not self.active_member.strategy == MemberStrategy.DEFENSE):
                turn_result += "\n<i>❗️ Побег и лечение невозможны, сначала нужно уйти в защиту!</i>"

        if (self.__mode == BattleMode.GLADIATORS and not self.__phase == BattlePhases.BATTLE_END):
            turn_result += tp.text_replacement(f"\n\n{self.dict.gladiators_interface}", {**self.__get_ui_data()})

        return (turn_result, self.__phase, self.__active_member)
    
    def __simulate_mobs(self):
        for member in self.members:
            if (type(member.entity) is Monster):
                member.simulate_actions()
    
    def __get_opponent(self) -> BattleMember:
        other_members:List = list(self.members)
        other_members.pop(self.members.index(self.__active_member))
        return random.choice(other_members)
    
    def get_bet_gladiator(self) -> Optional[BattleMember]:
        return next((gld for gld in self.members if gld.bet_money > 0), None)

    @staticmethod
    def health_bar(current, maximum, length=10, heal=0):
        """Создает полоску здоровья"""
        """Создает полоску здоровья с отображением вылеченного здоровья"""
        filled_bars = int((current / maximum) * length)
        filled_bars = min(filled_bars, length)
        
        healed_bars = int((heal / maximum) * length) if heal > 0 else 0
        healed_bars = min(healed_bars, length - filled_bars)
        
        # Создаем полоску: ▰ - текущее здоровье, ░ - вылеченное, □ - потерянное
        return ("▰" * filled_bars + "+" * healed_bars + "□" * (length - filled_bars - healed_bars)) + f" {current+heal}/{maximum}"
