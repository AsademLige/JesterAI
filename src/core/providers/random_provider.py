from abc import ABC, abstractmethod
from typing import List, Tuple, Any

class IRandomProvider(ABC):
    @abstractmethod
    async def roll_dice(self, chat_id: int) -> Tuple[List[int], List[Any]]:
        """
        Бросает два дайса.
        Возвращает: (список из двух значений [1-6], список отправленных сообщений для удаления)
        """
        pass

    @abstractmethod
    async def spin_slot(self, chat_id: int) -> Tuple[int, Any]:
        """
        Крутит слот.
        Возвращает: (значение [1-64], объект отправленного сообщения для удаления)
        """
        pass