from src.models.str_assets_negative_length_change_model import StrAssetsNegativeLengthChange
from src.models.str_assets_positive_length_change_model import StrAssetsPositiveLengthChange
from src.models.custom_sticker_model import CustomStickerModel
from src.models.bot_settings_model import BotSettingsModel
from src.models.sticker_set_model import StickerSetModel
from src.models.winners_log import WinnersLog
from src.models.user_model import UserModel
from src.models.role_model import RoleModel
from src.models.user_stats import UserStats
from src.models.db_model import db
from typing import List, Dict, Any
from src.data.config import Prefs
from aiogram.types import Chat
from datetime import  datetime
from sqlalchemy import select
from typing import Optional
from sqlalchemy import and_
from math import ceil

prefs = Prefs()

class DataBase():
    def __init__(self):
        pass
    ###--------------------------------------
    ### Методы работы с данными пользователей 
    ###--------------------------------------
    async def get_user(self, tg_id: int) -> Optional[UserModel]:
        try:
            return await UserModel.query.where(UserModel.tg_id == tg_id).gino.first()
        except:
            return None
        
    async def get_last_day_draw_winner_in_chat(self, chat_id: int) -> Optional[UserModel]:
        try:
            return await UserModel.query.where(and_(UserModel.chat_id == chat_id, 
                                               UserModel.last_daily_draw_winner == True)).gino.first()
        except:
            return None
        
    async def get_user_by_id(self, id: int) -> Optional[UserModel]:
        try:
            return await UserModel.query.where(UserModel.id == id).gino.first()
        except:
            return None
        
    async def get_user_by_chat_id(self, tg_id: int, chat_id: int) -> Optional[UserModel]:
        try:
            return await UserModel.query.where(and_(UserModel.chat_id == chat_id,
                                                    UserModel.tg_id == tg_id)).gino.first()
        except:
            return None
        
    async def get_all_users(self) ->  List[UserModel]: 
        return await UserModel.query.gino.all()
    
    async def get_all_users_by_chat(self, chat_id: int) ->  List[UserModel]: 
        return await UserModel.query.where(and_(UserModel.chat_id == chat_id)).gino.all()
    
    async def get_daily_draw_participants(self) ->  List[UserModel]: 
        return await UserModel.query.where(UserModel.last_daily_draw_winner == False).gino.all()
    
    async def add_user(self, tg_id: int, tg_name: str, length: int, custom_title: str, chat_id:int):
        try:
            user = UserModel(tg_id = tg_id, 
                             tg_name = tg_name, 
                             length = length, 
                             role_id = await self.get_role_id_by_name("member"),
                             custom_title = custom_title, 
                             chat_id = chat_id)
            await user.create()
            return True
        except Exception as error: 
            print(f"user create error: {error}")
            return False
        
    async def get_place_in_top_by_member(self, tg_id:int, chat_id:int) -> int:
        users:List[UserModel] = await UserModel.query.where(UserModel.chat_id == chat_id).\
                                        order_by(UserModel.length.desc()).gino.all()
        for i in range(len(users)):
            if (users[i].tg_id == tg_id):
                return i + 1
            
        return -1
    
    async def update_user_by_id(self, tg_id: int, args:Dict[str, Any] = {}) -> bool:
        try:
            await UserModel.update.values(**args).where(UserModel.tg_id == tg_id).gino.status()
            return True
        except Exception as error:
            print(f"update user error: {error}")
            return False
        
    async def update_user(self, user: UserModel, args:Dict[str, Any] = {}) -> bool:
        try:
            await user.update(**args).apply()
            return True
        except Exception as error:
            print(f"update user error: {error}")
            return False
        
    async def update_users_money_by_chat(self, chat_id: int, money:int) -> bool:
        try:
            await UserModel.update.where(UserModel.chat_id == chat_id).values(
                money=UserModel.money + money).gino.status()
            return True
        except Exception as error:
            print(f"update user error: {error}")
            return False
        
    async def get_role_id_by_name(self, name: str) -> int:
        try:
            role = await RoleModel.query.where(RoleModel.name == name).gino.first()
            return role.id
        except:
            return None
    
    async def is_admin(self, tg_id: int) -> bool: 
        try:
            super_users : List = prefs.super_users
            user = await self.get_user(tg_id)
            return user.role_id == 1 or f'{tg_id}' in super_users
        except Exception as error:
            print(f"check role error: {error}")
            return False
    
    async def get_admins_list(self) ->  List[UserModel]:
        try:
            return await UserModel.query.where(UserModel.role_id == 1).gino.all()
        except:
            return []
        
    ###-----------------------------------------
    ### Методы работы с данными наборов стикеров 
    ###-----------------------------------------

    async def add_sticker_set(self, short_name:str, title:str):
        try:
            sticker_set = StickerSetModel(short_name = short_name, title = title)
            await sticker_set.create()
            return True
        except Exception as error: 
            print(f"sticker set create error: {error}")
            return False
        
    async def add_custom_sticker(self, media_path: str, sticker_id:str, sticker_set_name:str):
        try:
            custom_sticker = CustomStickerModel(media_path = media_path, 
                                                sticker_id = sticker_id, 
                                                sticker_set_name = sticker_set_name)
            await custom_sticker.create()
            return True
        except Exception as error: 
            print(f"custom sticker create error: {error}")
            return False
        
    async def get_custom_sticker_by_id(self, sticker_id:str,) -> Optional[CustomStickerModel]:
        try:
            custom_sticker : CustomStickerModel = await CustomStickerModel.\
            query.where(CustomStickerModel.sticker_id == sticker_id).gino.first()

            return custom_sticker
        except Exception as error:
            print(f"custom sticker media get error: {error}")
            return None
        
    async def delete_custom_sticker_by_id(self, sticker_id:str) -> bool:
        try:
            return await CustomStickerModel.delete.\
                where(CustomStickerModel.sticker_id == sticker_id).gino.status()
        except Exception as error:
            print(f"custom sticker media delete error: {error}")
            return False
        
    async def get_custom_stickers_by_set_name(self,
                                              sticker_set_name:str) -> Optional[List[CustomStickerModel]]:
        try:
            custom_stickers : List[CustomStickerModel] = await CustomStickerModel.\
            query.where(CustomStickerModel.sticker_set_name == sticker_set_name).gino.all()

            return custom_stickers
        except Exception as error:
            print(f"custom stickers media get error: {error}")
            return None

    async def get_all_sticker_sets(self) ->  List[StickerSetModel]: 
        return await StickerSetModel.query.gino.all()
    
    async def get_sticker_set_by_id(self, set_id:str,) -> Optional[StickerSetModel]:
        try:
            custom_sticker : StickerSetModel = await StickerSetModel.\
            query.where(StickerSetModel.id == set_id).gino.first()

            return custom_sticker
        except Exception as error:
            print(f"sticker set get error: {error}")
            return None
    
    async def delete_sticker_set_by_name(self, short_name:str):
        return await StickerSetModel.delete.\
            where(StickerSetModel.short_name == short_name).gino.status()
    
    ###-----------------------------------------
    ### Методы работы с данными настроек 
    ###-----------------------------------------

    async def get_settings(self, chat: Chat) -> Optional[BotSettingsModel]:
        try:
            settings:Optional[BotSettingsModel] = await BotSettingsModel.query.where(BotSettingsModel.chat_id == chat.id).gino.first()
            if (not settings):
                settings = BotSettingsModel(
                    chat_id=chat.id,
                    alias = chat.full_name
                )
                await settings.create()
            return settings
        except Exception as error:
            print(f"settings get error: {error}")
            return None
        
    async def update_settings_by_chat_id(self, chat_id:int, args:Dict[str, Any] = {}) -> bool:
        try:
            query = BotSettingsModel.update.values(**args).where(BotSettingsModel.chat_id == chat_id)
            await query.gino.status()
            return True
        except Exception as error:
            print(f"update settings error: {error}")
            return False
        
    ###-----------------------------------------
    ### Методы работы с статистикой выигрышей 
    ###-----------------------------------------

    async def get_winners_logs_page(self, chat_id:int, page: int = 1):
        """Получить одну страницу логов"""
        items_per_page:int = 10
        offset = (page - 1) * items_per_page

        subquery = select([UserModel.id]).where(UserModel.chat_id == chat_id).alias()
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

        users: List[UserModel] = await UserModel.query.where(UserModel.id.in_(logs_page_users_id)).gino.all()
        
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
    ### Методы работы с статистикой пользователей
    ###-----------------------------------------
    
    async def update_user_stats(self, user_id:int, args:Dict[str, Any] = {}) -> bool:
        try:
            user_stats:Optional[UserStats] = await UserStats.query.where(UserStats.user_id == user_id).gino.first()
            if (not user_stats):
                user_stats = UserStats(user_id = user_id)
                await user_stats.create()
            await user_stats.update(**args).apply()
            return True
        except Exception as error: 
            print(f"user stats update error: {error}")
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