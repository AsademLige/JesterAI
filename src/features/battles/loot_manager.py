from features.battles.data.models.monster_orm import MonsterORM
from features.items.data.models.item_orm import ItemORM
from core.utils.app_herald import AppHerald
from typing import List, Optional, Tuple
from enum import Enum
import logging
import random
import json

class DropTags(Enum):
    tags = "tags"
    common = "common"
    rare = "rare"
    epic = "epic"
    thief = "thief"
    none = "none"

class LootManager():
    
    @staticmethod
    async def generate_drop(monster:MonsterORM) -> Tuple[List[ItemORM], int]:
        logger:AppHerald = AppHerald()

        drop_items:List[ItemORM] = []
        rules = json.loads(monster.drop_rules)

        total_weight:int = 0

        for tag in rules[DropTags.tags.name]:
            total_weight += rules[DropTags.tags.name][tag]

        roll = random.uniform(0, total_weight)

        logger.send_log("battle", logging.INFO, 
                        f"total_weight {total_weight} : roll {roll}")

        current:int = 0
        for tag in rules[DropTags.tags.name]:
            current += rules[DropTags.tags.name][tag]
            if roll <= current:
                if (not DropTags[tag.lower()] == DropTags.none):
                    item:Optional[ItemORM] = await LootManager.get_item_by_tag(DropTags[tag.lower()])
                    logger.send_log("battle", logging.INFO, 
                                    f"drop: {tag} {rules[DropTags.tags.name][tag.lower()]} {item}")
                    if (item): drop_items.append(item)
                break

        money_drop = 0
        if (monster.tag == "mob"):
            money_drop = random.randint(5, 15)
        elif (monster.tag == "boss"):
            money_drop = random.randint(15, 30)

        return (drop_items, money_drop)
    
    @staticmethod
    async def get_item_by_tag(tag:DropTags):
        from core.data.data_base import DataBase
        db:DataBase = DataBase()
        return await db.get_random_item_by_tag(tag)


        
        