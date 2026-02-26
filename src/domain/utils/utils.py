from datetime import timedelta, datetime
from typing import List, Any, Optional
from aiogram.types import Message
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

    @staticmethod
    def format_datetime(dt: datetime) -> str:
        """
        Расширенное форматирование даты
        """
        current_time = datetime.now()    
        
        delta = current_time - dt
        total_seconds = delta.total_seconds()
        
        # Меньше минуты
        if total_seconds < 60:
            return "только что"
        
        # Меньше часа - минуты
        if total_seconds < 3600:
            minutes = int(total_seconds // 60)
            return Utils.get_minutes_ago_text(minutes)
        
        # Меньше суток - часы
        if total_seconds < 86400:
            hours = int(total_seconds // 3600)
            return Utils.get_hours_ago_text(hours)
        
        # Меньше 7 дней - дни
        if total_seconds < 604800:  # 7 * 24 * 3600
            days = int(total_seconds // 86400)
            return Utils.get_days_ago_text(days)
        
        # В этом году
        if dt.year == current_time.year:
            return dt.strftime("%d.%m %H:%M")
        
        # Прошлые годы
        return dt.strftime("%d.%m.%Y %H:%M")

    @staticmethod
    def get_minutes_ago_text(minutes: int) -> str:
        """Склонение для минут"""
        if minutes % 10 == 1 and minutes % 100 != 11:
            return f"{minutes} минуту назад"
        elif 2 <= minutes % 10 <= 4 and (minutes % 100 < 10 or minutes % 100 >= 20):
            return f"{minutes} минуты назад"
        else:
            return f"{minutes} минут назад"

    @staticmethod
    def get_hours_ago_text(hours: int) -> str:
        """Склонение для часов"""
        if hours % 10 == 1 and hours % 100 != 11:
            return f"{hours} час назад"
        elif 2 <= hours % 10 <= 4 and (hours % 100 < 10 or hours % 100 >= 20):
            return f"{hours} часа назад"
        else:
            return f"{hours} часов назад"

    @staticmethod
    def get_days_ago_text(days: int) -> str:
        """Склонение для дней"""
        if days % 10 == 1 and days % 100 != 11:
            return f"{days} день назад"
        elif 2 <= days % 10 <= 4 and (days % 100 < 10 or days % 100 >= 20):
            return f"{days} дня назад"
        else:
            return f"{days} дней назад"
    
    @staticmethod
    def try_parse_int(value: str) -> Optional[int]:
        """Пытается преобразовать строку в int, возвращает None при ошибке"""
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def is_valid_index(list: List[Any], index: int) -> bool:
        """Проверяет, существует ли индекс в списке"""
        return 0 <= index < len(list)