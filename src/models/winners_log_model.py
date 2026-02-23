from src.models.db_model import BaseModel
import sqlalchemy as sa


class WinnersLog(BaseModel):
    __tablename__ = "winners_log"
    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    
    ### 0 - trash_loto_jackpot
    ### 1 - trash_loto_minor_win
    ### 2 - trash_loto_major_win
    ### 3 - trash_loto_consolation
    ### 4 - dice_game_minor_win
    ### 5 - dice_game_major_win
    event_type = sa.Column(sa.Integer)

    money = sa.Column(sa.Integer)
    length = sa.Column(sa.Integer)
    win_date = sa.Column(sa.Date)
    