from features.game_engine.data.repository.bot_settings_repository import IBotSettingsRepository
from features.game_engine.data.models.bot_settings_dto import BotSettings
from typing import Any, Dict
from pathlib import Path

class LocalBotSettingsRepository(IBotSettingsRepository):
    def __init__(self, snapshot_dir: str = ""):
        self.snapshot_dir = Path(snapshot_dir)
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)

        self._next_id = self.get_max_id() + 1

    def get_max_id(self) -> int:
        """Вспомогательный метод для определения максимального ID среди файлов"""
        ids = []
        for file in self.snapshot_dir.glob("*.json"):
            try:
                ids.append(int(file.stem))
            except ValueError:
                continue
        return max(ids) if ids else 0
    
    def _save_settings_file(self, settings: BotSettings) -> None:
        file_path = self.snapshot_dir / f"{settings.id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(settings.model_dump_json(indent=4))
    
    async def get_settings(self, chat_id:int, chat_full_name:str = "Unnamed") -> BotSettings:
        file_path = self.snapshot_dir / f"{id}.json"
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                return BotSettings.model_validate_json(f.read())
            
        new_settings = BotSettings(
            id=self._next_id,
            chat_id=chat_id,
            alias = chat_full_name,
            max_users_energy = 10
        )
        self._save_settings_file(new_settings)
        self._next_id += 1

        return new_settings
        
    async def update_settings_by_chat_id(self, chat_id:int, args:Dict[str, Any] = {}) -> bool:
        pass