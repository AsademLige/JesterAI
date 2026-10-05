from features.battles.data.models.battle_orm import BattleORM
from features.battles.data.models.battle_dto import Battle
from features.user.data.dtos.user_dto import User
from core.utils.app_herald import AppHerald
from sqlalchemy import and_, desc, func
from core.consts.config import Prefs
from typing import Optional
import logging
import json
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
        """Дописать лог, не трогая статус."""
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