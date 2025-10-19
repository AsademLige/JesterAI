from src.models.db_model import BaseModel
import sqlalchemy as sa


class CustomStickerModel(BaseModel):
    __tablename__ = "custom_sticker"
    id = sa.Column(sa.Integer, primary_key=True)
    sticker_id = sa.Column(sa.Text)
    sticker_set_name = sa.Column(sa.Text)
    media_path = sa.Column(sa.Text)