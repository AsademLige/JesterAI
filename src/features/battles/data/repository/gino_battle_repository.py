from features.battles.data.models.battle_orm import BattleORM
from features.battles.data.models.battle_dto import Battle
from features.user.data.dtos.user_dto import User
from core.utils.app_herald import AppHerald
from sqlalchemy import and_, desc, func
from core.consts.config import Prefs
from typing import Optional
import logging
import time


class GinoBattleRepository:
    _instance = None
    prefs = Prefs()
    logger:AppHerald = AppHerald()
    
    def __new__(cls):
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
    
    async def new_battle(self, user:User, battle_data:dict) -> bool:
        try:
            battle = BattleORM(user_id = user.tg_id,
                             started_timestamp = int(time.time()),
                             status = "prepared",
                             log = [],
                             data = battle_data)
            await battle.create()

            return True
        except Exception as error:
            self.logger.send_log("battle_repo", logging.ERROR, f"battle start error: {error}")
            return False

    async def get_battle(self, user:User, started:bool = False) -> Optional[Battle]:
        try:
            started_search = BattleORM.status != "none" if (started) else BattleORM.status != "started"
            battle_db:Optional[BattleORM] = await BattleORM.query.where(
                and_(
                   BattleORM.user_id == user.tg_id,
                   BattleORM.status != "end",
                   started_search,
                )).order_by(desc(BattleORM.id)).gino.first()
            battle = Battle.model_validate(battle_db)
            return battle
        except Exception as error:
            self.logger.send_log("battle_repo", logging.ERROR, f"battle get error: {error}")
            return None

    async def get_battle_by_id(self, battle_id:int) -> Optional[Battle]:
        try:
            battle_db:Optional[BattleORM] = await BattleORM.query.where(
                and_(
                    BattleORM.id == battle_id,
                )).gino.first()
            battle = Battle.model_validate(battle_db)
            return battle
        except Exception as error:
            self.logger.send_log("battle_repo", logging.ERROR, f"battle get error: {error}")
            return None

    async def update_log(self, battle_id: int, log: list) -> bool:
        try:
            battle = await BattleORM.get(battle_id)
            if not battle:
                return False
            await battle.update(log=log, status="started").apply()
            return True
        except Exception as error:
            self.logger.send_log(
                "battle_repo", logging.ERROR, f"update_log error: {error}"
            )
            return False

    async def update_battle(
        self,
        battle_id: int,
        status: Optional[str] = None,
        data: Optional[dict] = None,
        log: Optional[list] = None,
        validation: Optional[dict] = None,
    ) -> bool:
        try:
            battle = await BattleORM.get(battle_id)
            if not battle:
                return False

            values = {}
            if status is not None:
                values["status"] = status
            if data is not None:
                values["data"] = data
            if log is not None:
                values["log"] = log
            if validation is not None:
                values["validation"] = validation

            if values:
                await battle.update(**values).apply()
            return True
        except Exception as error:
            self.logger.send_log(
                "battle_repo", logging.ERROR, f"update_battle error: {error}"
            )
            return False

    async def get_week_fishing_stats(self, since_timestamp: int) -> dict:
        """Статистика рыбалки с момента since_timestamp (unix time) среди всех игроков.
        Возвращает {'best': {'tg_id', 'fish_name', 'weight_kg'} | None, 'total_weight': float},
        где best — самая тяжёлая пойманная рыба, total_weight — суммарный вес всего улова."""
        try:
            rows = await BattleORM.query.where(
                and_(
                    BattleORM.status == "end",
                    BattleORM.started_timestamp >= since_timestamp,
                )
            ).gino.all()

            best: Optional[dict] = None
            total_weight: float = 0.0
            for battle in rows:
                data = battle.data if isinstance(battle.data, dict) else {}
                if data.get("game_mode") != "fishing":
                    continue

                validation = battle.validation if isinstance(battle.validation, dict) else {}
                if validation.get("result") != "caught":
                    continue

                weight = data.get("fish_weight_kg")
                if not weight:
                    continue

                weight = float(weight)
                total_weight += weight
                if best is None or weight > best["weight_kg"]:
                    best = {
                        "tg_id": battle.user_id,
                        "fish_name": data.get("fish_name", "Рыба"),
                        "weight_kg": weight,
                    }

            return {"best": best, "total_weight": total_weight}
        except Exception as error:
            self.logger.send_log("battle_repo", logging.ERROR, f"get_week_fishing_stats error: {error}")
            return {"best": None, "total_weight": 0.0}

    async def get_week_monster_kills(self, since_timestamp: int) -> dict:
        """Статистика охоты с момента since_timestamp (unix time) среди всех игроков.
        Учитываются только победные бои с монстрами (режимы fishing/gladiators исключаются).
        Возвращает {'total_kills': int, 'top': {'tg_id', 'kills'} | None, 'monster_names': [str]}."""
        try:
            rows = await BattleORM.query.where(
                and_(
                    BattleORM.status == "end",
                    BattleORM.started_timestamp >= since_timestamp,
                )
            ).gino.all()

            kills_by_user: dict = {}
            monster_names: list = []
            total_kills: int = 0
            for battle in rows:
                data = battle.data if isinstance(battle.data, dict) else {}
                if data.get("game_mode") in ("fishing", "gladiators"):
                    continue

                validation = battle.validation if isinstance(battle.validation, dict) else {}
                if not validation.get("valid") or validation.get("status") != "victory":
                    continue

                total_kills += 1
                kills_by_user[battle.user_id] = kills_by_user.get(battle.user_id, 0) + 1
                name = data.get("monster_name")
                if name:
                    monster_names.append(name)

            top: Optional[dict] = None
            if kills_by_user:
                top_id, top_kills = max(kills_by_user.items(), key=lambda kv: kv[1])
                top = {"tg_id": top_id, "kills": top_kills}

            return {"total_kills": total_kills, "top": top, "monster_names": monster_names}
        except Exception as error:
            self.logger.send_log("battle_repo", logging.ERROR, f"get_week_monster_kills error: {error}")
            return {"total_kills": 0, "top": None, "monster_names": []}