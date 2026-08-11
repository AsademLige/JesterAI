from features.user.data.repository.user_repository import IUserRepository
from features.items.data.models.inventory_item_dto import InventoryItem
from features.items.data.models.base_item_dto import BaseItem
from features.items.data.models.item_orm import ItemORM
from features.battles.loot_manager import DropTags
from features.user.data.dtos.user_dto import User
from typing import Any, List, Optional
from cachetools import TTLCache
from pathlib import Path
import datetime
import os

class LocalUserRepository(IUserRepository):
    def __init__(self, snapshot_dir: str = ""):
        self.snapshot_dir = Path(snapshot_dir)
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
        self._cache = TTLCache(maxsize=100, ttl=86400)
        self._tg_id_map = TTLCache(maxsize=100, ttl=86400)
        self._chat_tg_map = TTLCache(maxsize=100, ttl=86400)

        self._next_id = self.get_max_id() + 1

    def _add_to_cache(self, user: User) -> None:
        self._cache[user.id] = user
        self._tg_id_map[user.tg_id] = user.id
        self._chat_tg_map[(user.chat_id, user.tg_id)] = user.id

    def _get_cache_user(self, tg_id: Optional[int] = None, 
                           id: Optional[int] = None, 
                           chat_id: Optional[int] = None) -> Optional[User]:
        if id is not None and id in self._cache:
            return self._cache[id]

        if chat_id is not None and tg_id is not None:
            cache_key = (chat_id, tg_id)
            if cache_key in self._chat_tg_map:
                user_id = self._chat_tg_map[cache_key]
                if user_id in self._cache:
                    return self._cache[user_id]
        
        return None
    
    def clear_cache(self):
        self._cache.clear()
        self._chat_tg_map.clear()
        self._tg_id_map.clear()

    def save_cache(self):
        for user in list(self._cache.values()):
            self._save_user_file(user)

    def get_max_id(self) -> int:
        """Вспомогательный метод для определения максимального ID среди файлов"""
        ids = []
        for file in self.snapshot_dir.glob("*.json"):
            try:
                ids.append(int(file.stem))
            except ValueError:
                continue
        return max(ids) if ids else 0

    def _load_all_users(self) -> List[User]:
        """Вспомогательный метод для загрузки всех сохраненных юзеров из файлов"""
        users = []
        json_files_count = sum(1 for _ in self.snapshot_dir.glob("*.json"))

        if (len(self._cache) == json_files_count):
            return list(self._cache.values())

        for file_path in self.snapshot_dir.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    user_data = f.read()
                    if user_data.strip():
                        user:User = User.model_validate_json(user_data)
                        self._add_to_cache(user)
                        users.append(user)
            except Exception as e:
                print(f"[Warning] Ошибка загрузки снапшота {file_path}: {e}")
                continue
        return users

    def _save_user_file(self, user: User) -> None:
        file_path = self.snapshot_dir / f"{user.id}.json"
        
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(user.model_dump_json(indent=4))
            f.flush()
            os.fsync(f.fileno())

    async def get_user(self, tg_id: Optional[int] = None, 
                       chat_id: Optional[int] = None,
                       id: Optional[int] = None,
                       last_daily_draw_winner: Optional[bool] = None) -> Optional[User]:
        """Поиск пользователя по переданным фильтрам (логика AND)"""

        cache_user = self._get_cache_user(tg_id, id, chat_id)
        if (cache_user): return cache_user
        
        if id is not None:
            file_path = self.snapshot_dir / f"{id}.json"
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    return User.model_validate_json(f.read())
            return None

        all_users = self._load_all_users()
        for user in all_users:
            if tg_id is not None and user.tg_id != tg_id:
                continue
            if chat_id is not None and user.chat_id != chat_id:
                continue
            if last_daily_draw_winner is not None and user.last_daily_draw_winner != last_daily_draw_winner:
                continue
            self._add_to_cache(user)
            return user

        return None
    
    async def get_users(self, chat_id: Optional[int] = None,
                        last_daily_draw_winner: Optional[bool] = None) -> List[User]: 
        """Получить отфильтрованный массив пользователей"""
        all_users = self._load_all_users()
        filtered_users = []
        
        for user in all_users:
            if chat_id is not None and user.chat_id != chat_id:
                continue
            if last_daily_draw_winner is not None and user.last_daily_draw_winner != last_daily_draw_winner:
                continue
            filtered_users.append(user)
            
        return filtered_users

    async def add(self, tg_id: int, tg_name: str, length: int, custom_title: str, chat_id: int) -> Optional[User]:
        """Создание нового тестового пользователя/бота и запись на диск"""
        existing = await self.get_user(tg_id=tg_id, chat_id=chat_id)
        if existing:
            return

        new_user = User(
            id=self._next_id,
            tg_id=tg_id,
            length=length,
            is_bot=False,  # Дефолтное значение для тестов, можно кастомизировать
            tg_name=tg_name,
            custom_title=custom_title,
            last_daily_draw_winner=False,
            last_length_check=datetime.datetime.now() - datetime.timedelta(days=30),
            last_dice_play=datetime.datetime.now() - datetime.timedelta(days=30),
            last_gladiators_bet=datetime.datetime.now() - datetime.timedelta(days=30),
            last_hunt=datetime.datetime.now() - datetime.timedelta(days=30),
            chat_id=chat_id,
            energy=10,
            money=20,
            inventory=[],
            relations={}
        )
        self._save_user_file(new_user)
        self._add_to_cache(new_user)
        self._next_id += 1

        return new_user
    
    async def update(self, user: User, **kwargs: Any) -> bool:
        """
        Обновление данных пользователя. 
        Принимает либо измененный объект User, либо словарь args с новыми полями.
        """
        if kwargs:
            user_dict = user.model_dump()
            user_dict.update(kwargs)
            updated_user = User.model_validate(user_dict)
            user = updated_user
        else:
            updated_user = user

        self._add_to_cache(updated_user)
        return True
    
    async def update_users_money_by_chat(self, chat_id: int, money:int) -> bool:
        all_users = self._load_all_users()
        
        for user in all_users:
            if chat_id is not None and user.chat_id != chat_id:
                continue
            await self.update(user, money=user.money + money)
            
        return True
    
    async def get_user_heal_items(self, user:User) -> List[InventoryItem]:
        pass

    async def get_item_by_id(self, item_id:int) -> Optional[BaseItem]:
        pass

    async def get_random_item_by_tag(self, tag:DropTags) -> Optional[BaseItem]:
        pass
    
    async def get_place_in_top_by_member(self, tg_id:int, chat_id:int) -> int:
        """Возвращает порядковый номер в топе по размеру {{pencil}}"""
        return 1
    
    async def user_item_transaction(self, user:User, item:ItemORM, quantity:int = 1) -> bool:
        """Перемещение предмета в инвентарь пользователя/бота"""
        pass
    
    async def change_reputation(self, source_id: str, target_id: str, delta: int) -> None:
        """Изменить репутацию (например, уменьшить при пакости)"""
        pass