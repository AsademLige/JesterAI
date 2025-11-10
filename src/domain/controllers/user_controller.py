from aiogram.types import User, Chat, ChatMemberAdministrator, ChatMemberOwner
from src.domain.utils.text_processing import TextProcessing as tp
from src.services.data_base.db import DataBase
from src.data.dictionary import Dictionary
from src.data.config import Prefs
from typing import Optional
from random import Random
from aiogram import Bot

db = DataBase()
dict = Dictionary()
prefs = Prefs()
bot = Bot(token=prefs.bot_token)

class UserController():
    @staticmethod
    async def is_admin(user: User) -> bool:
        return await db.is_admin(user.id)
    
    @staticmethod
    async def is_registered_in_chat(user: User, chat_id: int) -> bool:
        print(f"cdlog {await db.get_user_by_chat_id(user.id, chat_id)}")
        return await db.get_user_by_chat_id(user.id, chat_id) is not None

    @staticmethod
    async def register_user(user: User, chat: Chat) -> str:
        length : int = Random().randint(10, 30)
        member  = await bot.get_chat_member(chat.id, user.id)
        custom_title : Optional[str] = None

        if (type(member) is ChatMemberAdministrator or type(member) is ChatMemberOwner):
            custom_title = member.custom_title

        if (await db.add_user(user.id, user.full_name, length, custom_title, chat.id)):
            return dict.first_meet(user.full_name, user.id, length, custom_title)
        else:
            return dict.error