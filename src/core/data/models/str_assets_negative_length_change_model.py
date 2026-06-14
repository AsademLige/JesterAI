from core.services.data_base.db_model import BaseModel
import sqlalchemy as sa


class StrAssetsNegativeLengthChange(BaseModel):
    __tablename__ = "str_assets_negative_length_change"
    id = sa.Column(sa.Integer, primary_key=True)
    data = sa.Column(sa.Text)