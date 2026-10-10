from abc import ABC, abstractmethod

class INotificationProvider(ABC):
    @abstractmethod
    async def notifivcate(self, receiver_id: int, message:str, delete_delay:int = -1) -> bool:
        """
        Абстрактный класс для уведомлений
        """
        pass