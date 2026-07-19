from features.game_engine.data.repository.bot_settings_repository import IBotSettingsRepository
from features.game_engine.data.models.bot_settings_orm import BotSettingsORM
from features.game_engine.data.models.bot_settings_dto import BotSettings
from core.utils.app_herald import AppHerald
from typing import Any, Dict, Optional
from cachetools import TTLCache
from sqlalchemy import select
import logging


class GinoBotSettingsRepository(IBotSettingsRepository):
    _instance = None
    _cache:TTLCache

    logger:AppHerald = AppHerald()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._cache = TTLCache(maxsize=100, ttl=86400)
        return cls._instance
    
    def _add_to_cache(self, settings: BotSettings) -> None:
        self._cache[settings.chat_id] = settings
        self.logger.send_log("settings_repo", logging.INFO, f"cache update alias_{settings.alias}:chat_id_{settings.chat_id}")

    def _get_cache_settings(self, chat_id: int = None) -> Optional[BotSettings]:
        if chat_id in self._cache:
            return self._cache[chat_id]
        return None
    
    async def get_settings(self, chat_id:int, chat_full_name:str = "Unnamed") -> BotSettings:
        try:
            cache_settings = self._get_cache_settings(chat_id)
            if (cache_settings): return cache_settings

            query = select([BotSettingsORM.id]).select_from(BotSettingsORM).where(BotSettingsORM.chat_id == chat_id)
            settings_id = await query.gino.all()

            if (not settings_id):
                settings_db = BotSettingsORM(
                    chat_id=chat_id,
                    alias = chat_full_name
                )
                await settings_db.create()
            
            settings_db:Optional[BotSettingsORM] = await BotSettingsORM.query.where(BotSettingsORM.chat_id == chat_id).gino.first()
            settings = BotSettings.model_validate(settings_db)

            self._add_to_cache(settings)

            return settings
        except Exception as error:
            self.logger.send_log("settings_repo", logging.ERROR, f"settings get error: {error}")
            return None
        
    async def update_settings_by_chat_id(self, chat_id:int, args:Dict[str, Any] = {}) -> bool:
        try:
            query = BotSettingsORM.update.values(**args).where(BotSettingsORM.chat_id == chat_id)
            await query.gino.status()

            del self._cache[chat_id]

            return True
        except Exception as error:
            self.logger.send_log("settings_repo", logging.ERROR, f"update settings error: {error}")
            return False