from aiogram.types import Message
from cachetools import TTLCache
from typing import List
import asyncio


class MessageManager:
    _instance = None
    _cache:TTLCache

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._cache = TTLCache(maxsize=1000, ttl=600)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
    
    async def delete_old_message(messages:List[Message], delay:int = 3) -> bool:
            success:bool = True
            await asyncio.sleep(delay) 
            for message in messages:
                try:
                    await message.delete()
                except:
                    success = False
                    print("delete message error")
            messages.clear()
            return success