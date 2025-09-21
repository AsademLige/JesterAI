from src.services.data_base.db import DataBase
from src.data.dictionary import Dictionary
from aiogram.types import User

db = DataBase()

class UserController():
    @staticmethod
    async def is_registered(user: User) -> str:
        return not await db.is_user_unknown(user.id)

    @staticmethod
    async def register_user(user: User) -> str:
        return Dictionary.first_meet