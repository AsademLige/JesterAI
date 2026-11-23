from typing import Optional
from pydantic import BaseModel


class BestiaryKind():
    monster = "monster"
    fish = "fish"
    item = "item"

    all = (monster, fish, item)


class BestiaryEntry(BaseModel):
    kind: str
    entity_id: int
    title: str = ""
    utf8_icon: str = ""
    discovered: bool = False
    times: int = 0
    record_value: Optional[float] = None
