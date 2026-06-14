from aiogram.filters.callback_data import CallbackData
from features.battles.battle_unit_entity import BodyParts
from typing import Optional


class StickerSetCF(CallbackData, prefix="fab_sticker_set"):
    action: str
    id: Optional[int] = None

class JobsCF(CallbackData, prefix="fab_jobs"):
    action: str
    job_id: Optional[str] = None

class DiceGameCF(CallbackData, prefix="fab_dice_game"):
    action: str
    user_id: Optional[int] = None

class GladiatorsCF(CallbackData, prefix="fab_gladiators"):
    action: str
    gladiator_id:Optional[int] = None
    bet:Optional[int] = None
    user_id: Optional[int] = None

class TrashLotoCF(CallbackData, prefix="fab_trash_loto"):
    action: str
    user_id: Optional[int] = None

class GambaChoiceCF(CallbackData, prefix="fab_gamba_choice"):
    action: str
    user_id: Optional[int] = None

class InventoryCF(CallbackData, prefix="fab_inventory"):
    action: str
    item_id: Optional[int] = None
    user_id: Optional[int] = None

class BattleCF(CallbackData, prefix="fab_battle"):
    action: str
    part: Optional[int] = None
    item_index: Optional[int] = None
    user_id: Optional[int] = None

class HelpCF(CallbackData, prefix="fab_help"):
    action: str

class StoreCF(CallbackData, prefix="fab_store"):
    action: str
    id: Optional[int] = None
