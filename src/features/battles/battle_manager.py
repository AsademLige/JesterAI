import urllib

from core.utils.utils import Utils
from features.battles.battle_unit_entity import AttackStatus, BattleUnit, MemberStand, AttackResult
from features.battles.data.repository.monsters_repository import IMonstersRepository
from core.utils.enums import BattleMode, BattlePhases, MemberStatus
from features.battles.data.models.monster_dto import Monster
from core.utils.text_processing import TextProcessing as tp
from typing import Dict, List, Optional, Tuple, Union
from features.user.data.dtos.user_dto import User
from core.consts.dictionary import Dictionary
from core.utils.app_herald import AppHerald
from datetime import datetime, timedelta
from core.consts.config import Prefs
import logging
import random

class BattleManager():
    dict = Dictionary()
    prefs = Prefs()
    members:List[BattleUnit]
    logger:AppHerald = AppHerald()
    __mode:BattleMode
    __phase:BattlePhases

    __active_member:Optional[BattleUnit] = None
    __round:int = 0
    
    __battle_timer:timedelta
    __add_time_per_turn:timedelta
    battle_started:datetime = None
    last_status:str = ""
    max_motions_per_turn:int = 1

    @property
    def active_member(self) -> BattleUnit:
        return self.__active_member
    
    @property
    def round(self) -> int:
        return self.__round
    
    @property
    def phase(self) -> int:
        return self.__phase
    
    @property
    def battle_timer(self) -> timedelta:
        return self.__battle_timer
    
    @property
    def mode(self) -> int:
        return self.__mode

    def __init__(self, members:List[BattleUnit], mode:BattleMode):
        self.members = members
        self.__mode = mode
        self.__phase = BattlePhases.PREPARE
        pass

    @classmethod
    async def hunt(cls, hunter:User, monsters_repo:IMonstersRepository, monster_count:int = 1, boss:bool = False):
        lst:List[Union[Monster, User]] = [hunter]
        lst.extend(await monsters_repo.get_random_monsters_by_tag(monster_count, tag="boss" if boss else "mob"))
        
        cls.logger.send_log("battle", logging.INFO, 
                                    f"\n\nBattle: {hunter.tg_name} vs {lst[1].name} --------------------------------------------------")

        members:List[BattleUnit] = [await BattleUnit.create(entity) for entity in lst]
        return cls(
            members = members,
            mode = BattleMode.HUNT
        )
    
    @classmethod
    async def gladiators(cls, monsters_repo:IMonstersRepository, monster_count:int = 2):
        monsters:List[Monster] = await monsters_repo.get_random_monsters_by_tag(monster_count)
        members:List[BattleUnit] = [await BattleUnit.create(entity) for entity in monsters]

        return cls(
            members = members,
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
            self.__simulate_mobs()
            meeting:str = self.dict.hunt_monster_meeting_short(self.members[1].entity,
                                                         self.get_opponent().str_status,
                                                         self.members[1].fighting_style_visual())
            self.last_status = meeting
            return meeting
        if (self.__mode == BattleMode.GLADIATORS):
            self.__active_member = self.members[0]
            self.__simulate_mobs()
            return self.dict.gladiators_introduce(self.members, self.__get_ui_data())
        
    def start_battle(self, timer:timedelta = timedelta(seconds=30), 
                     add_time_per_turn:timedelta = timedelta(seconds=15)):
        self.__phase = BattlePhases.MOTION
        self.__round += 1
        self.__battle_timer = timer
        self.__add_time_per_turn = add_time_per_turn
        self.battle_started = datetime.now()
        
    def get_status(self) -> Optional[Tuple[str, BattlePhases, BattleUnit]]:
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

        fight_title:str = f"<blockquote><b>Раунд {self.round}</b>, таймер: {round((self.battle_started + self.__battle_timer - datetime.now()).total_seconds())} сек</blockquote>" if self.__mode == BattleMode.HUNT else f"⚔️ <b>ДРЫНОСТОЯНИЕ!</b>⚔️ <code>Раунд: {self.__round}</code>" + '\n\n'

        ui:str = tp.text_replacement(fight_title + self.dict.combat_interface + ("\n💥 {{turn}}, выбери, куда ударить:" 
                                    if self.__active_member.stand == MemberStand.ATTACK else "\n🛡 {{turn}}, выбери, что защитить:"),
                                    {**self.__get_ui_data()}, ignore_missing_keys = True)
        
        if (self.mode == BattleMode.GLADIATORS and self.__phase == BattlePhases.REST):
            self.__phase = BattlePhases.MOTION

        return (ui, self.__phase, self.__active_member)
    
    def __get_ui_data(self) -> Dict[str, str]:
        members_ui:Dict[str, str] = {}

        for i in range(len(self.members)):

            bet:str = f" (<b>{self.members[i].bet_money}💰</b>)" if (self.members[i].bet_money > 0) else ""

            members_ui[f"player{i+1}"] = self.members[i].full_battle_name + bet
            members_ui[f"player{i+1}_icon"] = self.members[i].utf8_icon
            members_ui[f"health{i+1}"] = Utils.progress_bar(self.members[i].hp, self.members[i].max_hp)
            members_ui[f"mana{i+1}"] = Utils.progress_bar(self.members[i].mana, self.members[i].max_mana, 5)
            
            if (self.members[i] == self.__active_member):
                members_ui["turn"] = f"{self.members[i].link}"
            
        return members_ui
        
    def escape(self) -> Optional[str]:
        """Побег из боя участника, которому принадлежит ход"""
        if (self.__active_member):
            self.__phase = BattlePhases.BATTLE_END
            return self.dict.battle_escape(self.__active_member.entity)

    def __start_action(self) -> Tuple[str, BattlePhases, BattleUnit]:
        """Основной цикл боя, в котором сменяются фазы, и передается очередность хода"""
        self.__phase = BattlePhases.REST
        self.__active_member.rest(motions=self.max_motions_per_turn)
        self.__round += 1
        
        next_index:int = self.members.index(self.__active_member) + 1
        if (self.__mode == BattleMode.HUNT or next_index > len(self.members) - 1):
            result = self.__end_turn()
            return result
        elif (self.__mode == BattleMode.DUEL):
            self.__active_member = 0 if (next_index > len(self.members) - 1) else self.members[next_index]
        
        return (self.get_status(), self.__phase, self.__active_member)
        
    def __end_turn(self) -> Tuple[str, BattlePhases, Optional[BattleUnit]]:
        self.__battle_timer += self.__add_time_per_turn
        
        opponent:BattleUnit = self.get_opponent()    

        turn_result:str = ""

        status:Optional[AttackResult] = self.__active_member.attacked(opponent)
        opponent_status:Optional[AttackResult] = opponent.attacked(self.__active_member)
        self.__simulate_mobs()

        if (status and status.status == AttackStatus.KILLED and opponent_status and opponent_status.status == AttackStatus.KILLED):
            self.__phase = BattlePhases.BATTLE_END
            self.logger.send_log("battle", logging.INFO, 
                                    f"\nBattle End Draw --------------------------------------------------")
            
            return ("⚰️⚰️ Бой кровавый, и победителя в нем нет, лежат все без дыхания...", self.__phase, None)
        elif (opponent_status and opponent_status.status == AttackStatus.KILLED):
            self.__phase = BattlePhases.BATTLE_END
            if (self.mode == BattleMode.HUNT):
                opponent.loot_by(self.__active_member)
            turn_result = self.dict.battle_end(opponent, self.__active_member, self.__mode, opponent_status)

            self.logger.send_log("battle", logging.INFO, 
                                    f"\nBattle End user WIN --------------------------------------------------")
            
            return (turn_result, self.__phase, self.__active_member)
        elif (status and status.status == AttackStatus.KILLED):
            self.__phase = BattlePhases.BATTLE_END
            turn_result = self.dict.battle_end(self.__active_member, opponent, self.__mode, status)

            self.logger.send_log("battle", logging.INFO, 
                                    f"\nBattle End user LOSE --------------------------------------------------")
            
            return (turn_result, self.__phase, None)

        if (not self.__mode == BattleMode.HUNT):
            turn_result += self.dict.battle_turn_log(self.__active_member, opponent, 
                                                    status, opponent_status, self.mode)
            turn_result += "\n\n"
            turn_result += self.dict.battle_turn_log(opponent, self.__active_member, 
                                                    opponent_status, status, self.mode)
        else:
            turn_result += self.dict.battle_dice_turn_log(self.__active_member, opponent,
                                                    status, opponent_status, self.mode)
        

        if (self.__mode == BattleMode.HUNT and not (status and status.status == AttackStatus.KILLED)):
            attack_status:str = ""
            opponent_attack_status:str = ""

            if (status):
                attack_status = f"<i>(-{status.damage}{'💥' if status.attack_dice == 20 else '🩸'})</i>" if (status.status == AttackStatus.DAMAGED) else "(🛡)" if (status.status == AttackStatus.DEFENDED) else ""

            if (opponent_status):
                opponent_attack_status = f"<i>(-{opponent_status.damage}{'💥' if opponent_status.attack_dice == 20 else '🩸'})</i>" if (opponent_status.status == AttackStatus.DAMAGED) else "(🛡)" if (opponent_status.status == AttackStatus.DEFENDED) else ""

            turn_result = f"<blockquote><b>Раунд {self.round-1}</b>, таймер: {round((self.battle_started + self.__battle_timer - datetime.now()).total_seconds())} сек</blockquote>" + \
                f"\n{tp.text_replacement(self.dict.combat_interface, {**self.__get_ui_data(), 'player2_strategy':self.get_opponent().str_status, 'player1_status_change': attack_status, 'player2_status_change':opponent_attack_status}, ignore_missing_keys = True)}" + turn_result

        if (self.__mode == BattleMode.GLADIATORS and not self.__phase == BattlePhases.BATTLE_END):
            turn_result += tp.text_replacement(f"\n\n{self.dict.gladiators_interface}", {**self.__get_ui_data()})

        self.last_status = turn_result

        return (turn_result, self.__phase, self.__active_member)
    
    def __simulate_mobs(self):
        for member in self.members:
            if (member.is_monster):
                member.simulate_actions()
    
    def get_opponent(self) -> BattleUnit:
        other_members:List = list(self.members)
        other_members.pop(self.members.index(self.__active_member))
        return random.choice(other_members)
    
    def get_bet_gladiator(self) -> Optional[BattleUnit]:
        return next((gld for gld in self.members if gld.bet_money > 0), None)

    def serialize_battle_info(self) -> str:
        monster:BattleUnit = self.get_opponent()
        user:User = self.active_member.entity
        
        battle_params:dict = {
            "energy_left" : user.energy,
            "monster_name" : monster.entity.name,
            "monster_hp" : monster.entity.health,
            "monster_id" : monster.entity.id,
            "is_boss": monster.is_boss,
            "money_drop": monster.inventory[1],
            "items_drop" : [f"{item.utf8_icon} {str(item.title)}" for item in monster.inventory[0]]
        }

        raw_data = urllib.parse.urlencode(battle_params)

        return raw_data
