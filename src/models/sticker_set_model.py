from src.models.db_model import BaseModel
import sqlalchemy as sa


class StickerSetModel(BaseModel):
    __tablename__ = "sticker_sets"
    id = sa.Column(sa.Integer, primary_key=True)
    short_name = sa.Column(sa.Text)
    title = sa.Column(sa.Text)