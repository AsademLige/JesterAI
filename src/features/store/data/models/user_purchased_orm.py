from core.services.data_base.db_model import BaseModel
import sqlalchemy as sa

class UserPurchasedORM(BaseModel):
    __tablename__ = "user_purchased"
    id = sa.Column(sa.Integer, primary_key=True)
    product_id = sa.Column(sa.Integer, sa.ForeignKey('store_goods.id'))
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    quantity = sa.Column(sa.Integer)
    date = sa.Column(sa.Date)