from pydantic import BaseModel, ConfigDict
from typing import Optional

class BaseItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    product_id: int
    price: int
    title: str
    tag: Optional[str] = None
    description: Optional[str] = None
    action: Optional[str] = None
    utf8_icon: Optional[str] = None