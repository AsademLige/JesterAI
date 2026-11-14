from abc import ABC, abstractmethod


class INewspaperRepository(ABC):
    @abstractmethod
    async def get_next_issue_number(self) -> int:
        """Следующий номер выпуска газеты."""
        pass

    @abstractmethod
    async def create_issue(self, number: int, data: str) -> bool:
        """Сохранить готовый выпуск газеты под указанным номером."""
        pass
