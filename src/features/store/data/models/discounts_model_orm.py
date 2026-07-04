from core.services.data_base.db_model import BaseModel
import sqlalchemy as sa

class ProductDiscountORM(BaseModel):
    __tablename__ = "product_discounts"
    id = sa.Column(sa.Integer, primary_key=True)
    product_id = sa.Column(sa.Integer, sa.ForeignKey('store_goods.id'))
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    discount_percent = sa.Column(sa.Integer)
    is_active = sa.Column(sa.Boolean)
