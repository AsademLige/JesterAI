from features.user.data.repository.gino_user_repository import GinoUserRepository
from features.user.data.models.user_stats_orm import UserStatsORM
from src.core.providers.random_provider import IRandomProvider
from features.user.data.models.user_model_orm import UserORM
from features.user.data.dtos.user_dto import User
from core.consts.dictionary import Dictionary
from core.data.data_base import DataBase
from core.utils.utils import Utils
from typing import Optional, Tuple
from datetime import datetime

class DiceGameManager:
    user_repo:GinoUserRepository = GinoUserRepository()

    def __init__(self, db:DataBase, dictionary:Dictionary):
        self.db = db
        self.dict = dictionary

    async def check_cool_down(self, user:User) -> Optional[Tuple[int, int, int]]:
        delta = Utils.get_time_delta(user.last_dice_play, 1)
        if delta.total_seconds() < 3600: 
            return delta
        return None

    async def play(self, user:User, action: str, provider: IRandomProvider) -> dict:
        dice_values, roll_result = await provider.roll_dice(user.chat_id)
        result = sum(dice_values)
        
        is_minor_win = (result > 7 and action == "bigger") or (result < 7 and action == "smaller")
        is_major_win = result == 7 and action == "equal"
        
        award = 5 if is_minor_win else (15 if is_major_win else 0)
        
        if award > 0:
            await self.user_repo.update(user, {UserORM.money.name: user.money + award,
                            UserStatsORM.dice_games.name: user.dice_games + 1,
                            UserORM.last_dice_play.name: datetime.now(),
                            UserStatsORM.dice_minor_wins.name: user.dice_minor_wins + (1 if is_minor_win else 0),
                            UserStatsORM.dice_major_wins.name: user.dice_major_wins + (1 if is_major_win else 0),})
            
            await self.db.add_win_log(user.id, event_type=4 if is_minor_win else 5, money=award)
        else:
            await self.user_repo.update(user, {
                            UserStatsORM.dice_games.name: user.dice_games + 1,
                            UserORM.last_dice_play.name: datetime.now()})

        msg:str

        if is_minor_win:
            msg = self.dict.dice_minor_win(user, dice_values, award)
        elif is_major_win:
            msg = self.dict.dice_minor_win(user, dice_values, award)
        else:
            msg = self.dict.dice_lose(user, dice_values)
        
        return {
            "msg": msg,
            "roll_result": roll_result 
        }