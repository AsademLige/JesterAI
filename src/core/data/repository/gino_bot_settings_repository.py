from core.data.repository.bot_settings_repository import IBotSettingsRepository
from core.data.models.bot_settings_orm import BotSettingsORM
from core.data.models.bot_settings_dto import BotSettings
from core.utils.app_herald import AppHerald
from typing import Any, Dict, Optional
from sqlalchemy import select


class GinoBotSettingsRepository(IBotSettingsRepository):
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def get_settings(self, chat_id:int, chat_full_name:str = "Unnamed") -> BotSettings:
        try:
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

            return settings
        except Exception as error:
            print(f"settings get error: {error}")
            return None
        
    async def update_settings_by_chat_id(self, chat_id:int, args:Dict[str, Any] = {}) -> bool:
        try:
            query = BotSettingsORM.update.values(**args).where(BotSettingsORM.chat_id == chat_id)
            await query.gino.status()
            return True
        except Exception as error:
            print(f"update settings error: {error}")
            return False