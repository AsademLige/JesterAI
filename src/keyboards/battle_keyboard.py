from src.domain.controllers.battle_controller import BattleController, BattlePhases
from src.models.battle_member_model import BodyParts, MemberStand, MemberStrategy
from src.models.user_inventory_item_model import UserInventoryItem
from src.keyboards.callback_fabrics import BattleCF, GladiatorsCF
from src.domain.utils.enums import AttackStatus, BattleMode
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, Message
from aiogram.types import InlineKeyboardButton
from src.data.dictionary import Dictionary
from typing import List, Optional, Tuple
from src.models.user_model import User
from src.models.item_model import Item
from src.data.config import Prefs
import random

prefs = Prefs()
dict = Dictionary()

class BattleKeyboard():
    def __init__(self):
        pass
    
    def link_keyboard(self, link:str) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.add(InlineKeyboardButton(text="⚔️", url=link))

        builder.adjust(1) 
        return builder.as_markup()
    
    def battle_keyboard(self, user:User, ctrl:BattleController, 
                        usable:Optional[List[Tuple[UserInventoryItem, Item]]] = None) -> InlineKeyboardMarkup:
        if (ctrl.mode == BattleMode.GLADIATORS):
            if (ctrl.phase == BattlePhases.PREPARE):
                return self.__gladiators_bets(user, ctrl)
            else:
                return self.__gladiators_fight(user, ctrl)

        if (ctrl.phase == BattlePhases.PREPARE or ctrl.phase == BattlePhases.REST):
                return self.__hunt_strategy_select(user, ctrl, usable)
        else:
            return self.__parts_selector(user, ctrl)

    def __hunt_strategy_select(self, user:User, ctrl:BattleController, 
                        usable:Optional[List[Tuple[UserInventoryItem, Item]]] = None) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(text="⚔️",
                callback_data=BattleCF(action=MemberStrategy.AGGRESSIVE.value,
                                        user_id=user.tg_id).pack()))
        builder.add(InlineKeyboardButton(text="🗡🛡",
                callback_data=BattleCF(action=MemberStrategy.CONTR_STRIKE.value,
                                        user_id=user.tg_id).pack()))
        builder.add(InlineKeyboardButton(text="🛡🛡",
                callback_data=BattleCF(action=MemberStrategy.DEFENSE.value,
                                        user_id=user.tg_id).pack()))
        
        if (ctrl.phase == BattlePhases.PREPARE or ctrl.active_member.strategy == MemberStrategy.DEFENSE):
                # builder.add(InlineKeyboardButton(text="💨 Побег",
                #         callback_data=BattleCF(action="escape", 
                #                                 user_id=user.tg_id).pack()))
                
                if (ctrl.phase == BattlePhases.REST):
                        for i in range(len(usable)):
                                if (usable[i][0].quantity > 0):
                                        builder.add(InlineKeyboardButton(text=f"{usable[i][1].utf8_icon} ({usable[i][0].quantity})",
                                                callback_data=BattleCF(action="heal",
                                                                item_index= i,
                                                                user_id=user.tg_id).pack()))
        builder.adjust(3) 
        return builder.as_markup()
    
    def __parts_selector(self, user:User, ctrl:BattleController) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        phase_icon:str = '🗡' if ctrl.active_member.stand == MemberStand.ATTACK else '🛡'
        action:str = "attack" if ctrl.active_member.stand == MemberStand.ATTACK else "defense"
        
        builder.add(InlineKeyboardButton(text=f"{phase_icon} Кабина",
                callback_data=BattleCF(action=action, part=BodyParts.HEAD.value,
                                       user_id=user.tg_id).pack()))
        
        builder.add(InlineKeyboardButton(text=f"{phase_icon} Туз",
                callback_data=BattleCF(action=action, part=BodyParts.CHEST.value,
                                       user_id=user.tg_id).pack()))
        
        builder.add(InlineKeyboardButton(text=f"{phase_icon} Костыли",
                callback_data=BattleCF(action=action, part=BodyParts.KNEES.value,
                                       user_id=user.tg_id).pack()))

        builder.adjust(3) 
        return builder.as_markup()
    
    def __gladiators_bets(self, user:User, ctrl:BattleController) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        for i in range(len(ctrl.members)):
            builder.add(InlineKeyboardButton(text=f"{ctrl.members[i].utf8_icon} 5💰",
            callback_data=GladiatorsCF(action="bet", gladiator_id=i,
                                        bet=5, user_id=user.tg_id).pack()))
            
            builder.add(InlineKeyboardButton(text=f"{ctrl.members[i].utf8_icon} 15💰",
            callback_data=GladiatorsCF(action="bet", gladiator_id=i,
                                        bet=15, user_id=user.tg_id).pack()))

        builder.adjust(2) 
        return builder.as_markup()
    
    def __gladiators_fight(self, user:User, ctrl:BattleController) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()


        builder.add(InlineKeyboardButton(text=random.choice(dict.gladiators_cheer_up) 
                                         if (ctrl.get_bet_gladiator().last_turn_result == AttackStatus.DEFENDED) 
                                         else random.choice(dict.gladiators_sucks),
                callback_data=GladiatorsCF(action="gladiators_fight",
                                           user_id=user.tg_id).pack()))

        builder.adjust(2) 
        return builder.as_markup()
