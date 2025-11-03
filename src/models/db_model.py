from src.services.data_base.db_config import POSTGRES_URI
from aiogram import Dispatcher
import sqlalchemy as sa
from typing import List
from gino import Gino
import datetime
import logging

db = Gino()

class BaseModel(db.Model):
    __abstract__ = True

    def __str__(self):
        model = self.__class__.__name__
        table: sa.Table = sa.inspect(self.__class__)
        primary_key_columns: List[sa.Column] = table.primary_key.columns
        values = {
            column.name: getattr(self, self._column_name_map[column.name])
            for column in primary_key_columns
        }
        values_str = " ".join(f"{name}={value!r}" for name, value in values.items())
        return f"<{model} {values_str}>"
    
class TimedBaseModel(BaseModel):
    __abstract__ = True

    created_at = db.Column(db.DateTime(True), server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime(True),
        default=datetime.datetime.now(datetime.timezone.utc),
        onupdate=datetime.datetime.now(datetime.timezone.utc),
        server_default=db.func.now(),
    )

async def on_startup(dispatcher: Dispatcher):
    logging.info(f"Setup PostgreSQL Connection on: {POSTGRES_URI}")
    await db.set_bind(POSTGRES_URI)