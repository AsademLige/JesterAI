from pydantic import BaseModel, ConfigDict, computed_field
from typing import Any, List, Optional
import random
import json


def _pick_tier(tiers: List[dict]) -> Optional[dict]:
    """Выбирает тир случайным образом пропорционально шансам."""
    chances = [float(t.get("chance", 0)) for t in tiers]
    total = sum(chances)
    if total <= 0:
        return tiers[0] if tiers else None
    roll = random.uniform(0, total)
    acc = 0.0
    for tier, chance in zip(tiers, chances):
        acc += chance
        if roll <= acc:
            return tier
    return tiers[-1]


def _roll_from_tier(tier: dict) -> float:
    """Генерирует вес внутри тира. min == max даёт фиксированный вес (в т.ч. 0)."""
    lo = float(tier.get("min", 0))
    hi = float(tier.get("max", lo))
    if hi < lo:
        lo, hi = hi, lo
    return round(random.uniform(lo, hi), 2)


def roll_weight_from_config(weight_cfg: Any) -> Optional[float]:
    if weight_cfg is None or isinstance(weight_cfg, bool):
        return None
    if isinstance(weight_cfg, (int, float)):
        return round(float(weight_cfg), 2)
    if not isinstance(weight_cfg, list) or not weight_cfg:
        return None
    tier = _pick_tier(weight_cfg)
    if tier is None:
        return None
    return _roll_from_tier(tier)


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
    
    @computed_field
    @property
    def can_target(self) -> bool:
        if not self.action:
            return False
            
        try:
            action_json = json.loads(self.action)
            if isinstance(action_json, dict):
                return "can_target" in action_json and action_json["can_target"]
        except json.JSONDecodeError:
            pass
            
        return False

    def roll_weight(self) -> Optional[float]:
        if not self.action:
            return None
        try:
            action_json = json.loads(self.action)
        except json.JSONDecodeError:
            return None
        if not isinstance(action_json, dict):
            return None
        return roll_weight_from_config(action_json.get("weight"))
