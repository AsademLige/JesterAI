from features.newspaper.data.repository.newspaper_repository import INewspaperRepository
from core.data.models.newspaper_issue_model import NewspaperIssue
from core.services.data_base.db_model import db
from core.utils.app_herald import AppHerald
from sqlalchemy import select
from datetime import datetime
import logging


class GinoNewspaperRepository(INewspaperRepository):
    _instance = None
    logger: AppHerald = AppHerald()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def get_next_issue_number(self) -> int:
        """Следующий номер выпуска газеты (MAX(id) + 1)."""
        try:
            last_number: int = await select([db.func.max(NewspaperIssue.id)]).gino.scalar()
            return (last_number or 0) + 1
        except Exception as error:
            self.logger.send_log("newspaper_repo", logging.ERROR, f"get next issue number error: {error}")
            return 1

    async def create_issue(self, number: int, data: str) -> bool:
        """Сохранить готовый выпуск газеты под указанным номером."""
        try:
            issue = NewspaperIssue(id=number, data=data, created=datetime.now())
            await issue.create()
            return True
        except Exception as error:
            self.logger.send_log("newspaper_repo", logging.ERROR, f"newspaper issue create error: {error}")
            return False
