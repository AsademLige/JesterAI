from src.core.providers.random_provider import IRandomProvider
from core.data.models.user_stats_model import UserStats
from core.data.models.user_model import User
from core.utils.utils import Utils
from typing import Optional, Tuple
from datetime import datetime

class DiceGameManager:
    def __init__(self, db, dictionary):
        self.db = db
        self.dict = dictionary

    async def check_cool_down(self, user) -> Optional[Tuple[int, int, int]]:
        delta = Utils.get_time_delta(user.last_dice_play, 1)
        if delta.total_seconds() < 3600: 
            return delta
        return None

    async def play(self, user, action: str, provider: IRandomProvider) -> dict:
        await self.db.update_user(user, {User.last_dice_play.name: datetime.now()})
        
        dice_values, sent_messages = await provider.roll_dice(user.chat_id)
        result = sum(dice_values)
        
        is_minor_win = (result > 7 and action == "bigger") or (result < 7 and action == "smaller")
        is_major_win = result == 7 and action == "equal"
        
        award = 5 if is_minor_win else (15 if is_major_win else 0)
        
        if award > 0:
            await self.db.update_user(user, {User.money.name: User.money + award})
            await self.db.add_win_log(user.id, event_type=4 if is_minor_win else 5, money=award)
            
        await self.db.update_user_status(user.id, {
            UserStats.dice_games.name: UserStats.dice_games + 1,
            UserStats.dice_minor_wins.name: UserStats.dice_minor_wins + (1 if is_minor_win else 0),
            UserStats.dice_major_wins.name: UserStats.dice_major_wins + (1 if is_major_win else 0),
        })
        
        return {
            "dice_values": dice_values,
            "is_minor_win": is_minor_win,
            "is_major_win": is_major_win,
            "award": award,
            "sent_messages": sent_messages 
        }