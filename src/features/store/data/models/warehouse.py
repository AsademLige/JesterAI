from core.services.data_base.db_model import BaseModel
import sqlalchemy as sa


class Warehouse(BaseModel):
    __tablename__ = "warehouse"
    id = sa.Column(sa.Integer, primary_key=True)
    product_id = sa.Column(sa.Integer, sa.ForeignKey('store_goods.id'))
    quantity = sa.Column(sa.Integer)
    max_capacity = sa.Column(sa.Integer)