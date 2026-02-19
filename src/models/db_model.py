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

async def ensure_games_played_column():
    """
    Убедимся, что столбец `games_played` существует в таблице `users`.
    Если его нет — добавим его вручную через SQL.
    """
    try:
        query = """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'users'
            AND column_name = 'games_played';
        """
        result = await db.fetch_one(query)
        if not result:
            # Столбец не существует — добавляем его
            await db.execute("ALTER TABLE users ADD COLUMN games_played INTEGER DEFAULT 0;")
            print("✅ Столбец `games_played` добавлен в таблицу `users`.")
        else:
            print("✅ Столбец `games_playzed` уже существует.")
    except Exception as e:
        print(f"❌ Ошибка при проверке или добавлении столбца `games_played`: {e}")