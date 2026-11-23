from features.bestiary.data.models.bestiary_dto import BestiaryEntry
from features.items.data.models.base_item_dto import BaseItem
from features.user.data.dtos.user_dto import User
from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class IBestiaryRepository(ABC):
    @abstractmethod
    async def register(self, user: User, kind: str, entity_id: Optional[int],
                       record_value: Optional[float] = None) -> bool:
        """Отметить встреченную сущность; идемпотентна к повторным вызовам."""
        pass

    @abstractmethod
    async def register_item(self, user: User, item: BaseItem,
                            record_value: Optional[float] = None) -> bool:
        """Отметить полученный предмет; рыба попадает в отдельный раздел."""
        pass

    @abstractmethod
    async def get_bestiary(self, user: User) -> Dict[str, List[BestiaryEntry]]:
        """Весь справочник по разделам с пометками об открытии."""
        pass
