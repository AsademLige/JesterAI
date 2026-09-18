from __future__ import annotations
from core.utils.enums import AttackStatus, BattleMode, BodyParts, MemberStatus
from features.items.data.models.base_item_dto import BaseItem
from features.battles.data.models.monster_dto import Monster
from typing import Dict, List, Optional, Tuple, Union
from features.battles.loot_manager import LootManager
from features.user.data.dtos.user_dto import User
from enum import Enum
import random
import json
import copy

class Hit:
    part:BodyParts
    damage:int
    dice:int

    def __init__(self, part:BodyParts, damage:int, dice:int):
        self.part = part
        self.damage = damage
        self.dice = dice

class AttackResult:
    status:AttackStatus
    damage:int
    attack_dice:int
    defense_dice:int

    def __init__(self, status:AttackStatus, damage:int, attack_dice:int, defense_dice:int):
            self.status = status
            self.damage = damage
            self.attack_dice = attack_dice
            self.defense_dice = defense_dice

class UnitStrategy(Enum):
    AGGRESSIVE = "AGGRESSIVE"
    CONTR_STRIKE = "CONTR_STRIKE"
    DEFENSE = "DEFENSE"

class MemberStand(Enum):
    ATTACK = 0
    DEFENSE = 1

class MonsterTags(Enum):
    MOB = "mob"
    BOSS = "boss"


