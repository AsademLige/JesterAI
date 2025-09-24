from src.models.user_model import UserModel
from src.models.role_model import RoleModel
from sqlalchemy import select
from typing import List

class DataBase():
    def __init__(self):
        pass

    ### Методы получения данных о пользователях     
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
            user = await self.get_user(tg_id)
            return user.role_id == 1
        except:
            return False
    
    async def get_admins_list(self) ->  List[UserModel]:
        try:
            return await UserModel.query.where(UserModel.role_id == 1).gino.all()
        except:
            return []