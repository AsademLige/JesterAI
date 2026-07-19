from pydantic import BaseModel, ConfigDict

class Monster(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    health: int
    name: str
    description: str
    drop_rules: str
    utf8_icon: str
    tag: str
    fighting_style: str
    min_damage: int
    max_damage: int
    crit_chance: int