class BattleUnit():
    entity:Union[Monster, User]
    utf8_icon:str

    __attack_target:List[BodyParts]
    __protected_parts:List[BodyParts]
    __protect_dice:int = -1

    __status:MemberStatus = MemberStatus.FULL_OF_ENERGY

    __hp:int
    __max_hp:int
    __motions_left:int = 1
    __mana:int
    __max_mana:int
    __crit_chance:int
    __bet_money:int

    __strategy:UnitStrategy = UnitStrategy.CONTR_STRIKE
    __last_strategy:Optional[UnitStrategy] = None
    __stand:MemberStand = MemberStand.ATTACK

    __last_turn_result:Optional[AttackStatus]
    __inventory:Optional[Tuple[List[BaseItem], int]]
    
    __fighting_style:Optional[Dict[UnitStrategy, int]] 

    @property
    def hp(self) -> int:
        return self.__hp
    
    @property
    def mana(self) -> int:
        return self.__mana
    
    @property
    def max_mana(self) -> int:
        return self.__max_mana
    
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
    def protect_dice(self) -> int:
        return self.__protect_dice
    
    @property
    def strategy(self) -> UnitStrategy:
        return self.__strategy
    
    @property
    def last_strategy(self) -> UnitStrategy:
        return self.__last_strategy
    
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
    def inventory(self) -> Optional[Tuple[List[BaseItem], int]]: return self.__inventory

    @property
    def is_mob(self) -> bool:
        return self.is_monster \
               and self.entity.tag == MonsterTags.MOB.value
    
    @property
    def is_boss(self) -> bool: 
        return self.is_monster \
               and self.entity.tag == MonsterTags.BOSS.value

    def __init__(self, entity:Union[Monster, User], 
                 drop:Optional[Tuple[List[BaseItem], int]], 
                 mode:BattleMode):
        self.entity = entity
        self.__bet_money = 0
        self.__attack_target = []
        self.__protected_parts = []
        self.__last_turn_result = None
        self.__crit_chance = entity.crit_chance if type(self.entity) is Monster else 0
        self.__max_hp = (entity.health if type(self.entity) is Monster else 35) * 3
        self.__hp = self.__max_hp
        self.__max_mana = 5
        self.__mana = self.__max_mana
        self.utf8_icon = entity.utf8_icon if entity.utf8_icon else random.choice(["🥷","🧝‍♂️","🧙🏿‍♂️","🧙🏼"])
        self.__inventory = drop if (self.is_monster) else None

        if (self.is_monster):
            raw_style = json.loads(entity.fighting_style)
            self.__fighting_style = {}
            for k, v in raw_style["strategy"].items():
                self.__fighting_style[UnitStrategy(k)] = v
        pass
    
    @classmethod
    async def create(cls, entity:Union[Monster, User], mode:BattleMode = BattleMode.DUEL):
        drop:Optional[Tuple[List[BaseItem], int]] = await LootManager.generate_drop(entity)\
                                                    if (type(entity) is Monster) else None
        return cls(entity, drop, mode)

    def attacked(self, opponent:BattleUnit) -> Optional[AttackResult]:
        hits:List[Hit] = opponent.get_hits()
        attack_status:AttackStatus = AttackStatus.NONE
        total_damage:int = 0

        # modifier:float = 0.75 if (self.strategy == UnitStrategy.DEFENSE and self.is_player) else \
        #             1.25 if (self.strategy == UnitStrategy.AGGRESSIVE) else 1

        attack_result:AttackResult = None

        for hit in hits:
            modifier:float = 1 if (not hit.dice == 20) else 2
            if (not hit.part in self.protected_parts or hit.dice > self.protect_dice):
                self.__hp -= round(hit.damage * modifier)
                total_damage += round(hit.damage * modifier)
                if (self.__hp <= 0): 
                    self.__status = MemberStatus.DEAD
                    attack_status = AttackStatus.KILLED
                else:
                    attack_status = AttackStatus.DAMAGED

                attack_result = AttackResult(attack_status, total_damage, hit.dice, self.protect_dice)
            else:
                if (not attack_status or attack_status == AttackStatus.NONE):
                    attack_status = AttackStatus.DEFENDED
                attack_result = AttackResult(attack_status, total_damage, -1, self.protect_dice)

        self.__protected_parts.clear()
        self.__protect_dice = -1
        self.__last_turn_result = attack_status

        return attack_result

    def take_aim(self, part:Optional[BodyParts]) -> MemberStatus:
        if (self.__stand == MemberStand.ATTACK and self.__motions_left > 0):
            self.__attack_target.append(part)
            self.__motions_left -= 1
            if (self.__motions_left == 0):
                self.__status = MemberStatus.EXHAUSTED
            else:
                if (not self.__strategy == UnitStrategy.AGGRESSIVE):
                    self.__stand = MemberStand.DEFENSE
        return self.__status

    def protect(self, part:Optional[BodyParts]) -> MemberStatus:
        if (self.__stand == MemberStand.DEFENSE and self.__motions_left > 0):
            self.__protected_parts.append(part)
            self.__protect_dice = random.randint(1, 20)
            self.__motions_left -= 1
            if (self.__motions_left == 0):
                self.__status = MemberStatus.EXHAUSTED
            else:
                if (not self.__strategy == UnitStrategy.DEFENSE):
                    self.__stand = MemberStand.ATTACK
        return self.__status

    def protect_all(self) -> MemberStatus:
        if (self.__stand == MemberStand.DEFENSE and self.__motions_left > 0):
            self.__protect_dice = random.randint(1, 20)
            self.__protected_parts = list(BodyParts)
            self.__status = MemberStatus.EXHAUSTED

    def rest(self, motions:int = 1) -> MemberStatus:
        self.__status = MemberStatus.FULL_OF_ENERGY
        self.choice_strategy(self.__strategy)
        self.__motions_left = motions
        return self.__status
    
    def heal(self, hp:int = 0):
        self.__hp += hp
    
    def choice_strategy(self, strategy:UnitStrategy):
        self.__strategy = strategy
        if (strategy == UnitStrategy.CONTR_STRIKE or
            strategy == UnitStrategy.AGGRESSIVE):
            self.__stand = MemberStand.ATTACK
        else:
            self.__stand = MemberStand.DEFENSE
        
    def get_hits(self) -> List[Hit]:
        list:List[Hit] = []
        for part in self.__attack_target:
            dice:int = random.randint(1, 20)

            crit_bonus:int = 0
            if (not dice == 1):
                crit_bonus = (self.__crit_chance // 5) - 1
                crit_bonus = max(0, crit_bonus)

            damage:int = random.randint(self.entity.min_damage, self.entity.max_damage) \
                    if (self.is_monster) else random.randint(5, 10)

            # dice = dice + crit_bonus
            # if (dice + crit_bonus > 20):
            #     dice = 20

            list.append(Hit(part, damage, dice))
        self.__attack_target.clear()
        return list
    
    def put_to_inventory(self, loot:Tuple[List[BaseItem], int]):
        if (self.__inventory):
            self.__inventory = (self.__inventory[0] + loot[0], 
                                self.__inventory[1] + loot[1])
        else:
            self.__inventory = loot
    
    def loot_by(self, marauder:BattleUnit):
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
                self.__last_strategy = self.__strategy
                self.__strategy = strategy
                break

        if (self.__strategy == UnitStrategy.AGGRESSIVE or self.__strategy == UnitStrategy.CONTR_STRIKE):
            self.__attack_target.append(random.choice(list(BodyParts)))
        elif (self.__strategy == UnitStrategy.DEFENSE):
            self.__protected_parts.append(random.choice(list(BodyParts)))
            self.__protect_dice = random.randint(1, 20)

    def bet(self, money:Optional[int]):
        if (money):
            self.__bet_money += (money * 2)

    def fighting_style_visual(self, total_pairs: int = 3) -> str:
        STRATEGY_EMOJIS = {
            UnitStrategy.AGGRESSIVE: "⚔️",      
            UnitStrategy.CONTR_STRIKE: "⚔️",    
            UnitStrategy.DEFENSE: "🛡"          
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
        str_strategy:str = f"⚔️" if (self.strategy == UnitStrategy.AGGRESSIVE or self.strategy == UnitStrategy.CONTR_STRIKE) else f"🛡"
        last_str_strategy:str = f"⚔️" if (self.last_strategy == UnitStrategy.AGGRESSIVE or self.last_strategy == UnitStrategy.CONTR_STRIKE) else f"🛡"
        return f"{last_str_strategy}->{str_strategy}" if (self.last_strategy and not self.strategy is self.last_strategy) else str_strategy   

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