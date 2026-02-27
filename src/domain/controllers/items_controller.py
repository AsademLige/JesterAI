from datetime import datetime, timedelta

from src.domain.utils.utils import Utils
from src.models.user_inventory_item_model import UserInventoryItem
from src.domain.utils.text_processing import TextProcessing as tp
from src.models.store_item_model import StoreItem
from src.services.data_base.db import DataBase
from src.data.dictionary import Dictionary
from aiogram.utils.markdown import hcode
from src.models.user_model import User
from typing import Optional, Tuple
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
    effects = "effects"

class ItemsController():
    @staticmethod
    async def use_item(user: User, item: Tuple[UserInventoryItem, StoreItem], 
                       target:Optional[User] = None) -> Optional[str]:
        action = json.loads(item[1].action)
        effects = action[ItemActions.effects.name]
        user_link:str = dict.get_user_link(user.tg_name, user.tg_id)
        target_link:str = dict.get_user_link(user.tg_name, user.tg_id) if target else ""
        usage_result:str = ""

        if (ItemActions.subtract_length.name in effects and
            await ItemsController.length_change_effect(user, 
                                                       target if target else user, item, 
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
                                                       target if target else user, item, 
                                                       Utils.try_parse_int(effects[ItemActions.add_length.name]))):
            args = {"user_link1":user_link,
                    "user_link2":target_link,
                    "item_title":hcode(item[1].title),
                    "length": dict.length_wrapper(Utils.try_parse_int(effects[ItemActions.add_length.name])),
                    **dict.random_member()}
            message = dict.length_add_target if target else dict.length_add
            usage_result += f"{tp.text_replacement(message,args, recursive_parse_args=True)}\n"

        if (ItemActions.pencil_timer_decresc.name in effects and
            await ItemsController.reset_pencil_timer(user, target if target else user, item)):
            args = {"user_link1":user_link,
                        "user_link2":target_link,
                    "item_title":hcode(item[1].title),
                    **dict.random_member()}
            message = dict.pencil_timer_decresc_target if target else dict.pencil_timer_decresc
            usage_result += f"{tp.text_replacement(message,args, recursive_parse_args=True)}\n"

        if (ItemActions.dice_timer_decresc.name in effects and
            await ItemsController.reset_dice_game_timer(user, target if target else user, item)):
            args = {"user_link1":user_link,
                    "user_link2":target_link,
                    "item_title":hcode(item[1].title)}
            message = dict.dice_game_timer_decresc_target if target else dict.dice_game_timer_decresc
            usage_result += f"{tp.text_replacement(message,args, recursive_parse_args=True)}\n"
        
        return usage_result
    
    @staticmethod
    async def length_change_effect(user: User, target:User, item:UserInventoryItem, length_change:int) -> bool:
        print(f"cdlog {target.chat_id} {target.tg_id} {target.id}")
        if (await db.update_user(target, {
                User.length.name: User.length + length_change,
            }) and await db.update_item_in_user_inventory(user, item, -1)):

            return True
    
    @staticmethod
    async def reset_dice_game_timer(user: User, target:User, item:UserInventoryItem) -> bool:
        if (await db.update_user(target, {
                User.last_dice_play.name: datetime.now() - timedelta(hours=1)
            }) and await db.update_item_in_user_inventory(user, item, -1)):

            return True
        
    @staticmethod
    async def reset_pencil_timer(user: User, target:User, item:UserInventoryItem) -> bool:
        if (await db.update_user(target, {
                User.last_length_check.name: datetime.now() - timedelta(hours=24)
            }) and await db.update_item_in_user_inventory(user, item, -1)):

            return True