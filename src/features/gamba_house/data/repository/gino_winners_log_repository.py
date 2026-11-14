from features.gamba_house.data.repository.winners_log_repository import IWinnersLogRepository
from features.user.data.models.user_model_orm import UserORM
from core.data.models.winners_log_model import WinnersLog
from core.services.data_base.db_model import db
from core.utils.app_herald import AppHerald
from sqlalchemy import select, desc
from datetime import datetime
from typing import List, Optional, Tuple
from math import ceil
import logging


class GinoWinnersLogRepository(IWinnersLogRepository):
    _instance = None
    logger: AppHerald = AppHerald()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def add_win_log(self, user_id: int, event_type: int = 0, money: int = 0,
                          length: int = 0, bet: int = 0) -> bool:
        try:
            log = WinnersLog(
                user_id=user_id,
                event_type=event_type,
                money=money,
                length=length,
                bet=bet,
                win_date=datetime.now(),
            )
            await log.create()
            return True
        except Exception as error:
            self.logger.send_log("winners_log_repo", logging.ERROR, f"log create error: {error}")
            return False

    async def get_winners_logs_page(self, chat_id: int, page: int = 1) -> Tuple[List[WinnersLog], int, List[UserORM]]:
        """Получить одну страницу логов (служебные записи проигрышей event_type=6 исключаются)."""
        items_per_page: int = 10
        offset = (page - 1) * items_per_page

        subquery = select([UserORM.id]).where(UserORM.chat_id == chat_id).alias()
        logs: List[WinnersLog] = await WinnersLog.query\
            .where(WinnersLog.user_id.in_(subquery))\
            .where(WinnersLog.event_type != 6)\
            .order_by(WinnersLog.win_date.desc())\
            .offset(offset).limit(items_per_page).gino.all()

        total_logs: int = await select([db.func.count(WinnersLog.id)]).where(
            WinnersLog.user_id.in_(subquery)
        ).where(WinnersLog.event_type != 6).gino.scalar()

        logs_page_users_id: List[int] = []
        for log in logs:
            if (not log.user_id in logs_page_users_id):
                logs_page_users_id.append(log.user_id)

        total_pages = ceil(total_logs / items_per_page)
        users: List[UserORM] = await UserORM.query.where(UserORM.id.in_(logs_page_users_id)).gino.all()

        return logs, total_pages, users

    async def get_top_spender(self, since: datetime) -> Optional[Tuple[int, int]]:
        """Возвращает (users.id, суммарные ставки) самого активного игрока гамба-хауса с момента since."""
        try:
            total_bet = db.func.sum(WinnersLog.bet)
            row = await select([WinnersLog.user_id, total_bet.label("spent")])\
                .where(WinnersLog.win_date >= since)\
                .group_by(WinnersLog.user_id)\
                .order_by(desc(total_bet))\
                .limit(1).gino.first()
            if not row or not row[1]:
                return None
            return (row[0], int(row[1]))
        except Exception as error:
            self.logger.send_log("winners_log_repo", logging.ERROR, f"top spender error: {error}")
            return None
