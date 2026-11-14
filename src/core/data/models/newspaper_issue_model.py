from core.services.data_base.db_model import BaseModel
import sqlalchemy as sa


class NewspaperIssue(BaseModel):
    __tablename__ = "newspaper_issues"
    # id также выступает номером выпуска
    id = sa.Column(sa.Integer, primary_key=True)
    # data хранит готовый текст номера (HTML)
    data = sa.Column(sa.Text)
    created = sa.Column(sa.Date)
