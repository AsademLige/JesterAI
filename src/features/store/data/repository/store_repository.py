from features.items.data.models.store_item_dto import StoreItem
from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod

from features.user.data.dtos.user_dto import User


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
    async def update_warehouse(self, out_of_stock_count:int = 0) -> List[StoreItem]:
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

    @abstractmethod
    async def create_purchase_transaction(self, item:StoreItem, user:User, quantity:int = 1) -> bool:
        """Сохранение в базу записи о транзакции пользователя"""
        pass

    @abstractmethod
    async def check_product_quantity_by_user(self, item:StoreItem, user:User) -> int:
        """Проверка остатков товара для конкретного пользователя"""
        pass