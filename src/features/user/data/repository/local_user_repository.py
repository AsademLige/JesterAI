from calendar import month
import datetime

from features.user.data.repository.user_repository import IUserRepository
from features.items.data.models.item_orm import ItemORM
from features.user.data.dtos.user_dto import User
from typing import Any, Dict, List, Optional
from pathlib import Path

class LocalUserRepository(IUserRepository):
    def __init__(self, snapshot_dir: str = "tests/snapshots"):
        self.snapshot_dir = Path(snapshot_dir)
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)

        self._next_id = self._get_max_id() + 1

    def _get_max_id(self) -> int:
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
        for file_path in self.snapshot_dir.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    # Pydantic v2 отлично собирает модель из json-строки
                    user_data = f.read()
                    if user_data.strip():
                        users.append(User.model_validate_json(user_data))
            except Exception as e:
                print(f"[Warning] Ошибка загрузки снапшота {file_path}: {e}")
                continue
        return users

    def _save_user_file(self, user: User) -> None:
        """Сохранение конкретного юзера в файл JSON"""
        file_path = self.snapshot_dir / f"{user.id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            # Сериализуем модель Pydantic в JSON (обработает datetime и вложенные DTO)
            f.write(user.model_dump_json(indent=4))

    async def get_user(self, tg_id: Optional[int] = None, 
                       chat_id: Optional[int] = None,
                       id: Optional[int] = None,
                       last_daily_draw_winner: Optional[bool] = None) -> Optional[User]:
        """Поиск пользователя по переданным фильтрам (логика AND)"""
        # Если передан id, можно оптимизировать и прочитать конкретный файл напрямую
        if id is not None:
            file_path = self.snapshot_dir / f"{id}.json"
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    return User.model_validate_json(f.read())
            return None

        # Иначе фильтруем по всему списку
        all_users = self._load_all_users()
        for user in all_users:
            if tg_id is not None and user.tg_id != tg_id:
                continue
            if chat_id is not None and user.chat_id != chat_id:
                continue
            if last_daily_draw_winner is not None and user.last_daily_draw_winner != last_daily_draw_winner:
                continue
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

    async def add(self, tg_id: int, tg_name: str, length: int, custom_title: str, chat_id: int) -> None:
        """Создание нового тестового пользователя/бота и запись на диск"""
        # Проверяем, существует ли уже такой tg_id в этом чате (симуляция ограничений уникальности БД)
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
            last_length_check=datetime.datetime.now() - datetime.timedelta(days=30),
            last_dice_play=datetime.datetime.now() - datetime.timedelta(days=30),
            last_gladiators_bet=datetime.datetime.now() - datetime.timedelta(days=30),
            last_hunt=datetime.datetime.now() - datetime.timedelta(days=30),
            chat_id=chat_id,
            money=20,
            inventory=[],
            relations={}
        )
        self._save_user_file(new_user)
        self._next_id += 1
    
    async def update(self, user: User, args: Dict[str, Any] = {}) -> bool:
        """
        Обновление данных пользователя. 
        Принимает либо измененный объект User, либо словарь args с новыми полями.
        """
        file_path = self.snapshot_dir / f"{user.id}.json"
        if not file_path.exists():
            return False
        

        if args:
            user_dict = user.model_dump()
            user_dict.update(args)
            updated_user = User.model_validate(user_dict)
        else:
            updated_user = user

        self._save_user_file(updated_user)
        return True
    
    async def update_users_money_by_chat(self, chat_id: int, money:int) -> bool:
        all_users = self._load_all_users()
        
        for user in all_users:
            if chat_id is not None and user.chat_id != chat_id:
                continue

            user_dict = user.model_dump()
            user_dict.update({"money":user.money + money})
            User.model_validate(user_dict)

        return True
    
    async def get_place_in_top_by_member(self, tg_id:int, chat_id:int) -> int:
        """Возвращает порядковый номер в топе по размеру {{pencil}}"""
        return 1
    
    async def user_item_transaction(self, user:User, item:ItemORM, quantity:int = 1) -> bool:
        """Перемещение предмета в инвентарь пользователя/бота"""
        pass
    
    async def change_reputation(self, source_id: str, target_id: str, delta: int) -> None:
        """Изменить репутацию (например, уменьшить при пакости)"""
        pass