from src.models.monster_model import Monster
from typing import List, Optional, Tuple
from src.models.item_model import Item
from enum import Enum
import random
import json

class DropTags(Enum):
    tags = "tags"
    common = "common"
    rare = "rare"
    epic = "epic"
    thief = "thief"
    none = "none"

class ItemDropManager():
    
    @staticmethod
    async def generate_drop(monster:Monster) -> Tuple[List[Item], int]:
        drop_items:List[Item] = []
        rules = json.loads(monster.drop_rules)

        total_weight:int = 0

        for tag in rules[DropTags.tags.name]:
            total_weight += rules[DropTags.tags.name][tag]

        roll = random.uniform(0, total_weight)

        print(f"cdlog total_weight {total_weight} : roll {roll}")

        current:int = 0
        for tag in rules[DropTags.tags.name]:
            current += rules[DropTags.tags.name][tag]
            if roll <= current:
                if (not DropTags[tag.lower()] == DropTags.none):
                    item:Optional[Item] = await ItemDropManager.get_item_by_tag(DropTags[tag.lower()])
                    print(f"cdlog drop: {tag} {rules[DropTags.tags.name][tag.lower()]} {item}")
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
        from src.services.data_base.db import DataBase
        db:DataBase = DataBase()
        return await db.get_random_item_by_tag(tag)


        
        