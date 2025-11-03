from src.models.db_model import BaseModel
import sqlalchemy as sa


class RoleModel(BaseModel):
    __tablename__ = "roles"
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.Text)
    alias = sa.Column(sa.Text)