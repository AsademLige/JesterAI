from core.services.data_base.db_model import BaseModel
import sqlalchemy as sa


class BotSettings(BaseModel):
    __tablename__ = "bot_settings"
    id = sa.Column(sa.Integer, primary_key=True)
    last_captcha_time = sa.Column(sa.Date)
    chat_id = sa.Column(sa.BigInteger)
    alias = sa.Column(sa.Text)
    events_enabled = sa.Column(sa.Boolean)