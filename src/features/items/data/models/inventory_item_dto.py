from features.user.data.models.user_inventory_link_orm import UserInventoryLinkORM
from features.items.data.models.base_item_dto import BaseItem
from features.items.data.models.item_orm import ItemORM


class InventoryItem(BaseItem):
    user_id: int
    quantity: int = 0

    @classmethod
    def from_orm(cls, user_id: int, item: ItemORM, link: UserInventoryLinkORM) -> "InventoryItem":
        return cls(
            product_id=item.id,
            price=item.price,
            title=item.title,
            tag=item.tag,
            description=item.description,
            action=item.action,
            utf8_icon=item.utf8_icon,
            user_id=user_id,
            quantity=link.quantity if link else 0
        )