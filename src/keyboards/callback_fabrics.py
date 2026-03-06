from aiogram.filters.callback_data import CallbackData
from typing import Optional

class StickerSetCF(CallbackData, prefix="fab_sticker_set"):
    action: str
    id: Optional[int] = None

class JobsCF(CallbackData, prefix="fab_jobs"):
    action: str
    job_id: Optional[str] = None

class DiceGameCF(CallbackData, prefix="fab_dice_game"):
    action: str

class InventoryCF(CallbackData, prefix="fab_combat"):
    action: str
    item_id: Optional[int] = None
    user_id: Optional[int] = None

class CombatCF(CallbackData, prefix="fab_combat"):
    action: str
    user_id: Optional[int] = None

class StoreCF(CallbackData, prefix="fab_store"):
    action: str
    id: Optional[int] = None
