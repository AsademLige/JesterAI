from features.store.data.models.discounts_model_orm import ProductDiscountORM
from features.store.data.models.warehouse_item_orm import WarehouseItemORM
from features.items.data.models.base_item_dto import BaseItem
from features.items.data.models.item_orm import ItemORM
from typing import Optional

class StoreItem(BaseItem):
    warehouse_quantity: Optional[int] = None
    max_capacity: Optional[int] = None
    
    discount_percent: int = 0
    is_discount_active: bool = False

    @property
    def final_price(self) -> int:
        if self.is_discount_active and self.discount_percent > 0:
            return int(self.price * (1 - self.discount_percent / 100))
        return self.price

    @classmethod
    def from_orm_objects(
        cls, 
        item: ItemORM, 
        warehouse: Optional[WarehouseItemORM] = None, 
        discount: Optional[ProductDiscountORM] = None
    ) -> "StoreItem":
        return cls(
            product_id=item.id,
            price=item.price,
            title=item.title,
            tag=item.tag,
            description=item.description,
            action=item.action,
            utf8_icon=item.utf8_icon,
            
            warehouse_quantity=warehouse.quantity if warehouse else None,
            max_capacity=warehouse.max_capacity if warehouse else None,
            
            discount_percent=discount.discount_percent if (discount and discount.is_active) else 0,
            is_discount_active=discount.is_active if discount else False
        )