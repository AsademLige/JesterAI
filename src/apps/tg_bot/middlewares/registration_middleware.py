from domain.controllers.user_controller import UserController
from aiogram.types import Message, CallbackQuery, TelegramObject
from typing import Any, Callable, Dict, Awaitable
from core.consts.dictionary import Dictionary
from aiogram.enums import ParseMode
from aiogram import BaseMiddleware

class RegistrationMiddleware(BaseMiddleware):
     async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        if isinstance(event, Message) or isinstance(event, CallbackQuery):
            if (event.chat.type == "private" and isinstance(event, Message) and not "start" in event.text):
                return event.answer(Dictionary.private_messages_restriction)
            
            if (await UserController.is_registered_in_chat(event.from_user, event.chat.id)):
                return await handler(event, data)
            else:
                await event.answer(await UserController.register_user(event.from_user, event.chat), 
                                   parse_mode=ParseMode.HTML)
        else:
            return await handler(event, data)