from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup
from aiogram.exceptions import TelegramRetryAfter, TelegramBadRequest
from typing import Union, Optional, Dict
import asyncio
import time

class SafeEditMessage:
    _last_updates: Dict[str, float] = {}
    _pending_tasks: Dict[str, asyncio.Task] = {}
    _min_interval: float = 1.2

    @classmethod
    async def safe_edit(cls, event: Union[Message, CallbackQuery], text: str, **kwargs) -> bool:
        message = event.message if isinstance(event, CallbackQuery) else event
        key = f"{message.chat.id}:{message.message_id}"
        
        if isinstance(event, CallbackQuery):
            try: await event.answer()
            except: pass

        if key in cls._pending_tasks:
            cls._pending_tasks[key].cancel()

        task = asyncio.create_task(cls._bg_worker(key, message, text, **kwargs))
        cls._pending_tasks[key] = task
        
        return True
        
    @classmethod
    async def _bg_worker(cls, key: str, message: Message, text: str, **kwargs):
        """Фоновый исполнитель с обработкой лимитов и ошибок API"""
        try:
            # now = time.time()
            # wait = cls._min_interval - (now - cls._last_updates.get(key, 0))
            
            # if wait > 0:
            #     await asyncio.sleep(wait)

            await message.edit_text(text=text, **kwargs)
            cls._last_updates[key] = time.time()

        except asyncio.CancelledError:
            pass

        except TelegramRetryAfter as e:
            print("receive TelegramRetryAfter")
            await message.answer(f"⛔️ Слишком часто, попробуй через {e.retry_after}")
            await asyncio.sleep(e.retry_after)
            try:
                await message.edit_text(text=text, **kwargs)
                cls._last_updates[key] = time.time()
            except:
                pass

        except TelegramBadRequest as e:
            if "message is not modified" in e.message:
                cls._last_updates[key] = time.time()
            pass

        except Exception as e:
            print(f"Критическая ошибка SafeEdit: {e}")

        finally:
            if cls._pending_tasks.get(key) == asyncio.current_task():
                cls._pending_tasks.pop(key, None)
        
    @classmethod
    async def is_locked(cls, event: Union[Message, CallbackQuery]) -> bool:
        message = event.message if isinstance(event, CallbackQuery) else event
        key = f"{message.from_user.id}:{message.message_id}"
        now = time.time()
        
        last_update = cls._last_updates.get(key, 0)
        
        if (now - last_update) < cls._min_interval:
            if isinstance(event, CallbackQuery):
                try: await event.answer() 
                except: pass
            return True 
            
        return False