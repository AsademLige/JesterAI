from core.services.data_base.db_model import BaseModel
import sqlalchemy as sa


class BattleORM(BaseModel):
    __tablename__ = "battles"
    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer) 
    started_timestamp = sa.Column(sa.Integer)
    

    status = sa.Column(sa.Text)
    data = sa.Column(sa.JSON, default=dict, server_default="{}") 
    validation = sa.Column(sa.JSON, default=dict, server_default="{}") 
    log = sa.Column(sa.JSON, default=list, server_default="[]")