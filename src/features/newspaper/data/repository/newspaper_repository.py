from abc import ABC, abstractmethod
from typing import Optional


class INewspaperRepository(ABC):
    @abstractmethod
    async def get_next_issue_number(self) -> int:
        """Следующий номер выпуска газеты."""
        pass

    @abstractmethod
    async def create_issue(self, number: int, data: str) -> bool:
        """Сохранить готовый выпуск газеты под указанным номером."""
        pass

    @abstractmethod
    async def get_issue(self, number: int) -> Optional[str]:
        """Текст выпуска газеты по номеру или None, если выпуска нет."""
        pass
