from __future__ import annotations
from src.domain.utils.enums import AttackStatus, BodyParts, MemberStatus
from typing import List, Optional, Tuple, Union
from src.models.monster_model import Monster
from src.models.user_model import User
from enum import Enum
import random

class MemberStrategy(Enum):
    AGGRESSIVE = "aggressive_strategy"
    CONTR_STRIKE = "contr_strike_strategy"
    DEFENSE = "defense_strategy"

class MemberStand(Enum):
    ATTACK = 0
    DEFENSE = 1

class BattleMember():
    entity:Union[Monster, User]
    utf8_icon:str

    __attack_target:List[BodyParts]
    __protected_parts:List[BodyParts]

    __status:MemberStatus = MemberStatus.FULL_OF_ENERGY

    __hp:int
    __max_hp:int
    __motions_left:int = 2
    __crit_chance:int
    __bet_money:int

    __strategy:MemberStrategy = MemberStrategy.CONTR_STRIKE
    __stand:MemberStand = MemberStand.ATTACK

    __last_turn_result:Optional[AttackStatus]

    @property
    def hp(self) -> int:
        return self.__hp 
    
    @property
    def max_hp(self) -> int:
        return self.__max_hp
    
    @property
    def motions_left(self) -> int:
        return self.__motions_left 
    
    @property
    def status(self) -> MemberStatus:
        return self.__status 
    
    @property
    def is_dead(self) -> bool:
        return self.__status == MemberStatus.DEAD
    
    @property
    def is_alive(self) -> bool:
        return self.__status == MemberStatus.FULL_OF_ENERGY
    
    @property
    def protected_parts(self) -> List[BodyParts]:
        return self.__protected_parts
    
    @property
    def attack_target(self) -> List[BodyParts]:
        return self.__attack_target
    
    @property
    def strategy(self) -> MemberStrategy:
        return self.__strategy
    
    @property
    def stand(self) -> MemberStatus:
        return self.__stand
    
    @property
    def bet_money(self) -> MemberStatus:
        return self.__bet_money
    
    @property
    def last_turn_result(self) -> AttackStatus:
        return self.__last_turn_result

    def __init__(self, entity:Union[Monster, User]):
        self.entity = entity
        self.__bet_money = 0
        self.__attack_target = []
        self.__protected_parts = []
        self.__last_turn_result = None
        self.__crit_chance = entity.crit_chance if type(entity) is Monster else 15
        self.__max_hp = entity.health if type(entity) is Monster else 30
        self.__hp = self.__max_hp
        self.utf8_icon = entity.utf8_icon if entity.utf8_icon else random.choice(["🥷","🧝‍♂️","🧙🏿‍♂️","🧙🏼"])
        pass

    def attacked(self, opponent:BattleMember) -> Optional[Tuple[AttackStatus, int, bool]]:
        hits:List[Tuple[BodyParts, int, bool]] = opponent.get_hits()
        attack_status:AttackStatus = AttackStatus.DEFENDED
        total_damage:int = 0
        is_crit:bool = False

        for hit in hits:
            if (not hit[0] in self.protected_parts):
                self.__hp -= hit[1]
                total_damage += hit[1]
                if (hit[2]):
                    is_crit = True
                if (self.__hp <= 0): 
                    self.__status = MemberStatus.DEAD
                    attack_status = AttackStatus.KILLED
                else:
                    attack_status = AttackStatus.DAMAGED
            else:
                if (not attack_status):
                    attack_status = AttackStatus.DEFENDED
        self.__protected_parts.clear()

        self.__last_turn_result = attack_status

        return (attack_status, total_damage, is_crit)

    def take_aim(self, part:Optional[BodyParts]) -> MemberStatus:
        if (self.__stand == MemberStand.ATTACK and self.__motions_left > 0):
            self.__attack_target.append(part)
            self.__motions_left -= 1
            if (self.__motions_left == 0):
                self.__status = MemberStatus.EXHAUSTED
            else:
                if (not self.__strategy == MemberStrategy.AGGRESSIVE):
                    self.__stand = MemberStand.DEFENSE
        return self.__status

    def protect(self, part:Optional[BodyParts]) -> MemberStatus:
        if (self.__stand == MemberStand.DEFENSE and self.__motions_left > 0):
            self.__protected_parts.append(part)
            self.__motions_left -= 1
            if (self.__motions_left == 0):
                self.__status = MemberStatus.EXHAUSTED
            else:
                if (not self.__strategy == MemberStrategy.DEFENSE):
                    self.__stand = MemberStand.ATTACK
        return self.__status

    def rest(self, motions:int = 2) -> MemberStatus:
        self.__status = MemberStatus.FULL_OF_ENERGY
        self.choice_strategy(self.__strategy)
        self.__motions_left = motions
        return self.__status
    
    def heal(self, hp:int = 0):
        self.__hp += hp
    
    def choice_strategy(self, strategy:MemberStrategy):
        self.__strategy = strategy
        if (strategy == MemberStrategy.CONTR_STRIKE or
            strategy == MemberStrategy.AGGRESSIVE):
            self.__stand = MemberStand.ATTACK
        else:
            self.__stand = MemberStand.DEFENSE
        
    def get_hits(self) -> List[Tuple[BodyParts, int, bool]]:
        list:List[Tuple[BodyParts, int, bool]] = []
        for part in self.__attack_target:
            damage:int = random.randint(self.entity.min_damage, self.entity.max_damage) \
                    if (type(self.entity) is Monster) else random.randint(5, 10)
            
            is_crit:bool = False
            if random.random() < (self.__crit_chance / 100):
                damage = round(damage * 1.5)
                is_crit = True

            list.append((part, damage, is_crit))
        self.__attack_target.clear()
        return list
    
    def simulate_actions(self):
        self.__attack_target.clear()
        self.__protected_parts.clear()

        self.__attack_target = [random.choice(list(BodyParts))]
        self.__protected_parts = [random.choice(list(BodyParts))]

    def bet(self, money:Optional[int]):
        if (money):
            self.__bet_money += (money * 2)

    @property
    def full_battle_name(self) -> str:
        return f"<code>{self.entity.name}</code>" \
                if (type(self.entity) is Monster) else \
                    self.short_battle_name + f" - <code>{self.entity.length}см</code>"

    @property
    def short_battle_name(self) -> str:
        return f"<code>{self.entity.name}</code>" \
                if (type(self.entity) is Monster) else \
                    f"{self.link}" + (f'<code>[{self.entity.custom_title}]</code>' if self.entity.custom_title is not None else '')
    

    @property
    def link(self) -> str:
        return f'<a href="tg://user?id={self.entity.tg_id}">{self.entity.tg_name}</a>' \
                        if (type(self.entity) is User) else ""