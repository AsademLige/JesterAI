from core.services.data_base.db_model import BaseModel
import sqlalchemy as sa


class BestiaryORM(BaseModel):
    __tablename__ = "user_bestiary"
    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))

    kind = sa.Column(sa.Text)
    entity_id = sa.Column(sa.Integer)
    times = sa.Column(sa.Integer, server_default="1")
    record_value = sa.Column(sa.Float)

    first_seen_at = sa.Column(sa.Integer)
    last_seen_at = sa.Column(sa.Integer)

    __table_args__ = (sa.UniqueConstraint('user_id', 'kind', 'entity_id'),)
