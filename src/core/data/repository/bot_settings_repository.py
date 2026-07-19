from typing import Any, Dict

from core.data.models.bot_settings_dto import BotSettings
from abc import ABC, abstractmethod



class IBotSettingsRepository(ABC):
    @abstractmethod
    async def get_settings(chat_id:int, chat_full_name:str) -> BotSettings:
        """Получить глобальные настройки для чата по его названию и идентификатору"""
        pass
    
    @abstractmethod
    async def update_settings_by_chat_id(self, chat_id:int, args:Dict[str, Any] = {}) -> bool:
        """Обновить глобальные настройки для чата"""
        pass