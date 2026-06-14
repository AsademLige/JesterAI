from core.services.data_base.db_model import BaseModel
import sqlalchemy as sa


class Monster(BaseModel):
    __tablename__ = "monsters"
    id = sa.Column(sa.Integer, primary_key=True)
    health = sa.Column(sa.Integer)
    name = sa.Column(sa.Text)
    description = sa.Column(sa.Text)
    drop_rules = sa.Column(sa.Text)
    utf8_icon = sa.Column(sa.Text)
    tag = sa.Column(sa.Text)
    fighting_style = sa.Column(sa.Text)
    min_damage = sa.Column(sa.Integer)
    max_damage = sa.Column(sa.Integer)
    crit_chance = sa.Column(sa.Integer)