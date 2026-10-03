from pydantic import BaseModel, ConfigDict
from typing import Any

class Battle(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    started_timestamp: int
    user_id: int

    status: str = "none"
    data: dict[str, Any] = {}
    validation: dict[str, Any] = {}
    log: list[Any] = []