from features.items.data.models.store_item_dto import StoreItem
from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod


class IStoreRepository(ABC):
    @abstractmethod
    async def get_store_items_with_quantity(self) -> List[StoreItem]:
        """Получение списка всех доступных в магазине предметов"""
        pass
    
    @abstractmethod
    async def update_item_quantity_at_warehouse(self, item:StoreItem, quantity:int = 1) -> bool:
        """Обновление количества доступных единиц предмета на складе"""
        pass
    
    @abstractmethod
    async def update_warehouse(self) -> bool:
        """Обновление остатков магазина"""
        pass
    
    @abstractmethod
    async def deactivate_discounts(self) -> bool:
        """Удаление текущих скидок"""
        pass
    
    @abstractmethod
    async def create_random_discount(self, discounts_count:int = 1) -> List[StoreItem]:
        """Генерация случайных скидок"""
        pass