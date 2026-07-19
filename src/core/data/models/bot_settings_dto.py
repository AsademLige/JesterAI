from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class BotSettings(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    chat_id: int
    last_gladiators_bet: Optional[datetime] = None
    max_users_energy:int
    events_enabled:bool
    alias: str