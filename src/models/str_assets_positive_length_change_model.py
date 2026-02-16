from src.models.db_model import BaseModel
import sqlalchemy as sa


class StrAssetsPositiveLengthChange(BaseModel):
    __tablename__ = "str_assets_positive_length_change"
    id = sa.Column(sa.Integer, primary_key=True)
    data = sa.Column(sa.Text)