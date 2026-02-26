from aiogram.filters.callback_data import CallbackData
from typing import Optional

class StickerSetCF(CallbackData, prefix="fab_sticker_set"):
    action: str
    id: Optional[int] = None

class JobsCF(CallbackData, prefix="fab_jobs"):
    action: str
    job_id: Optional[str] = None

class DiceGameCF(CallbackData, prefix="dice_game"):
    action: str

class StoreCF(CallbackData, prefix="fab_store"):
    action: str
    id: Optional[int] = None
