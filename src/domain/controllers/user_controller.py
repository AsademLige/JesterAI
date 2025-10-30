from aiogram.types import User, Chat, ChatMemberAdministrator, ChatMemberOwner
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
    async def is_registered(user: User) -> str:
        return not await db.is_user_unknown(user.id)

    @staticmethod
    async def register_user(user: User, chat: Chat) -> str:
        length : int = Random().randint(10, 30)
        member  = await bot.get_chat_member(chat.id, user.id)
        custom_title : Optional[str] = None

        if (type(member) is ChatMemberAdministrator or type(member) is ChatMemberOwner):
            custom_title = member.custom_title
        
        if (await db.add_user(user.id, user.full_name, length, custom_title)):
            return dict.first_meet(user.full_name, length, custom_title)
        else:
            return dict.error