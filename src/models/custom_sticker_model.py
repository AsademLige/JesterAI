from src.models.db_model import BaseModel
import sqlalchemy as sa


class CustomStickerModel(BaseModel):
    __tablename__ = "custom_sticker"
    id = sa.Column(sa.Integer, primary_key=True)
    media_path = sa.Column(sa.Text)