from core.services.data_base.db_model import TimedBaseModel
import sqlalchemy as sa


class User(TimedBaseModel):
    __tablename__ = "users"
    id = sa.Column(sa.Integer, primary_key=True)
    tg_id = sa.Column(sa.BigInteger)
    length = sa.Column(sa.BigInteger)
    tg_name = sa.Column(sa.Text)
    utf8_icon = sa.Column(sa.Text)
    custom_title = sa.Column(sa.Text)
    chat_id = sa.Column(sa.BigInteger)
    money = sa.Column(sa.Integer)
    last_daily_draw_winner = sa.Column(sa.Boolean)
    last_length_check = sa.Column(sa.Date)
    last_dice_play = sa.Column(sa.Date)
    last_hunt = sa.Column(sa.Date)
    last_gladiators_bet = sa.Column(sa.Date)
    last_boss_hunt = sa.Column(sa.Date)
    role_id = sa.Column(sa.Integer, sa.ForeignKey('roles.id'))