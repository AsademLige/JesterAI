from features.items.data.models.base_item_dto import BaseItem
from features.user.data.dtos.user_dto import User
from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod

class IUserRepository(ABC):
    @abstractmethod
    async def get_user(self, tg_id: Optional[int] = None, 
                       chat_id: Optional[int] = None,
                       id: Optional[int] = None,
                       last_daily_draw_winner: Optional[bool] = None) -> Optional[User]:
        """Формирование DTO модели пользователя на основе основных данных и данных статистики"""
        pass
    
    @abstractmethod
    async def get_users(self, chat_id: Optional[int] = None,
                        last_daily_draw_winner: Optional[bool] = None) -> List[User]: 
        """Формирование DTO модели массива пользователей на основе основных данных и данных статистики"""
        pass

    @abstractmethod
    async def add(self, tg_id: int, tg_name: str, length: int, custom_title: str, chat_id:int) -> None:
        """Добавить нового пользователя"""
        pass
    
    @abstractmethod
    async def update(self, user: User, args:Dict[str, Any] = {}) -> bool:
        """Обновление данных пользователя/бота"""
        pass

    @abstractmethod
    async def get_place_in_top_by_member(self, tg_id:int, chat_id:int) -> int:
        """Возвращает порядковый номер в топе по размеру {{pencil}}"""
        pass

    @abstractmethod
    async def user_item_transaction(self, user:User, item:BaseItem, quantity:int = 1) -> bool:
        """Перемещение предмета в инвентарь пользователя/бота"""
        pass
    
    @abstractmethod
    async def change_reputation(self, source_id: str, target_id: str, delta: int) -> None:
        """Изменить репутацию (например, уменьшить при пакости)"""
        pass