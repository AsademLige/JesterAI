from src.models.db_model import TimedBaseModel
import sqlalchemy as sa


class UserModel(TimedBaseModel):
    __tablename__ = "users"
    id = sa.Column(sa.Integer, primary_key=True)
    tg_id = sa.Column(sa.BigInteger)
    length = sa.Column(sa.BigInteger)
    tg_name = sa.Column(sa.Text)
    custom_title = sa.Column(sa.Text)
    chat_id = sa.Column(sa.Integer)
    money = sa.Column(sa.Integer)
    last_length_check = sa.Column(sa.Date)
    role_id = sa.Column(sa.Integer, sa.ForeignKey('roles.id'))