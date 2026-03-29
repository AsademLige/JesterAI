from src.models.db_model import BaseModel
import sqlalchemy as sa


class UserStats(BaseModel):
    __tablename__ = "user_stats"
    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))

    trash_loto_money_wins = sa.Column(sa.Integer)
    trash_loto_length_wins = sa.Column(sa.Integer)
    trash_loto_jackpots = sa.Column(sa.Integer)
    trash_loto_spins = sa.Column(sa.Integer)
    
    dice_minor_wins = sa.Column(sa.Integer)
    dice_major_wins = sa.Column(sa.Integer)
    dice_games = sa.Column(sa.Integer)
    gladiators_bet = sa.Column(sa.Integer)
    gladiators_bet_win = sa.Column(sa.Integer)

    good_hunting_count = sa.Column(sa.Integer)
    duels_win_count = sa.Column(sa.Integer)
    duels_count = sa.Column(sa.Integer)


