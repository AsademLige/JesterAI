from src.models.battle_member_model import AttackStatus, BattleMember, BodyParts
from src.domain.utils.text_processing import TextProcessing as tp
from typing import Any, Dict, List, Optional, Tuple, Union
from src.services.data_base.db import DataBase
from src.models.monster_model import Monster
from src.data.dictionary import Dictionary
from datetime import datetime, timedelta
from aiogram.types import Message, Chat
from src.models.user_model import User
from src.data.config import Prefs
from random import Random
from aiogram import Bot
from enum import Enum
import random

class BattleMode(Enum):
    HUNT = 0
    DUEL = 1
    GLADIATORS = 2

class BattlePhases(Enum):
    PREPARE = 0
    ATTACK = 1
    DEFENSE = 2
    BATTLE_END = 3

class BattleController():
    db = DataBase()
    dict = Dictionary()
    prefs = Prefs()
    members:List[BattleMember]
    mode:BattleMode
    phase:BattlePhases

    turn:int = -1
    round:int = 1
    battle_timer:timedelta
    battle_started:datetime

    def __init__(self, members:List[Union[Monster, User]], mode:BattleMode):
        self.members = [BattleMember(entity) for entity in members]
        self.mode = mode
        self.phase = BattlePhases.PREPARE
        pass

    @classmethod
    def hunt(cls, members:List[Union[Monster, User]]):
        return cls(
            members = members,
            mode = BattleMode.HUNT
        )
    
    @classmethod
    def duel(cls, members:List[User]):
        return cls(
            members = members,
            mode = BattleMode.DUEL
        )
    
    def prepare_battle(self):
        if (self.mode == BattleMode.HUNT):
            #TODO: Можно будет расширить возможности боя на несколько монстров
            return self.dict.monster_meeting(self.members[1].entity)
        
    def start_battle(self, timer:timedelta = timedelta(seconds=30)):
        self.phase = BattlePhases.ATTACK
        self.turn = 0
        self.battle_timer = timer
        self.battle_started = datetime.now()
        
    def get_turn_ui(self) -> str:
        return tp.text_replacement(self.dict.combat_interface + ("💥 {{turn}}, выбери, куда ударить:" 
                                    if self.phase == BattlePhases.ATTACK else "🛡 {{turn}}, выбери, что защитить:"),
                                   {
                                       **self.__get_members_ui(),
                                       "timer": f"{round((self.battle_started + self.battle_timer - datetime.now()).total_seconds())} сек",
                                       "fight_name": f"🏹 <b>ОХОТА!</b>🏹 <code>Раунд: {self.round}</code>" 
                                            if self.mode == BattleMode.HUNT else 
                                        f"⚔️ <b>ДРЫНОСТОЯНИЕ!</b>⚔️ <code>Раунд: {self.round}</code>",
                                   })
    
    def __get_members_ui(self):
        members_ui:Dict[str, str] = {}

        for i in range(len(self.members)):

            members_ui[f"player{i+1}"] = self.members[i].full_battle_name
            members_ui[f"player{i+1}_icon"] = self.members[i].utf8_icon
            members_ui[f"health{i+1}"] = self.health_bar(self.members[i].hp, self.members[i].entity.health \
                                        if (type(self.members[i].entity) is Monster) else 30)
            
            if (i == self.turn):
                members_ui["turn"] = self.members[i].link
            
        return members_ui
        
    def escape(self):
        """Побег из боя участника, которому принадлежит ход"""
        self.phase = BattlePhases.BATTLE_END
        return self.dict.battle_escape(self.members[self.turn if (self.turn >= 0) else 0].entity)

    def turn_loop(self, part:BodyParts) -> Tuple[str, BattlePhases]:
        """Основной цикл боя, в котором сменяются фазы, и передается очередность хода"""
        if (self.phase == BattlePhases.ATTACK):
            self.members[self.turn].attack_target = part
            self.phase = BattlePhases.DEFENSE
        elif (self.phase == BattlePhases.DEFENSE):
            self.members[self.turn].protect = part
            self.phase = BattlePhases.ATTACK
            self.round += 1

            if (self.mode == BattleMode.HUNT or self.turn == len(self.members) - 1):
                result = self.end_turn()
                self.turn = 0
                return result
            elif (self.mode == BattleMode.DUEL):
                self.turn = 0 if (self.turn == len(self.members) - 1) else self.turn + 1
        
        return (self.get_turn_ui(), self.phase)
                
        
    def end_turn(self) -> Tuple[str, BattlePhases, Optional[User]]:
        self.__simulate_mobs()
        
        opponent:BattleMember = self.__get_opponent()
        
        hit:int = self.members[self.turn].get_hit()
        opponent_hit:int = opponent.get_hit()

        turn_result:str = ""
        status:AttackStatus = self.members[self.turn].attacked(opponent.attack_target, opponent_hit)
        opponent_status:Optional[AttackStatus] = opponent.attacked(self.members[self.turn].attack_target, hit)

        if (not self.mode == BattleMode.HUNT and status == AttackStatus.KILLED and opponent_status == AttackStatus.KILLED):
            self.phase = BattlePhases.BATTLE_END
            return ("Оба сдохли", self.phase, None)
        elif (opponent_status == AttackStatus.KILLED):
            self.phase = BattlePhases.BATTLE_END
            turn_result = tp.text_replacement("🎯 {{player1}} {{dead}}", {
                "player1": opponent.short_battle_name,
                "dead": tp.text_replacement(random.choice(self.dict.battle_dead_description), {
                    **self.dict.random_member(),
                    **self.dict.get_part_cases(opponent.protect),
                })
            })
            return (turn_result, self.phase, self.members[self.turn].entity)
        elif (status == AttackStatus.KILLED):
            self.phase = BattlePhases.BATTLE_END
            turn_result = tp.text_replacement("☠️ {{player1}} {{dead}}", {
                "player1": self.members[self.turn].short_battle_name,
                "dead": tp.text_replacement(random.choice(self.dict.battle_dead_description), {
                    **self.dict.random_member(),
                    **self.dict.get_part_cases(opponent.protect),
                })
            })
        
        if (status == AttackStatus.DEFENDED and opponent_status == AttackStatus.DEFENDED):
            turn_result = tp.text_replacement("🛡🛡 {{player1}} {{protect1}}, также как и {{player2}} {{protect2}}",{
                "player1": self.members[self.turn].short_battle_name,
                "player2": opponent.short_battle_name,
                "protect1": tp.text_replacement(random.choice(self.dict.battle_protect_description), 
                                                {**self.dict.get_part_cases(self.members[self.turn].protect),
                                                 **self.dict.random_member()}),
                "protect2": tp.text_replacement(random.choice(self.dict.battle_protect_description), 
                                                {**self.dict.get_part_cases(opponent.protect),
                                                 **self.dict.random_member()}),
            })
        elif (status == AttackStatus.DAMAGED and opponent_status == AttackStatus.DEFENDED):
            turn_result = tp.text_replacement("🩸🛡 {{player2}} {{attack}}! {{player1}} {{attacked}} на <code>💥{{opponent_hit}}</code>, пока {{player2}} {{protect}}",{
                "player1": self.members[self.turn].short_battle_name,
                "player2": opponent.short_battle_name,
                "protect": tp.text_replacement(random.choice(self.dict.battle_protect_description),
                                               {**self.dict.get_part_cases(opponent.protect),
                                                 **self.dict.random_member()}),
                "attacked": tp.text_replacement(random.choice(self.dict.battle_attacked_description), {
                    **self.dict.get_part_cases(self.members[self.turn].protect),
                    **self.dict.random_member()
                }),
                "attack": tp.text_replacement(random.choice(self.dict.battle_attack_description), {
                    **self.dict.get_part_cases(opponent.attack_target),
                                            **self.dict.random_member()
                }),
                "opponent_hit" : opponent_hit,
            })
        elif (status == AttackStatus.DEFENDED and opponent_status == AttackStatus.DAMAGED):
            turn_result = tp.text_replacement("🛡🩸 {{player1}} {{protect}}, затем {{attack}}! {{player2}} {{attacked}} на <code>💥{{hit}}</code>",{
                "player1": self.members[self.turn].short_battle_name,
                "player2": opponent.short_battle_name,
                "protect": tp.text_replacement(random.choice(self.dict.battle_protect_description), {
                    **self.dict.get_part_cases(self.members[self.turn].protect),
                                            **self.dict.random_member()
                }),
                "attacked": tp.text_replacement(random.choice(self.dict.battle_attacked_description), {
                    **self.dict.get_part_cases(opponent.protect),
                                    **self.dict.random_member()
                }),
                "attack": tp.text_replacement(random.choice(self.dict.battle_attack_description), {
                    **self.dict.get_part_cases(self.members[self.turn].attack_target),
                                        **self.dict.random_member()
                }),
                "hit" : hit,
            })
        elif (status == AttackStatus.DAMAGED and opponent_status == AttackStatus.DAMAGED):
            turn_result = tp.text_replacement("🩸🩸 {{player1}} {{attacked1}} на <code>💥{{opponent_hit}}</code>, но и {{player2}} {{attacked2}} на <code>💥{{hit}}</code>",{
                "player1": self.members[self.turn].short_battle_name,
                "player2": opponent.short_battle_name,
                "attacked1": tp.text_replacement(random.choice(self.dict.battle_attacked_description), {
                    **self.dict.get_part_cases(self.members[self.turn].protect),
                        **self.dict.random_member()
                }),
                "attacked2": tp.text_replacement(random.choice(self.dict.battle_attacked_description), {
                     **self.dict.get_part_cases(opponent.protect),
                        **self.dict.random_member()
                }),
                "opponent_hit" : opponent_hit,
                "hit" : hit,
            })

        return (turn_result, self.phase, None)
    
    def __simulate_mobs(self):
        for member in self.members:
            if (type(member.entity) is Monster):
                member.simulate_actions()
    
    def __get_opponent(self) -> BattleMember:
        return self.members[self.turn+1] if (self.turn+1 < len(self.members)) else self.members[0]

    def health_bar(self, current, maximum, length=10):
        """Создает полоску здоровья"""
        filled_bars = int((current / maximum) * length)
        filled_bars = min(filled_bars, length)
        return ("▰" * filled_bars + "□" * (length - filled_bars)) + f" {current}/{maximum}"
