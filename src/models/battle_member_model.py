from __future__ import annotations
from src.domain.utils.enums import AttackStatus, BattleMode, BodyParts, MemberStatus
from src.domain.controllers.item_drop_manager import ItemDropManager
from typing import Dict, List, Optional, Tuple, Union
from src.models.monster_model import Monster
from src.models.item_model import Item
from src.models.user_model import User
from enum import Enum
import json
import random
import copy

class MemberStrategy(Enum):
    AGGRESSIVE = "AGGRESSIVE"
    CONTR_STRIKE = "CONTR_STRIKE"
    DEFENSE = "DEFENSE"

class MemberStand(Enum):
    ATTACK = 0
    DEFENSE = 1

class MonsterTags(Enum):
    MOB = "mob"
    BOSS = "boss"


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
    __inventory:Optional[Tuple[List[Item], int]]
    
    __fighting_style:Optional[Dict[MemberStrategy, int]] 

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
    
    @property
    def is_monster(self) -> bool:
        return type(self.entity) is Monster
    
    @property
    def is_player(self) -> bool:
        return type(self.entity) is User
    
    @property
    def inventory(self) -> Optional[Tuple[List[Item], int]]: return self.__inventory

    @property
    def is_mob(self) -> bool:
        return self.is_monster \
               and self.entity.tag == MonsterTags.MOB.value
    
    @property
    def is_boss(self) -> bool: 
        return self.is_monster \
               and self.entity.tag == MonsterTags.BOSS.value

    def __init__(self, entity:Union[Monster, User], 
                 drop:Optional[Tuple[List[Item], int]], 
                 mode:BattleMode):
        self.entity = entity
        self.__bet_money = 0
        self.__attack_target = []
        self.__protected_parts = []
        self.__last_turn_result = None
        self.__crit_chance = entity.crit_chance if type(self.entity) is Monster else 15
        self.__max_hp = entity.health if type(self.entity) is Monster else 35
        self.__hp = self.__max_hp
        self.utf8_icon = entity.utf8_icon if entity.utf8_icon else random.choice(["🥷","🧝‍♂️","🧙🏿‍♂️","🧙🏼"])
        self.__inventory = drop if (self.is_monster) else None

        if (self.is_monster):
            raw_style = json.loads(entity.fighting_style)
            self.__fighting_style = {}
            for k, v in raw_style["strategy"].items():
                self.__fighting_style[MemberStrategy(k)] = v
        pass
    
    @classmethod
    async def create(cls, entity:Union[Monster, User], mode:BattleMode = BattleMode.DUEL):
        drop:Optional[Tuple[List[Item], int]] = await ItemDropManager.generate_drop(entity)\
                                                    if (type(entity) is Monster) else None
        return cls(entity, drop, mode)

    def attacked(self, opponent:BattleMember) -> Optional[Tuple[AttackStatus, int, bool]]:
        hits:List[Tuple[BodyParts, int, bool]] = opponent.get_hits()
        attack_status:AttackStatus = AttackStatus.NONE
        total_damage:int = 0
        is_crit:bool = False

        modifier:float = 0.75 if (self.strategy == MemberStrategy.DEFENSE) else \
                    1.25 if (self.strategy == MemberStrategy.AGGRESSIVE) else 1
        
        print(f"{self.short_battle_name} modifier: {modifier}")

        for hit in hits:
            if (not hit[0] in self.protected_parts):
                self.__hp -= round(hit[1] * modifier)
                total_damage += round(hit[1] * modifier)
                if (hit[2]):
                    is_crit = True
                if (self.__hp <= 0): 
                    self.__status = MemberStatus.DEAD
                    attack_status = AttackStatus.KILLED
                else:
                    attack_status = AttackStatus.DAMAGED
            else:
                if (not attack_status or attack_status == AttackStatus.NONE):
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
                    if (self.is_monster) else random.randint(5, 10)
            
            is_crit:bool = False
            if random.random() < (self.__crit_chance / 100):
                damage = round(damage * 1.5)
                is_crit = True

            list.append((part, damage, is_crit))
        self.__attack_target.clear()
        return list
    
    def put_to_inventory(self, loot:Tuple[List[Item], int]):
        if (self.__inventory):
            self.__inventory = (self.__inventory[0] + loot[0], 
                                self.__inventory[1] + loot[1])
        else:
            self.__inventory = loot
    
    def loot_by(self, marauder:BattleMember):
        pull_out = copy.copy(self.__inventory)
        self.__inventory = None
        marauder.put_to_inventory(pull_out)
    
    def simulate_actions(self):
        self.__attack_target.clear()
        self.__protected_parts.clear()
        
        total_strategy_weight:int = 0

        for strategy, weight in self.__fighting_style.items():
            total_strategy_weight += weight

        roll = random.uniform(0, total_strategy_weight)

        current:int = 0
        for strategy, weight in self.__fighting_style.items():
            current += weight
            if roll <= current:
                self.__strategy = strategy
                break

        if (self.__strategy == MemberStrategy.AGGRESSIVE):
            self.__attack_target.extend([random.choice(list(BodyParts)), 
                                    random.choice(list(BodyParts))])
        elif (self.__strategy == MemberStrategy.CONTR_STRIKE):
            self.__attack_target.append(random.choice(list(BodyParts)))
            self.__protected_parts.append(random.choice(list(BodyParts)))
        elif (self.__strategy == MemberStrategy.DEFENSE):
            self.__protected_parts.extend([random.choice(list(BodyParts)),
                                      random.choice(list(BodyParts))])

    def bet(self, money:Optional[int]):
        if (money):
            self.__bet_money += (money * 2)

    def fighting_style_visual(self, total_pairs: int = 3) -> str:
        STRATEGY_EMOJIS = {
            MemberStrategy.AGGRESSIVE: "⚔️⚔️",      
            MemberStrategy.CONTR_STRIKE: "⚔️🛡",    
            MemberStrategy.DEFENSE: "🛡🛡"          
        }
        total_weight = sum(self.__fighting_style.values())
        
        if total_weight == 0:
            return ""
        
        swords = 0
        shields = 0
        
        for strategy, weight in self.__fighting_style.items():
            pairs = round((weight / total_weight) * total_pairs)
            emoji_pair = STRATEGY_EMOJIS[strategy]
            
            swords += emoji_pair.count("⚔️") * pairs
            shields += emoji_pair.count("🛡") * pairs
        
        return "⚔️" * swords + "🛡" * shields

    @property
    def str_status(self) -> str:
        if (self.strategy == MemberStrategy.AGGRESSIVE):
            return f"<blockquote>⚔️⚔️ <i>{self.short_battle_name} пропишет двоечку</i></blockquote>"
        elif (self.strategy == MemberStrategy.CONTR_STRIKE):
            return f"<blockquote>⚔️🛡 <i>{self.short_battle_name} лупанет в ответ</i></blockquote>"
        elif (self.strategy == MemberStrategy.DEFENSE):
            return f"<blockquote>🛡🛡 <i>{self.short_battle_name} плотно прикроет туз</i></blockquote>"

    @property
    def full_battle_name(self) -> str:
        return f"<code>{self.entity.name}</code>" \
                if (self.is_monster) else \
                    self.short_battle_name + f" - <code>{self.entity.length}см</code>"

    @property
    def short_battle_name(self) -> str:
        return f"<code>{self.entity.name}</code>" \
                if (self.is_monster) else \
                    f"{self.link}" + (f'<code>[{self.entity.custom_title}]</code>' if self.entity.custom_title is not None else '')
    

    @property
    def link(self) -> str:
        return f'<a href="tg://user?id={self.entity.tg_id}">{self.entity.tg_name}</a>' \
                        if (self.is_player) else ""