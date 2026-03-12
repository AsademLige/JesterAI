from src.models.user_model import User
from src.models.monster_model import Monster
from typing import Optional, Union
from enum import Enum
import random

class BodyParts(Enum):
    HEAD = 0
    CHEST = 1
    KNEES = 2

class AttackStatus(Enum):
    DAMAGED = 0
    DEFENDED = 1
    KILLED = 2

class MemberStatus(Enum):
    ALIVE = 0
    DEAD = 1

class BattleMember():
    entity:Union[Monster, User]
    utf8_icon:str

    attack_target:Optional[BodyParts] = None
    protect:Optional[BodyParts] = None

    status:MemberStatus = MemberStatus.ALIVE

    __hp:int

    @property
    def hp(self):
        return self.__hp 

    def __init__(self, entity:Union[Monster, User]):
        self.entity = entity
        self.__hp = entity.health if type(entity) is Monster else 30
        self.utf8_icon = entity.utf8_icon if entity.utf8_icon else random.choice(["🥷","🧝‍♂️","🧙🏿‍♂️","🧙🏼"])
        pass
    
    def attacked(self, part:Optional[BodyParts], damage:int) -> AttackStatus:
        if (not part == self.protect):
            self.__hp -= damage
            if (self.__hp <= 0): 
                self.status = MemberStatus.DEAD
                return AttackStatus.KILLED
            else:
                return AttackStatus.DAMAGED
        else:
            return AttackStatus.DEFENDED
        
    def get_hit(self) -> int:
        return random.randint(self.entity.min_damage, self.entity.max_damage) \
                if (type(self.entity) is Monster) else random.randint(5, 10)
    
    def simulate_actions(self):
        self.attack_target = random.choice(list(BodyParts))
        self.protect = random.choice(list(BodyParts))

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