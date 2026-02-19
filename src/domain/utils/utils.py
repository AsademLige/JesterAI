from aiogram.types import Message
from typing import List
import asyncio

class Utils():
    @staticmethod
    async def delete_old_message(messages:List[Message], delay:int = 3):
        await asyncio.sleep(delay) 
        for message in messages:
            try:
                await message.delete()
            except:
                print("delete message error")
        messages.clear()