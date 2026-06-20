from core.services.data_base.db_model import BaseModel
import sqlalchemy as sa


class RelationsORM(BaseModel):
    __tablename__ = "relations"
    id = sa.Column(sa.Integer, primary_key=True)
    reputation = sa.Column(sa.Integer)
    
    source_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    target_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
