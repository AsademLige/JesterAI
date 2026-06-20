from typing import Optional

from pydantic import BaseModel, ConfigDict


class InventoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    product_id: int
    user_id: int
    quantity: int = 0

    price: Optional[int] = None
    title: Optional[str] = None
    tag: Optional[str] = None
    description: Optional[str] = None
    action: Optional[str] = None
    utf8_icon: Optional[str] = None