from features.user.data.dtos.inventory_item_dto import InventoryItem
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import datetime

class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tg_id: int
    length: int
    is_bot: bool
    tg_name: Optional[str] = None
    utf8_icon: Optional[str] = None
    custom_title: Optional[str] = None
    chat_id: int
    money: int
    role_id: Optional[int] = None
    
    last_daily_draw_winner: Optional[bool] = None
    last_gladiators_bet: Optional[datetime] = None
    last_boss_hunt: Optional[datetime] = None
    last_length_check: Optional[datetime] = None
    last_dice_play: Optional[datetime] = None
    last_hunt: Optional[datetime] = None
    
    trash_loto_money_wins: int = 0
    trash_loto_spins: int = 0
    trash_loto_jackpots: int = 0
    trash_loto_length_wins: int = 0

    dice_games: int = 0
    dice_minor_wins: int = 0
    dice_major_wins: int = 0

    gladiators_bet_win: int = 0
    gladiators_bet: int = 0

    duels_count: int = 0
    duels_win_count: int = 0
    good_hunting_count: int = 0
    
    inventory: List[InventoryItem] = Field(default_factory=list)