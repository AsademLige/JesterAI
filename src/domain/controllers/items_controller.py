import random

from src.models.user_inventory_item_model import UserInventoryItem
from src.domain.utils.text_processing import TextProcessing as tp
from src.models.battle_member_model import BattleMember
from src.services.data_base.db import DataBase
from src.data.dictionary import Dictionary
from src.domain.utils.utils import Utils
from datetime import datetime, timedelta
from aiogram.utils.markdown import hcode
from src.models.user_model import User
from src.models.item_model import Item
from typing import List, Optional, Tuple
from src.data.config import Prefs
from random import Random
from aiogram import Bot
from enum import Enum
import json

db = DataBase()
dict = Dictionary()
prefs = Prefs()
bot = Bot(token=prefs.bot_token)

class ItemActions(Enum):
    pencil_timer_decresc = "pencil_timer_decresc"
    dice_timer_decresc = "dice_timer_decresc"
    subtract_length = "subtract_length"
    add_length = "add_length"
    heal = "heal"
    steal_item = "steal_item"
    steal_money = "steal_money"
    effects = "effects"

class ItemsController():
    @staticmethod
    async def use_item(user: User, item: Tuple[UserInventoryItem, Item], 
                       target:Optional[User] = None) -> Optional[str]:
        action = json.loads(item[1].action)
        effects = action[ItemActions.effects.name]
        user_link:str = dict.get_user_link(user.tg_name, user.tg_id)
        target_link:str = dict.get_user_link(target.tg_name, target.tg_id) if target else ""
        usage_result:str = ""

        if (ItemActions.subtract_length.name in effects and
            await ItemsController.length_change_effect(user, 
                                                       target if target else user, item[1], 
                                                       Utils.try_parse_int(effects[ItemActions.subtract_length.name]))):
                args = {"user_link1":user_link,
                        "user_link2":target_link,
                        "item_title":hcode(item[1].title),
                        "length": dict.length_wrapper(Utils.try_parse_int(effects[ItemActions.subtract_length.name])),
                        **dict.random_member()}
                message = dict.length_decresc_target if target else dict.length_decresc
                usage_result += f"{tp.text_replacement(message,args, recursive_parse_args=True)}\n"
            
        if (ItemActions.add_length.name in effects and
            await ItemsController.length_change_effect(user, 
                                                       target if target else user, item[1], 
                                                       Utils.try_parse_int(effects[ItemActions.add_length.name]))):
            args = {"user_link1":user_link,
                    "user_link2":target_link,
                    "item_title":hcode(item[1].title),
                    "length": dict.length_wrapper(Utils.try_parse_int(effects[ItemActions.add_length.name])),
                    **dict.random_member()}
            message = dict.length_add_target if target else dict.length_add
            usage_result += f"{tp.text_replacement(message,args, recursive_parse_args=True)}\n"

        if (ItemActions.pencil_timer_decresc.name in effects and
            await ItemsController.reset_pencil_timer(user, target if target else user, item[1])):
            args = {"user_link1":user_link,
                        "user_link2":target_link,
                    "item_title":hcode(item[1].title),
                    **dict.random_member()}
            message = dict.pencil_timer_decresc_target if target else dict.pencil_timer_decresc
            usage_result += f"{tp.text_replacement(message,args, recursive_parse_args=True)}\n"

        if (ItemActions.dice_timer_decresc.name in effects and
            await ItemsController.reset_dice_game_timer(user, target if target else user, item[1])):
            args = {"user_link1":user_link,
                    "user_link2":target_link,
                    "item_title":hcode(item[1].title)}
            message = dict.dice_game_timer_decresc_target if target else dict.dice_game_timer_decresc
            usage_result += f"{tp.text_replacement(message,args, recursive_parse_args=True)}\n"

        if (ItemActions.steal_item.name in effects):
            steal_item = await ItemsController.steal_item(user, target, item[1])
            if (steal_item):
                args = {"user_link1":user_link,
                    "user_link2":target_link,
                    "item_title":hcode(item[1].title),
                    "steal_item_title": hcode(steal_item.title)}
                usage_result += f"{tp.text_replacement(dict.item_steal_usage, args, recursive_parse_args=True)}\n"
            else:
                usage_result += f"🐀 Попытка кражи не удалась, {user_link} оказался нищуком!\n"

        if (ItemActions.steal_money.name in effects):
            steal_count = Utils.try_parse_int(effects[ItemActions.steal_money.name])
            if (await ItemsController.steal_money(user, target, item[1],steal_count)):
                args = {"user_link1":user_link,
                    "user_link2":target_link,
                    "item_title":hcode(item[1].title),
                    "money": dict.money_wrapper(steal_count)}
                usage_result += f"{tp.text_replacement(dict.item_steal_money, args, recursive_parse_args=True)}\n"
            else:
                usage_result += f"🐀 Попытка кражи не удалась, {user_link} оказался нищуком!\n"
        
        return usage_result
    
    @staticmethod
    def is_heal_item(item:Item) -> bool:
        #TODO:Перенести в модель
        action = json.loads(item.action)
        effects = action[ItemActions.effects.name]
        return ItemActions.heal.name in effects
    
    @staticmethod
    def is_steal_item(item:Item) -> bool:
        #TODO:Перенести в модель
        action = json.loads(item.action)
        effects = action[ItemActions.effects.name]
        return ItemActions.steal_item.name in effects or\
                ItemActions.steal_money.name in effects

    @staticmethod
    async def use_heal_item(user: User, item: Tuple[UserInventoryItem, Item], 
                       target:BattleMember) -> Optional[Tuple[str, int]]:
        action = json.loads(item[1].action)
        effects = action[ItemActions.effects.name]
        usage_result:str = ""

        if (item[0].quantity > 0 and ItemActions.heal.name in effects and
            await ItemsController.heal_effect(user, target, item[1], effects[ItemActions.heal.name])):
            usage_result += f'💊 Предмет <code>"{item[1].title}"</code> восстановил вам <b>{effects[ItemActions.heal.name]}HP</b>'

        if (usage_result):
            return (usage_result, effects[ItemActions.heal.name])
        else:
            return None
        
    @staticmethod
    def effects_description(item:Item) -> str: 
        #TODO:Перенести в модель
        action = json.loads(item.action)
        effects = action[ItemActions.effects.name]
        description:str = f"<code>{item.title} - </code>"
        if (ItemActions.heal.name in effects):
            description += f"Лечение: <b>{effects[ItemActions.heal.name]}HP</b>"
        
        return description

    
    @staticmethod
    async def length_change_effect(user: User, target:User, item:Item, length_change:int) -> bool:
        if (await db.update_user(target, {
                User.length.name: User.length + length_change,
            }) and await db.user_item_transaction(user, item, -1)):

            return True
    
    @staticmethod
    async def reset_dice_game_timer(user: User, target:User, item:Item) -> bool:
        if (await db.update_user(target, {
                User.last_dice_play.name: datetime.now() - timedelta(hours=1)
            }) and await db.user_item_transaction(user, item, -1)):

            return True
        
    @staticmethod
    async def reset_pencil_timer(user: User, target:User, item:Item) -> bool:
        if (await db.update_user(target, {
                User.last_length_check.name: datetime.now() - timedelta(hours=24)
            }) and await db.user_item_transaction(user, item, -1)):

            return True
        
    @staticmethod
    async def heal_effect(user: User, target:BattleMember, item:Item, hp:int = 0) -> bool:
        if (await db.user_item_transaction(user, item, -1)):
            target.heal(hp)
            return True

    @staticmethod
    async def steal_item(user: User, target:User, item:Item) -> Optional[Item]:
        target_inventory:List[Tuple[UserInventoryItem, Item]] = await db.get_user_inventory(target)
        if (target_inventory):
            steal_item:Tuple[UserInventoryItem, Item] = random.choice(target_inventory)
            if (await db.user_item_transaction(user, steal_item[1]) and 
                await db.user_item_transaction(target, steal_item[1], -1) and
                await db.user_item_transaction(user, item, -1)):
                return steal_item[1]
        else:
            return None
        
    @staticmethod
    async def steal_money(user: User, target:User, item:Item, count:int) -> bool:
        if (target.money >= count):
            if (await db.update_user(target, {
                    User.money.name: target.money - count
                })  and
                await db.update_user(user, {
                    User.money.name: user.money + count
                })  and 
                await db.user_item_transaction(user, item, -1)):
                return True
        else:
            return False
            