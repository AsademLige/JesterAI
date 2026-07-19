from core.data.models.str_assets_negative_length_change_model import StrAssetsNegativeLengthChange
from core.data.models.str_assets_positive_length_change_model import StrAssetsPositiveLengthChange
from core.data.models.custom_sticker_model import CustomSticker
from features.user.data.models.user_model_orm import UserORM
from features.game_engine.data.models.bot_settings_orm import BotSettingsORM
from core.data.models.sticker_set_model import StickerSet
from core.data.models.winners_log_model import WinnersLog
from core.services.data_base.db_model import db
from core.consts.config import Prefs
from sqlalchemy import func, select
from typing import List, Dict, Any
from datetime import  datetime
from typing import Optional
from sqlalchemy import and_
from math import ceil
import random

prefs = Prefs()

class DataBase():
    def __init__(self):
        pass
        
    ###-----------------------------------------
    ### Методы работы с данными наборов стикеров 
    ###-----------------------------------------

    async def add_sticker_set(self, short_name:str, title:str):
        try:
            sticker_set = StickerSet(short_name = short_name, title = title)
            await sticker_set.create()
            return True
        except Exception as error: 
            print(f"sticker set create error: {error}")
            return False
        
    async def add_custom_sticker(self, media_path: str, sticker_id:str, sticker_set_name:str):
        try:
            custom_sticker = CustomSticker(media_path = media_path, 
                                                sticker_id = sticker_id, 
                                                sticker_set_name = sticker_set_name)
            await custom_sticker.create()
            return True
        except Exception as error: 
            print(f"custom sticker create error: {error}")
            return False
        
    async def get_custom_sticker_by_id(self, sticker_id:str,) -> Optional[CustomSticker]:
        try:
            custom_sticker : CustomSticker = await CustomSticker.\
            query.where(CustomSticker.sticker_id == sticker_id).gino.first()

            return custom_sticker
        except Exception as error:
            print(f"custom sticker media get error: {error}")
            return None
        
    async def delete_custom_sticker_by_id(self, sticker_id:str) -> bool:
        try:
            return await CustomSticker.delete.\
                where(CustomSticker.sticker_id == sticker_id).gino.status()
        except Exception as error:
            print(f"custom sticker media delete error: {error}")
            return False
        
    async def get_custom_stickers_by_set_name(self,
                                              sticker_set_name:str) -> Optional[List[CustomSticker]]:
        try:
            custom_stickers : List[CustomSticker] = await CustomSticker.\
            query.where(CustomSticker.sticker_set_name == sticker_set_name).gino.all()

            return custom_stickers
        except Exception as error:
            print(f"custom stickers media get error: {error}")
            return None

    async def get_all_sticker_sets(self) ->  List[StickerSet]: 
        return await StickerSet.query.gino.all()
    
    async def get_sticker_set_by_id(self, set_id:str,) -> Optional[StickerSet]:
        try:
            custom_sticker : StickerSet = await StickerSet.\
            query.where(StickerSet.id == set_id).gino.first()

            return custom_sticker
        except Exception as error:
            print(f"sticker set get error: {error}")
            return None
    
    async def delete_sticker_set_by_name(self, short_name:str):
        return await StickerSet.delete.\
            where(StickerSet.short_name == short_name).gino.status()

    ###-----------------------------------------
    ### Методы работы с статистикой выигрышей 
    ###-----------------------------------------

    async def get_winners_logs_page(self, chat_id:int, page: int = 1):
        """Получить одну страницу логов"""
        items_per_page:int = 10
        offset = (page - 1) * items_per_page

        subquery = select([UserORM.id]).where(UserORM.chat_id == chat_id).alias()
        logs:List[WinnersLog] = await WinnersLog.query.where(WinnersLog.user_id.in_(subquery)).order_by(WinnersLog.win_date.desc())\
            .offset(offset).limit(items_per_page).gino.all()

        total_logs:int = await select([db.func.count(WinnersLog.id)]).where(
            WinnersLog.user_id.in_(subquery)
        ).gino.scalar()
        
        logs_page_users_id:List[int] = []
        
        for log in logs:
            if (not log.user_id in logs_page_users_id):
                logs_page_users_id.append(log.user_id)
        
        total_pages = ceil(total_logs / items_per_page)

        users: List[UserORM] = await UserORM.query.where(UserORM.id.in_(logs_page_users_id)).gino.all()
        
        return logs, total_pages, users
    
    async def add_win_log(self, user_id:int, event_type:int = 0, money:int = 0, length:int = 0):
        try:
            log = WinnersLog(
                user_id = user_id,
                event_type = event_type,
                money = money,
                length = length,
                win_date = datetime.now()
            )
            await log.create()
            return True
        except Exception as error: 
            print(f"log create error: {error}")
            return False

    ###-----------------------------------------
    ### Методы загрузки наборов данных 
    ###-----------------------------------------

    async def get_negative_length_change_assets(self) -> List[str]: 
        models:List[StrAssetsNegativeLengthChange] = await StrAssetsNegativeLengthChange.query.gino.all()
        return [model.data for model in models] 
    
    async def get_positive_length_change_assets(self) -> List[str]: 
        models:List[StrAssetsPositiveLengthChange] = await StrAssetsPositiveLengthChange.query.gino.all()
        return [model.data for model in models] 