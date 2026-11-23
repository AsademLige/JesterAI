from features.bestiary.data.repository.bestiary_repository import IBestiaryRepository
from features.bestiary.data.models.bestiary_dto import BestiaryEntry, BestiaryKind
from features.bestiary.data.models.bestiary_orm import BestiaryORM
from features.battles.data.models.monster_orm import MonsterORM
from features.items.data.models.base_item_dto import BaseItem
from features.items.data.models.item_orm import ItemORM
from features.battles.loot_manager import DropTags
from features.user.data.dtos.user_dto import User
from core.utils.app_herald import AppHerald
from sqlalchemy import and_
from typing import Dict, List, Optional
import logging
import time


def parse_entity_id(value) -> Optional[int]:
    """Id из JSON-данных боя приходит строкой и бывает служебным («default»).
    Ноль допустим: в справочнике монстров есть запись с id = 0."""
    try:
        entity_id = int(value)
    except (TypeError, ValueError):
        return None
    return entity_id if entity_id >= 0 else None


class GinoBestiaryRepository(IBestiaryRepository):
    _instance = None
    logger: AppHerald = AppHerald()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def register(self, user: User, kind: str, entity_id: Optional[int],
                       record_value: Optional[float] = None) -> bool:
        entity_id = parse_entity_id(entity_id)
        if not user or entity_id is None:
            return False

        timestamp = int(time.time())
        try:
            entry: Optional[BestiaryORM] = await BestiaryORM.query.where(and_(
                BestiaryORM.user_id == user.id,
                BestiaryORM.kind == kind,
                BestiaryORM.entity_id == entity_id,
            )).gino.first()

            if entry:
                values = {"times": (entry.times or 0) + 1, "last_seen_at": timestamp}
                if record_value is not None and (entry.record_value is None
                                                 or record_value > entry.record_value):
                    values["record_value"] = record_value
                await entry.update(**values).apply()
                return True

            await BestiaryORM(user_id=user.id, kind=kind, entity_id=entity_id,
                              times=1, record_value=record_value,
                              first_seen_at=timestamp, last_seen_at=timestamp).create()
            return True
        except Exception as error:
            self.logger.send_log("bestiary_repo", logging.ERROR, f"register error: {error}")
            return False

    async def register_item(self, user: User, item: BaseItem,
                            record_value: Optional[float] = None) -> bool:
        if not item:
            return False
        kind = BestiaryKind.fish if item.tag == DropTags.fish.value else BestiaryKind.item
        return await self.register(user, kind, item.id, record_value)

    async def get_bestiary(self, user: User) -> Dict[str, List[BestiaryEntry]]:
        try:
            found = {kind: {} for kind in BestiaryKind.all}
            rows: List[BestiaryORM] = await BestiaryORM.query.where(
                BestiaryORM.user_id == user.id).gino.all()
            for row in rows:
                if row.kind in found:
                    found[row.kind][row.entity_id] = row

            monsters: List[MonsterORM] = await MonsterORM.query.order_by(MonsterORM.id).gino.all()
            items: List[ItemORM] = await ItemORM.query.order_by(ItemORM.id).gino.all()

            result: Dict[str, List[BestiaryEntry]] = {kind: [] for kind in BestiaryKind.all}
            for monster in monsters:
                result[BestiaryKind.monster].append(self.__merge(found[BestiaryKind.monster], BestiaryEntry(
                    kind=BestiaryKind.monster, entity_id=monster.id,
                    title=monster.name or "", utf8_icon=monster.utf8_icon or "")))

            for item in items:
                kind = BestiaryKind.fish if item.tag == DropTags.fish.value else BestiaryKind.item
                result[kind].append(self.__merge(found[kind], BestiaryEntry(
                    kind=kind, entity_id=item.id,
                    title=item.title or "", utf8_icon=item.utf8_icon or "")))

            return result
        except Exception as error:
            self.logger.send_log("bestiary_repo", logging.ERROR, f"get bestiary error: {error}")
            return {kind: [] for kind in BestiaryKind.all}

    @staticmethod
    def __merge(found: Dict[int, BestiaryORM], entry: BestiaryEntry) -> BestiaryEntry:
        row = found.get(entry.entity_id)
        if not row:
            return entry
        entry.discovered = True
        entry.times = row.times or 0
        entry.record_value = row.record_value
        return entry
