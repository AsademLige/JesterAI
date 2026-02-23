from src.models.db_model import BaseModel
import sqlalchemy as sa


class StoreGoods(BaseModel):
    __tablename__ = "store_goods"
    id = sa.Column(sa.Integer, primary_key=True)
    price = sa.Column(sa.Integer)
    title = sa.Column(sa.Text)
    description = sa.Column(sa.Text)
    action = sa.Column(sa.Text)
