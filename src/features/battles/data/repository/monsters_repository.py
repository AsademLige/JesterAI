from features.battles.data.models.monster_dto import Monster
from abc import ABC, abstractmethod
from typing import Any, Dict, List


class IMonstersRepository(ABC):
    @abstractmethod
    async def get_random_monsters_by_tag(self, monster_count:int = 1, tag:str = "mob") -> List[Monster]:
        """Получить случайных монстров в заданном количестве"""
        pass
    
    @abstractmethod
    async def update_monster_status(self, monster_id:int, args:Dict[str, Any] = {}) -> bool:
        """"""
        pass