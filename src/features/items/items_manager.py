from features.user.data.repository.user_repository import IUserRepository
from features.items.data.models.inventory_item_dto import InventoryItem
from core.utils.text_processing import TextProcessing as tp
from features.battles.battle_unit_entity import BattleUnit
from features.user.data.dtos.user_dto import User
from core.consts.dictionary import Dictionary
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from core.data.data_base import DataBase
from core.consts.config import Prefs
from core.utils.utils import Utils
from enum import Enum
import random
import json


class ItemActions(Enum):
    pencil_timer_decresc = "pencil_timer_decresc"
    dice_timer_decresc = "dice_timer_decresc"
    subtract_length = "subtract_length"
    steal_money = "steal_money"
    steal_item = "steal_item"
    add_length = "add_length"
    mark_user = "mark_user"
    effects = "effects"
    heal = "heal"

class ItemsManager():
    user_repo:IUserRepository
    customer:User
    
    def __init__(self, user_repo:IUserRepository):
        self.user_repo = user_repo
        self.db = DataBase()
        self.dict = Dictionary()
        self.prefs = Prefs()

    async def use_item(self, user: User, item: InventoryItem, 
                       target:Optional[User] = None) -> Optional[str]:
        action = json.loads(item.action)
        effects = action[ItemActions.effects.name]
        user_link:str = self.dict.get_user_link(user.tg_name, user.tg_id)
        target_link:str = self.dict.get_user_link(target.tg_name, target.tg_id) if target else ""
        usage_result:str = ""

        if (ItemActions.subtract_length.name in effects and
            await self.length_change_effect(user, 
                                                       target if target else user, item, 
                                                       Utils.try_parse_int(effects[ItemActions.subtract_length.name]))):
                args = {"user_link1":user_link,
                        "user_link2":target_link,
                        "item_title":f"<code>{item.title}</code>",
                        "length": self.dict.length_wrapper(Utils.try_parse_int(effects[ItemActions.subtract_length.name])),
                        **self.dict.random_member()}
                message = self.dict.length_decresc_target if target else self.dict.length_decresc
                usage_result += f"{tp.text_replacement(message,args, recursive_parse_args=True)}\n"
            
        if (ItemActions.add_length.name in effects and
            await self.length_change_effect(user, 
                                            target if target else user, item, 
                                            Utils.try_parse_int(effects[ItemActions.add_length.name]))):
            args = {"user_link1":user_link,
                    "user_link2":target_link,
                    "item_title":f"<code>{item.title}</code>",
                    "length": self.dict.length_wrapper(Utils.try_parse_int(effects[ItemActions.add_length.name])),
                    **self.dict.random_member()}
            message = self.dict.length_add_target if target else self.dict.length_add
            usage_result += f"{tp.text_replacement(message,args, recursive_parse_args=True)}\n"

        if (ItemActions.pencil_timer_decresc.name in effects and
            await self.reset_pencil_timer(user, target if target else user, item)):
            args = {"user_link1":user_link,
                        "user_link2":target_link,
                    "item_title":f"<code>{item.title}</code>",
                    **self.dict.random_member()}
            message = self.dict.pencil_timer_decresc_target if target else self.dict.pencil_timer_decresc
            usage_result += f"{tp.text_replacement(message,args, recursive_parse_args=True)}\n"

        if (ItemActions.dice_timer_decresc.name in effects and
            await self.reset_dice_game_timer(user, target if target else user, item)):
            args = {"user_link1":user_link,
                    "user_link2":target_link,
                    "item_title":f"<code>{item.title}</code>"}
            message = self.dict.dice_game_timer_decresc_target if target else self.dict.dice_game_timer_decresc
            usage_result += f"{tp.text_replacement(message,args, recursive_parse_args=True)}\n"

        if (ItemActions.steal_item.name in effects):
            steal_item = await self.steal_item(user, target, item)
            if (steal_item):
                args = {"user_link1":user_link,
                    "user_link2":target_link,
                    "item_title":f"<code>{item.title}</code>",
                    "steal_item_title": f"<code>{item.title}</code>"}
                usage_result += f"{tp.text_replacement(self.dict.item_steal_usage, args, recursive_parse_args=True)}\n"
            else:
                usage_result += f"🐀 Попытка кражи не удалась, {user_link} оказался нищуком!\n"

        if (ItemActions.steal_money.name in effects):
            steal_count = Utils.try_parse_int(effects[ItemActions.steal_money.name])
            if (await self.steal_money(user, target, item,steal_count)):
                args = {"user_link1":user_link,
                    "user_link2":target_link,
                    "item_title":f"<code>{item.title}</code>",
                    "money": self.dict.money_wrapper(steal_count)}
                usage_result += f"{tp.text_replacement(self.dict.item_steal_money, args, recursive_parse_args=True)}\n"
            else:
                usage_result += f"🐀 Попытка кражи не удалась, {target_link} оказался нищуком!\n"

        if (ItemActions.mark_user.name in effects):
            from apps.tg_bot.handlers.interactive import marked_users
            marked_users[target.tg_id if target else user.tg_id] = (datetime.now(), datetime.now())
            await self.user_repo.user_item_transaction(user, item, -1)
            usage_result += f"🦠 {user_link} вешает метку на {target_link if target_link else user_link}"
        
        return usage_result
        
    
    def is_heal_item(self, item:InventoryItem) -> bool:
        #TODO:Перенести в модель
        action = json.loads(item.action)
        effects = action[ItemActions.effects.name]
        return ItemActions.heal.name in effects
    
    def is_steal_item(self, item:InventoryItem) -> bool:
        #TODO:Перенести в модель
        action = json.loads(item.action)
        effects = action[ItemActions.effects.name]
        return ItemActions.steal_item.name in effects or\
                ItemActions.steal_money.name in effects

    async def use_heal_item(self, user: User, item: InventoryItem, 
                       target:BattleUnit) -> Optional[Tuple[str, int]]:
        action = json.loads(item.action)
        effects = action[ItemActions.effects.name]
        usage_result:str = ""

        if (item.quantity > 0 and ItemActions.heal.name in effects and
            await self.heal_effect(user, target, item, effects[ItemActions.heal.name])):
            usage_result += f'💊 Предмет <code>"{item.title}"</code> восстановил вам <b>{effects[ItemActions.heal.name]}HP</b>'

        if (usage_result):
            return (usage_result, effects[ItemActions.heal.name])
        else:
            return None
        
    def effects_description(self, item:InventoryItem) -> str: 
        #TODO:Перенести в модель
        action = json.loads(item.action)
        effects = action[ItemActions.effects.name]
        description:str = f"<code>{item.title} - </code>"
        if (ItemActions.heal.name in effects):
            description += f"Лечение: <b>{effects[ItemActions.heal.name]}HP</b>"
        
        return description

    
    async def length_change_effect(self, user: User, target:User, item:InventoryItem, length_change:int) -> bool:
        if (await self.user_repo.update(target, length=user.length + length_change) 
            and await self.user_repo.user_item_transaction(user, item, -1)):
            return True
    
    async def reset_dice_game_timer(self, user: User, target:User, item:InventoryItem) -> bool:
        if (await self.user_repo.update(target, last_dice_play=datetime.now() - timedelta(hours=1)) 
            and await self.user_repo.user_item_transaction(user, item, -1)):
            return True
        
    async def reset_pencil_timer(self, user: User, target:User, item:InventoryItem) -> bool:
        if (await self.user_repo.update(target, last_length_check=datetime.now() - timedelta(hours=24)) 
            and await self.user_repo.user_item_transaction(user, item, -1)):
            return True
        
    async def heal_effect(self, user: User, target:BattleUnit, item:InventoryItem, hp:int = 0) -> bool:
        if (await self.user_repo.user_item_transaction(user, item, -1)):
            target.heal(hp)
            return True

    async def steal_item(self, user: User, target:User, item:InventoryItem) -> Optional[InventoryItem]:
        if (target.inventory):
            steal_item:InventoryItem = random.choice(target.inventory)
            if (await self.user_repo.user_item_transaction(user, steal_item) and 
                await self.user_repo.user_item_transaction(target, steal_item, -1) and
                await self.user_repo.user_item_transaction(user, item, -1)):
                return steal_item
        else:
            return None
        
    async def steal_money(self, user: User, target:User, item:InventoryItem, count:int) -> bool:
        if (target.money >= count):
            if (await self.user_repo.update(target, money=target.money - count) and
                await self.user_repo.update(user, money=user.money + count)  and 
                await self.user_repo.user_item_transaction(user, item, -1)):
                return True
        else:
            return False
            