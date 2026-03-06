from src.models.db_model import BaseModel
import sqlalchemy as sa


class Monster(BaseModel):
    __tablename__ = "monsters"
    id = sa.Column(sa.Integer, primary_key=True)
    health = sa.Column(sa.Integer)
    name = sa.Column(sa.Text)
    description = sa.Column(sa.Text)
    drop_rules = sa.Column(sa.Text)