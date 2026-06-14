from features.battles.battle_unit_entity import AttackStatus, BattleUnit, MemberStand, MemberStrategy
from core.utils.enums import BattleMode, BattlePhases, MemberStatus
from core.utils.text_processing import TextProcessing as tp
from typing import Any, Dict, List, Optional, Tuple, Union
from core.data.datasource import DataBase
from features.battles.data.models.monster_model import Monster
from core.consts.dictionary import Dictionary
from datetime import datetime, timedelta
from core.data.models.user_model import User
from core.consts.config import Prefs
import random

class BattleManager():
    db = DataBase()
    dict = Dictionary()
    prefs = Prefs()
    members:List[BattleUnit]
    __mode:BattleMode
    __phase:BattlePhases

    __active_member:Optional[BattleUnit] = None
    __round:int = 0
    
    __battle_timer:timedelta
    __add_time_per_turn:timedelta
    battle_started:datetime
    motions_per_turn:int = 2

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
    def battle_timer(self) -> int:
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
    async def hunt(cls, hunter:User, monster_count:int = 1, boss:bool = False):
        lst:List[Union[Monster, User]] = [hunter]
        lst.extend(await cls.db.get_random_monsters_by_tag(monster_count, tag="boss" if boss else "mob"))

        members:List[BattleUnit] = [await BattleUnit.create(entity) for entity in lst]
        return cls(
            members = members,
            mode = BattleMode.HUNT
        )
    
    @classmethod
    async def gladiators(cls, monster_count:int = 2):
        monsters:List[Monster] = await cls.db.get_random_monsters_by_tag(monster_count)
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
            meeting:str = self.dict.hunt_monster_meeting(self.members[1].entity,
                                                         self.get_opponent().str_status,
                                                         self.members[1].fighting_style_visual())

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

    def __start_action(self) -> Tuple[str, BattlePhases, BattleUnit]:
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
        
    def __end_turn(self) -> Tuple[str, BattlePhases, Optional[BattleUnit]]:
        self.__battle_timer += self.__add_time_per_turn
        
        opponent:BattleUnit = self.get_opponent()    

        print(f"cdlog attack {self.active_member.attack_target} : {opponent.attack_target}")
        print(f"cdlog protect {self.active_member.protected_parts} : {opponent.protected_parts}")

        turn_result:str = ""
        status:Optional[Tuple[AttackStatus, int, bool]] = self.__active_member.attacked(opponent)
        opponent_status:Optional[Tuple[AttackStatus, int, bool]] = opponent.attacked(self.__active_member)
        self.__simulate_mobs()

        print(f"cdlog {opponent_status[1]} : {status[1]}")

        if (status[0] == AttackStatus.KILLED and opponent_status[0] == AttackStatus.KILLED):
            self.__phase = BattlePhases.BATTLE_END
            return ("⚰️⚰️ Бой кровавый, и победителя в нем нет, лежат все без дыхания...", self.__phase, None)
        elif (opponent_status and opponent_status[0] == AttackStatus.KILLED):
            self.__phase = BattlePhases.BATTLE_END
            if (self.mode == BattleMode.HUNT):
                opponent.loot_by(self.__active_member)
            turn_result = self.dict.battle_end(opponent, self.__active_member, self.__mode, (opponent_status[1], opponent_status[2]))
            return (turn_result, self.__phase, self.__active_member)
        elif (status[0] == AttackStatus.KILLED):
            self.__phase = BattlePhases.BATTLE_END
            turn_result = self.dict.battle_end(self.__active_member, opponent, self.__mode, (status[1], status[2]))
            return (turn_result, self.__phase, opponent)

        turn_result += self.dict.battle_turn_log(self.__active_member, opponent, 
                                                 status, opponent_status, self.mode)
        
        if (not self.__mode == BattleMode.HUNT):
            turn_result += "\n\n"
            turn_result += self.dict.battle_turn_log(opponent, self.__active_member, 
                                                    opponent_status, status, self.mode)

        if (self.__mode == BattleMode.HUNT and not status[0] == AttackStatus.KILLED):
            turn_result += f"\n\n{self.get_opponent().str_status}"
            turn_result = f"<blockquote><b>Сводка раунда {self.round-1}</b>, таймер: {round((self.battle_started + self.__battle_timer - datetime.now()).total_seconds())} сек</blockquote>\n" + turn_result
            if (not self.active_member.strategy == MemberStrategy.DEFENSE):
                turn_result += "\n<i>❗️ Побег и лечение невозможны, сначала нужно уйти в защиту!</i>"

        if (self.__mode == BattleMode.GLADIATORS and not self.__phase == BattlePhases.BATTLE_END):
            turn_result += tp.text_replacement(f"\n\n{self.dict.gladiators_interface}", {**self.__get_ui_data()})

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
