from features.battles.data.repository.monsters_repository import IMonstersRepository
from features.battles.data.models.monster_stats_orm import MonsterStatsORM
from features.battles.data.models.monster_orm import MonsterORM
from features.battles.data.models.monster_dto import Monster
from core.utils.app_herald import AppHerald
from core.consts.config import Prefs
from typing import Any, Dict, List, Optional
from sqlalchemy import func
import logging

class GinoMonstersRepository(IMonstersRepository):
    _instance = None
    prefs = Prefs()

    logger:AppHerald = AppHerald()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def get_random_monsters_by_tag(self, monster_count:int = 1, tag:str = "mob") -> Optional[List[Monster]]:
        try:
            random_monster:List[Monster] = []
            db_monsters:List[MonsterORM] = await MonsterORM.query.order_by(func.random()).\
                                where(MonsterORM.tag.ilike(f"%{tag}%")).limit(monster_count).gino.all()
            for monster_db in db_monsters:
                random_monster.append(Monster.model_validate(monster_db))

            return random_monster
        except Exception as error:
            self.logger.send_log("monsters_repo", logging.ERROR, f"get monsters error: {error}")
            return None
        
    async def update_monster_status(self, monster_id:int, args:Dict[str, Any] = {}) -> bool:
        try:
            monster_stats:Optional[MonsterStatsORM] = await MonsterStatsORM.query.\
                            where(MonsterStatsORM.monster_id == monster_id).gino.first()
            if (not monster_stats):
                monster_stats = MonsterStatsORM(monster_id = monster_id)
                await monster_stats.create()
            await monster_stats.update(**args).apply()
            return True
        except Exception as error: 
            print(f"monster stats update error: {error}")
            return False