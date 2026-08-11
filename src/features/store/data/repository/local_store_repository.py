from features.store.data.repository.store_repository import IStoreRepository
from features.items.data.models.store_item_dto import StoreItem
from typing import List, Optional
from pathlib import Path

class LocalStoreRepository(IStoreRepository):
    def __init__(self, snapshot_dir: str = ""):
        self.snapshot_dir = Path(snapshot_dir)
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)

        self._next_id = self.get_max_id() + 1

    def get_max_id(self) -> int:
        """Вспомогательный метод для определения максимального ID среди файлов"""
        ids = []
        for file in self.snapshot_dir.glob("*.json"):
            try:
                ids.append(int(file.stem))
            except ValueError:
                continue
        return max(ids) if ids else 0

    async def get_store_items_with_quantity(self) -> Optional[List[StoreItem]]:
        pass
        
    async def update_item_quantity_at_warehouse(self, item:StoreItem, quantity:int = 1) -> bool:
        pass
        
    async def create_random_discount(self, discounts_count:int = 1) -> Optional[List[StoreItem]]:
        pass

    async def update_warehouse(self) -> bool:
        pass
    
    async def deactivate_discounts(self) -> bool:
        pass