from features.user.data.models.user_model_orm import UserORM
from core.data.models.winners_log_model import WinnersLog
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Tuple


class IWinnersLogRepository(ABC):
    @abstractmethod
    async def add_win_log(self, user_id: int, event_type: int = 0, money: int = 0,
                          length: int = 0, bet: int = 0) -> bool:
        """Записать результат спина/игры. bet — сумма ставки (для учёта трат в гамба-хаусе)."""
        pass

    @abstractmethod
    async def get_winners_logs_page(self, chat_id: int, page: int = 1) -> Tuple[List[WinnersLog], int, List[UserORM]]:
        """Страница таблицы выигрышей чата (без служебных записей проигрышей)."""
        pass

    @abstractmethod
    async def get_top_spender(self, since: datetime) -> Optional[Tuple[int, int]]:
        """(users.id, сумма ставок) игрока, потратившего больше всех в гамба-хаусе с момента since."""
        pass

    @abstractmethod
    async def get_total_spent(self, since: datetime) -> int:
        """Суммарные ставки всех игроков гамба-хауса с момента since."""
        pass
