from aiogram.filters.callback_data import CallbackData
from typing import Optional

class StickerSetCF(CallbackData, prefix="fab_sticker_set"):
    action: str
    short_name: Optional[str] = None
