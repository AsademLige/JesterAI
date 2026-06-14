from enum import Enum


###Battle

class BattleMode(Enum):
    HUNT = 0
    DUEL = 1
    GLADIATORS = 2

class BattlePhases(Enum):
    PREPARE = 0
    MOTION = 1
    REST = 2
    BATTLE_END = 3

###Battle Member

class BodyParts(Enum):
    HEAD = 0
    CHEST = 1
    KNEES = 2

class AttackStatus(Enum):
    DAMAGED = 0
    DEFENDED = 1
    NONE = 2
    KILLED = 3

class MemberStatus(Enum):
    FULL_OF_ENERGY = 0
    EXHAUSTED = 1
    DEAD = 2