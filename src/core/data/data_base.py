from core.data.models.str_assets_negative_length_change_model import StrAssetsNegativeLengthChange
from core.data.models.str_assets_positive_length_change_model import StrAssetsPositiveLengthChange
from features.user.data.models.user_inventory_link_orm import UserInventoryLinkORM
from features.battles.data.models.monster_stats_orm import MonsterStatsORM
from features.store.data.models.discounts_model_orm import ProductDiscountORM
from core.data.models.custom_sticker_model import CustomSticker
from features.battles.data.models.monster_orm import MonsterORM
from features.user.data.models.user_model_orm import UserORM
from core.data.models.bot_settings_orm import BotSettingsORM
from features.store.data.models.warehouse_item_orm import WarehouseItemORM
from core.data.models.sticker_set_model import StickerSet
from core.data.models.winners_log_model import WinnersLog
from features.items.data.models.item_orm import ItemORM
from features.battles.loot_manager import DropTags
from core.services.data_base.db_model import db
from typing import List, Dict, Any, Tuple
from sqlalchemy import func, select
from core.consts.config import Prefs
from datetime import  datetime
from typing import Optional
from sqlalchemy import and_
from math import ceil
import random

prefs = Prefs()

class DataBase():
    def __init__(self):
        pass
    ###--------------------------------------
    ### Методы работы с данными пользователей 
    ###--------------------------------------
        
    async def get_user_heal_items(self, user:UserORM) -> List[Tuple[UserInventoryLinkORM, ItemORM]]:
        try:
            query = ItemORM.join(UserInventoryLinkORM).select().where(and_(ItemORM.action.ilike(f"%heal%"), 
                                                                     UserInventoryLinkORM.quantity > 0,
                                                                     UserInventoryLinkORM.user_id == user.id))
            return await query.gino.load((UserInventoryLinkORM, ItemORM)).all()
        except Exception as error:
            print(f"get user heal items error: {error}")
            return []
        
    async def get_item_by_id(self, item_id:int) -> Optional[ItemORM]:
        try:
            return await ItemORM.query.where(ItemORM.id == item_id).gino.first()
        except Exception as error:
            print(f"add to inventory error: {error}")
            return None
        
    async def get_random_item_by_tag(self, tag:DropTags) -> Optional[ItemORM]:
        try:
            return await ItemORM.query.order_by(func.random()).\
                    where(ItemORM.tag.ilike(f"%{tag.name}%")).gino.first()
        except Exception as error:
            print(f"get item by tag error: {error}")
            return None
        
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
    ### Методы работы с данными настроек 
    ###-----------------------------------------

    async def get_settings(self, chat_id:int, chat_full_name:str) -> Optional[BotSettingsORM]:
        try:
            settings:Optional[BotSettingsORM] = await BotSettingsORM.query.where(BotSettingsORM.chat_id == chat_id).gino.first()
            if (not settings):
                settings = BotSettingsORM(
                    chat_id=chat_id,
                    alias = chat_full_name
                )
                await settings.create()
            return settings
        except Exception as error:
            print(f"settings get error: {error}")
            return None
        
    async def update_settings_by_chat_id(self, chat_id:int, args:Dict[str, Any] = {}) -> bool:
        try:
            query = BotSettingsORM.update.values(**args).where(BotSettingsORM.chat_id == chat_id)
            await query.gino.status()
            return True
        except Exception as error:
            print(f"update settings error: {error}")
            return False
        
    ###-----------------------------------------
    ### Методы работы с магазином
    ###-----------------------------------------
        
    ###-----------------------------------------
    ### Методы работы с монстрами
    ###-----------------------------------------
    
    async def get_random_monsters_by_tag(self, monster_count:int = 1, tag:str = "mob") -> List[MonsterORM]:
        random_monster:List[MonsterORM] = await MonsterORM.query.order_by(func.random()).\
                            where(MonsterORM.tag.ilike(f"%{tag}%")).limit(monster_count).gino.all()
        return random_monster

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
    ### Методы работы с статистикой монстра
    ###-----------------------------------------
    
    async def update_monster_status(self, monster_id:int, args:Dict[str, Any] = {}) -> bool:
        try:
            monster_stats:Optional[MonsterStatsORM] = await MonsterStatsORM.query.\
                            where(MonsterStatsORM.monster_id == monster_id).gino.first()
            if (not monster_stats):
                monster_stats = MonsterStatsORM(monster_id = monster_id)
                await monster_stats.create()
            await monster_stats.update(**args).apply()
            return True
        except Exception as error: 
            print(f"monster stats update error: {error}")
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