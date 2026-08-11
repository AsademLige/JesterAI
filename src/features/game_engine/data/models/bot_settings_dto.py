from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class BotSettings(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    chat_id: int
    last_captcha_time: Optional[datetime] = None
    max_users_energy:int

    ###Время восстановления энергии в секундах
    energy_restore_time:int = 10
    events_enabled:bool = True
    alias: str