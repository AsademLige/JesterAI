from pydantic import BaseModel, ConfigDict, computed_field
from typing import Optional
import json

class BaseItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    price: int
    title: str
    tag: Optional[str] = None
    description: Optional[str] = None
    action: Optional[str] = None
    utf8_icon: Optional[str] = None

    @computed_field
    @property
    def usable(self) -> bool:
        if not self.action:
            return False
            
        try:
            action_json = json.loads(self.action)
            if isinstance(action_json, dict):
                return "usable" in action_json and action_json["usable"]
        except json.JSONDecodeError:
            pass
            
        return False