from src.models.custom_sticker_model import CustomStickerModel
from src.models.sticker_set_model import StickerSetModel
from src.models.user_model import UserModel
from src.models.role_model import RoleModel
from src.data.config import Prefs
from sqlalchemy import select
from typing import Optional
from typing import List
import datetime

prefs = Prefs()

class DataBase():
    def __init__(self):
        pass
    ###--------------------------------------
    ### Методы работы с данными пользователей 
    ###--------------------------------------
    async def get_user(self, tg_id: int) -> UserModel :
        try:
            return await UserModel.query.where(UserModel.tg_id == tg_id).gino.first()
        except:
            return None
        
    async def get_user_by_id(self, id: int) -> UserModel :
        try:
            return await UserModel.query.where(UserModel.id == id).gino.first()
        except:
            return None
        
    async def get_all_users(self) ->  List[UserModel]: 
        return await UserModel.query.gino.all()
    
    async def add_user(self, tg_id: int, tg_name: str, length: int, custom_title: str,):
        try:
            user = UserModel(tg_id = tg_id, tg_name = tg_name, length = length, custom_title = custom_title)
            await user.create()
            return True
        except Exception as error: 
            print(f"user create error: {error}")
            return False
        
    async def update_user_role(self, tg_id: int, role_id: int) -> bool:
        try:
            user = await self.get_user(tg_id)
            await user.update(role_id = role_id).apply()
            return True
        except Exception as error:
            print(f"update role error: {error}")
            return False
        
    async def update_user_member(self, tg_id: int, length: int) -> bool:
        user = await self.get_user(tg_id)
        return self.__update_user_member(user, length);    
    
    async def update_user_member(self, user: UserModel, length: int) -> bool:
        return await self.__update_user_member(user, length);    
        
    async def __update_user_member(self, user: UserModel, length: int) -> bool:
        try:
            await user.update(length = length, last_length_check = datetime.datetime.now()).apply()
            return True
        except Exception as error:
            print(f"update member error: {error}")
            return False
        
    async def get_role_id_by_name(self, name: str) -> int:
        try:
            role = await RoleModel.query.where(RoleModel.name == name).gino.first()
            return role.id
        except:
            return None
    
    async def is_user_unknown(self, tg_id: int) -> bool: 
        try:
            return await self.get_user(tg_id) == None
        except:
            return False
    
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
    
    async def delete_sticker_set_by_name(self, short_name:str):
        return await StickerSetModel.delete.\
            where(StickerSetModel.short_name == short_name).gino.status()