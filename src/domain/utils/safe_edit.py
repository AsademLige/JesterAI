from aiogram.exceptions import TelegramRetryAfter, TelegramBadRequest
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from typing import Dict, Optional, Union
import asyncio
import time

class SafeEditMessage():
    _last_updates: Dict[str, float] = {}
    _min_interval: float = 0.8

    @classmethod
    async def safe_edit(
        cls, 
        event: Union[Message, CallbackQuery], 
        text: str, 
        reply_markup: Optional[InlineKeyboardMarkup] = None,
        parse_mode: str = "HTML"
    ) -> bool:
        """
        Безопасно редактирует сообщение. 
        Если это CallbackQuery, всегда подтверждает его (убирает загрузку).
        """
        now = time.time()
        
        message = event.message if isinstance(event, CallbackQuery) else event
        chat_id = message.chat.id
        msg_id = message.message_id
        key = f"{chat_id}:{msg_id}"

        last_update = cls._last_updates.get(key, 0)
        if now - last_update < cls._min_interval:
            return False 

        try:
            cls._last_updates[key] = now
            await message.edit_text(
                text=text, 
                reply_markup=reply_markup, 
                parse_mode=parse_mode
            )
            return True

        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after)
            try:
                await message.edit_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
                return True
            except:
                return False

        except TelegramBadRequest as e:
            if "message is not modified" in e.message:
                return True
            return False
        
    @classmethod
    def _get_key(cls, event: Union[Message, CallbackQuery]) -> str:
        """Вспомогательный метод для генерации уникального ключа сообщения"""
        message = event.message if isinstance(event, CallbackQuery) else event
        return f"{message.chat.id}:{message.message_id}"

    @classmethod
    async def is_locked(cls, event: Union[Message, CallbackQuery]) -> bool:
        """
        Проверяет, заблокировано ли редактирование для этого сообщения.
        """
        key = cls._get_key(event)
        now = time.time()
        last_update = cls._last_updates.get(key, 0)
        
        if isinstance(event, CallbackQuery):
            try:
                await event.answer() 
            except Exception:
                pass

        return (now - last_update) < cls._min_interval