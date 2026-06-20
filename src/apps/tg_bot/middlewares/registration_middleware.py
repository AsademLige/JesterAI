from aiogram.types import Chat, ChatMemberAdministrator, ChatMemberOwner, Message, CallbackQuery, TelegramObject, User
from features.user.data.repository.gino_user_repository import GinoUserRepository
from typing import Any, Callable, Dict, Awaitable, Optional
from features.user.domain.user_manager import UserManager
from core.consts.dictionary import Dictionary
from aiogram.enums import ParseMode
from aiogram import BaseMiddleware
from random import Random

class RegistrationMiddleware(BaseMiddleware):
    user_repo:GinoUserRepository = GinoUserRepository()
    user_mr:UserManager = UserManager(repo=user_repo)
    dict:Dictionary = Dictionary()

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        if isinstance(event, Message) or isinstance(event, CallbackQuery):
            if (event.chat.type == "private" and isinstance(event, Message) and not "start" in event.text):
                return event.answer(Dictionary.private_messages_restriction)
            
            if (await self.user_mr.is_registered_in_chat(event.from_user.id, event.chat.id)):
                return await handler(event, data)
            else:
                await event.answer(await self.register_user(event.from_user.id, event.chat), 
                                   parse_mode=ParseMode.HTML)
        else:
            return await handler(event, data)
        

    async def register_user(self, user: User, chat: Chat) -> str:
        length : int = Random().randint(10, 30)
        from bot import bot
        member  = await bot.get_chat_member(chat.id, user.id)
        custom_title : Optional[str] = None

        if (type(member) is ChatMemberAdministrator or type(member) is ChatMemberOwner):
            custom_title = member.custom_title

        if (await self.user_repo.add(user.id, user.full_name, length, custom_title, chat.id)):
            return self.dict.first_meet(user.full_name, user.id, length, custom_title)
        else:
            return self.dict.error