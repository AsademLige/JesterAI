from datetime import timedelta, datetime
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

    @staticmethod
    def get_last_member_check_delta(last_length_check: datetime, hours_delta:int = 24) -> timedelta:
        return datetime.now() - (last_length_check + timedelta(hours=hours_delta))

    @staticmethod
    def timedelta_to_hhmm(delta):
        """Преобразует timedelta в строку формата ЧЧ:мм"""
        total_seconds = int(delta.total_seconds()) * -1
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours:02d}:{minutes:02d}"