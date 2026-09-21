from pydantic import BaseModel, ConfigDict, model_validator
from typing import Any, List
import json

class Battle(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    started_timestamp:int
    user_id: int
    status: str = "none"
    data: dict = {}
    log: List[Any] = []

    @model_validator(mode="before")
    @classmethod
    def parse_json_fields(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            for field_name in ["data", "log"]:
                raw_val = getattr(value, field_name, None)
                if isinstance(raw_val, str):
                    try:
                        setattr(value, field_name, json.loads(raw_val))
                    except json.JSONDecodeError:
                        default = [] if field_name == "log" else {}
                        setattr(value, field_name, default)
            return value

        for field_name in ["data", "log"]:
            if isinstance(value.get(field_name), str):
                try:
                    value[field_name] = json.loads(value[field_name])
                except json.JSONDecodeError:
                    value[field_name] = [] if field_name == "log" else {}

        return value