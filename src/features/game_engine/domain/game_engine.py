from features.game_engine.data.repository.bot_settings_repository import IBotSettingsRepository
from features.game_engine.data.models.bot_settings_dto import BotSettings
from features.user.data.repository.user_repository import IUserRepository
from core.providers.notification_provider import INotificationProvider
from features.user.data.dtos.user_dto import User
from datetime import datetime, timedelta
from typing import List, Optional
import asyncio

class GameEngine:
    def __init__(self, settings_repo: IBotSettingsRepository, 
                 user_repo:IUserRepository,
                 notification_provider:INotificationProvider):
        self._next_energy_restore: dict[int, datetime] = {}
        self.notification_provider = notification_provider
        self.settings_repo = settings_repo
        self.user_repo = user_repo
        self._is_running = False

    async def start(self):
        self._is_running = True

        users:List[User] = await self.user_repo.get_users()
        for user in users:
            settings:BotSettings = await self.settings_repo.get_settings(user.chat_id)
            if (user.energy < settings.max_users_energy):
                self.create_energy_restore_timer(user)
        
        asyncio.create_task(self._main_loop())

    async def stop(self):
        self._is_running = False

    async def _main_loop(self):
        while self._is_running:
            await self._update_energy()
            await asyncio.sleep(5) 

    async def _update_energy(self):
        """Логика проверки и восстановления энергии"""
        for user_id in list(self._next_energy_restore.keys()):
            if datetime.now() >= self._next_energy_restore[user_id]:
                user:User = await self.user_repo.get_user(id=user_id)
                settings:BotSettings = await self.settings_repo.get_settings(user.chat_id)

                await self.user_repo.update(user, energy=user.energy+1)
                
                if (user.energy < settings.max_users_energy):
                    self._next_energy_restore[user_id] = datetime.now() + timedelta(minutes=2)
                else:
                    await self.notification_provider.notifivcate(user.tg_id, "⚡️ Бачок энергии заполнен до отказа!")
                    del self._next_energy_restore[user_id]

    def get_energy_restore_time(self, user:User) -> Optional[datetime]:
        return self._next_energy_restore[user.id] if user.id in self._next_energy_restore else None

    def create_energy_restore_timer(self, user:User):
        self._next_energy_restore[user.id] = datetime.now() + timedelta(minutes=2)