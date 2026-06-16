from core.services.data_base.db_model import BaseModel
import sqlalchemy as sa


class MonsterStatsORM(BaseModel):
    __tablename__ = "monster_stats"
    id = sa.Column(sa.Integer, primary_key=True)
    monster_id = sa.Column(sa.Integer, sa.ForeignKey('monsters.id'))

    arena_fights = sa.Column(sa.Integer)
    arena_wins = sa.Column(sa.Integer)

    hunts_count = sa.Column(sa.Integer)
    killed = sa.Column(sa.Integer)