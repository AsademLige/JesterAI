from src.domain.controllers.user_controller import UserController
from aiogram.types import Message, CallbackQuery, TelegramObject
from typing import Any, Callable, Dict, Awaitable
from src.data.dictionary import Dictionary
from aiogram import BaseMiddleware

class RegistrationMiddleware(BaseMiddleware):
     async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        if isinstance(event, Message) or isinstance(event, CallbackQuery):
            if (await UserController.is_registered(event.from_user)):
                return await handler(event, data)
            else:
                await event.answer(await UserController.register_user(event.from_user, event.chat))
        else:
            return await handler(event, data)