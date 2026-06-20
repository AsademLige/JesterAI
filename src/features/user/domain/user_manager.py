from features.user.data.repository.user_repository import IUserRepository
from features.user.data.models.user_model_orm import UserORM
from features.user.data.dtos.user_dto import User
from core.consts.dictionary import Dictionary
from datetime import datetime, timedelta
from core.utils.utils import Utils
import random
import math


class UserManager:
    def __init__(self, repo:IUserRepository):
        self.dictionary:Dictionary = Dictionary()
        self.repo = repo

    async def pencil_change(self, user:User):
        delta:timedelta = Utils.get_time_delta(user.last_length_check)

        if (math.floor(delta.total_seconds() / 3600) < 0):
            return {"error": self.dictionary.timer_message(user, Utils.timedelta_to_hhmm(delta))}

        length_change:int = random.choice([-4, -3, -2, - 1, 1, 2, 3, 4, 5, 6])
        length_from_behind:int = 0

        if (await self.repo.get_place_in_top_by_member(user.tg_id, user.chat_id) > 3):
            length_from_behind = random.choice([0, 1])

        ###Нужно будет заменить args
        if (await self.repo.update(user, {
            UserORM.length.name: user.length + length_change + length_from_behind,
            UserORM.last_length_check.name : datetime.now()
        })):
            return {"msg": self.dictionary.length_change(user.tg_name, length_change), "length_change":length_change}
        
    async def get_menu(self, user:User):
        place_in_top:int = await self.repo.get_place_in_top_by_member(user.tg_id, user.chat_id)
        
        delta_pencil:timedelta = Utils.get_time_delta(user.last_length_check)
        if math.floor(delta_pencil.total_seconds() / 3600) < 0:
            time_to_pencil = Utils.timedelta_to_hhmm(delta_pencil)
        else:
            time_to_pencil = "Готов"
        
        delta_dice:timedelta = Utils.get_time_delta(user.last_dice_play, 1)
        if math.floor(delta_dice.total_seconds() / 3600) < 0:
            time_to_dice = Utils.timedelta_to_hhmm(delta_dice)
        else:
            time_to_dice = "Готов"
        
        return {
            "msg": self.dictionary.user_information(user, 
                                         place_in_top, 
                                         time_to_pencil, 
                                         time_to_dice)
        }
    
    async def is_admin(self, tg_id:int) -> bool:
        return await self.repo.is_admin(tg_id)
    
    async def is_registered_in_chat(self, tg_id:int, chat_id: int) -> bool:
        return await self.repo.get_user(tg_id, chat_id) is not None or tg_id == chat_id
    
