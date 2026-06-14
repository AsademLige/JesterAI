from core.services.data_base.db_model import BaseModel
import sqlalchemy as sa


class UserInventoryItem(BaseModel):
    __tablename__ = "user_inventory"
    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    product_id = sa.Column(sa.Integer, sa.ForeignKey('store_goods.id'))
    quantity = sa.Column(sa.Integer)