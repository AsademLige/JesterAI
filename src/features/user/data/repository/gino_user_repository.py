
from features.battles.loot_manager import DropTags
from features.user.data.models.user_inventory_link_orm import UserInventoryLinkORM
from features.user.data.repository.user_repository import IUserRepository
from features.user.data.models.user_stats_orm import UserStatsORM
from features.user.data.dtos.user_dto import InventoryItem, User
from features.items.data.models.base_item_dto import BaseItem
from features.user.data.models.user_model_orm import UserORM
from features.user.data.models.role_orm import UserRoleORM
from features.items.data.models.item_orm import ItemORM
from core.services.data_base.db_model import db
from typing import Any, Dict, List, Optional
from core.utils.app_herald import AppHerald
from core.data.data_base import DataBase
from core.consts.config import Prefs
from sqlalchemy import func, select
from cachetools import TTLCache
from sqlalchemy import and_
import logging


class GinoUserRepository(IUserRepository):
    _instance = None
    db = DataBase()
    prefs = Prefs()
    _cache:TTLCache
    _tg_id_map:TTLCache
    _chat_tg_map:TTLCache
    
    logger:AppHerald = AppHerald()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._cache = TTLCache(maxsize=100, ttl=86400)
            cls._instance._tg_id_map = TTLCache(maxsize=100, ttl=86400)
            cls._instance._chat_tg_map = TTLCache(maxsize=100, ttl=86400)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True

    def _add_to_cache(self, user: User) -> None:
        """метод заполнения кэш-карт User"""
        self._cache[user.id] = user
        self._tg_id_map[user.tg_id] = user.id
        self._chat_tg_map[(user.chat_id, user.tg_id)] = user.id

        self.logger.send_log("user_repo", logging.INFO, f"cache update id_{user.id}:tg_id_{user.tg_id}:chat_id_{user.chat_id}")

    def _get_cache_user(self, tg_id: Optional[int] = None, 
                       id: Optional[int] = None, 
                       chat_id: Optional[int] = None) -> Optional[User]:
        
        if id in self._cache:
            return self._cache[id]
        
        if tg_id in self._tg_id_map:
            user_id = self._tg_id_map[tg_id]
            if user_id in self._cache:
                return self._cache[user_id]
            
        cache_key = (chat_id, tg_id)
        if cache_key in self._chat_tg_map:
            user_id = self._chat_tg_map[cache_key]
            if user_id in self._cache:
                return self._cache[user_id]
            
        return None
    
    def clear_cache(self):
        self._cache.clear()
        self._chat_tg_map.clear()
        self._tg_id_map.clear()

    async def get_user(self, tg_id: Optional[int] = None, 
                       chat_id: Optional[int] = None,
                       id: Optional[int] = None,
                       last_daily_draw_winner: Optional[bool] = None) -> Optional[User]:
        
        if (not tg_id and not id): return None
        
        cache_user = self._get_cache_user(tg_id, id, chat_id)

        if (cache_user): return cache_user

        try:
            query = (
                select([UserORM, UserStatsORM])
                .select_from(UserORM.join(UserStatsORM))
            )

            if tg_id is not None:
                query = query.where(UserORM.tg_id == tg_id)

            if id is not None:
                query = query.where(UserORM.id == id)

            if chat_id is not None:
                query = query.where(UserORM.chat_id == chat_id)

            if last_daily_draw_winner is not None:
                query = query.where(UserORM.last_daily_draw_winner == last_daily_draw_winner)            
            
            row = await query.gino.load((UserORM, UserStatsORM)).first()
            if not row:
                return None

            db_user: UserORM
            db_stats: UserStatsORM
            (db_user, db_stats) = row

            user_dto = User.model_validate(db_user)

            user_dto.trash_loto_money_wins = db_stats.trash_loto_money_wins
            user_dto.trash_loto_length_wins = db_stats.trash_loto_length_wins
            user_dto.trash_loto_jackpots = db_stats.trash_loto_jackpots
            user_dto.trash_loto_spins = db_stats.trash_loto_spins

            user_dto.dice_games = db_stats.dice_games
            user_dto.dice_minor_wins = db_stats.dice_minor_wins
            user_dto.dice_major_wins = db_stats.dice_major_wins

            user_dto.gladiators_bet = db_stats.gladiators_bet
            user_dto.gladiators_bet_win = db_stats.gladiators_bet_win

            user_dto.duels_count = db_stats.duels_count
            user_dto.duels_win_count = db_stats.duels_win_count
            user_dto.good_hunting_count = db_stats.good_hunting_count

            await self.load_user_inventory(user_dto)

            self._add_to_cache(user_dto)

            return user_dto
        except Exception as error:
            self.logger.send_log("user_repo", logging.ERROR, f"get user  error: {error}")
            return None
        
    async def get_users(self, chat_id: Optional[int] = None,
                        last_daily_draw_winner: Optional[bool] = None) -> List[User]: 
        
        try:
            query = select([UserORM.id, UserORM.tg_id]).select_from(UserORM)
        
            if chat_id is not None:
                query = query.where(UserORM.chat_id == chat_id)
                
            if last_daily_draw_winner is not None:
                query = query.where(UserORM.last_daily_draw_winner == last_daily_draw_winner)
                
            rows = await query.gino.all()
            if not rows:
                self.logger.send_log("user_repo", logging.ERROR, f"get users error, no users in chat {chat_id}: {error}")
                return []

            result: List[User] = []
            ids_to_fetch_from_db: List[int] = []

            for row in rows:
                user_id = row[0]
                tg_id = row[1]

                cache_user = self._get_cache_user(id=user_id, tg_id=tg_id)
                
                if cache_user:
                    result.append(cache_user)
                else:
                    ids_to_fetch_from_db.append(user_id)

            if ids_to_fetch_from_db:
                db_query = (
                    select([UserORM, UserStatsORM])
                    .select_from(UserORM.outerjoin(UserStatsORM))
                    .where(UserORM.id.in_(ids_to_fetch_from_db))
                )
                db_rows = await db_query.gino.load((UserORM, UserStatsORM)).all()
                
                for db_row in db_rows:
                    db_user: UserORM
                    db_stats: UserStatsORM
                    db_user, db_stats = db_row
                    
                    user_dto = User.model_validate(db_user)
                    if db_stats:
                        user_dto.trash_loto_money_wins = db_stats.trash_loto_money_wins
                        user_dto.trash_loto_length_wins = db_stats.trash_loto_length_wins
                        user_dto.trash_loto_jackpots = db_stats.trash_loto_jackpots
                        user_dto.trash_loto_spins = db_stats.trash_loto_spins

                        user_dto.dice_games = db_stats.dice_games
                        user_dto.dice_minor_wins = db_stats.dice_minor_wins
                        user_dto.dice_major_wins = db_stats.dice_major_wins

                        user_dto.gladiators_bet = db_stats.gladiators_bet
                        user_dto.gladiators_bet_win = db_stats.gladiators_bet_win

                        user_dto.duels_count = db_stats.duels_count
                        user_dto.duels_win_count = db_stats.duels_win_count
                        user_dto.good_hunting_count = db_stats.good_hunting_count

                    await self.load_user_inventory(user_dto)
                    
                    self._add_to_cache(user_dto)
                    result.append(user_dto)

            return result
        except Exception as error:
            self.logger.send_log("user_repo", logging.ERROR, f"get users  error: {error}")
            return []
        
    async def add(self, tg_id: int, tg_name: str, length: int, custom_title: str, chat_id:int):
        try:
            user = UserORM(tg_id = tg_id, 
                                tg_name = tg_name, 
                                length = length, 
                                role_id = await self.get_role_id_by_name("member"),
                                custom_title = custom_title, 
                                chat_id = chat_id)
            await user.create()
            return True
        except Exception as error: 
            self.logger.send_log("user_repo", logging.ERROR, f"user create error: {error}")
            return False
        
    
    async def update(self, user: User, args:Dict[str, Any] = {}) -> bool:
        if not args:
            return True
        
        user_args = {}
        stats_args = {}
        
        for key, value in args.items():
            if key in UserStatsORM.__table__.c:
                stats_args[key] = value
            elif key in UserORM.__table__.c:
                user_args[key] = value

        try:
            async with db.transaction():
                if user_args:
                        await UserORM.update.values(**user_args).where(UserORM.id == user.id).gino.status()
                        
                if stats_args:
                    await UserStatsORM.update.values(**stats_args).where(UserStatsORM.user_id == user.id).gino.status()
                
            cached_user = self._cache.get(user.id)
            
            index_needs_update = False
            
            for key, value in args.items():
                if cached_user and hasattr(cached_user, key):
                    setattr(cached_user, key, value)
                if hasattr(user, key):
                    setattr(user, key, value)
                    
                if key in ("chat_id", "tg_id"):
                    index_needs_update = True


            if not cached_user:
                self._add_to_cache(user)
            elif index_needs_update:
                self._add_to_cache(cached_user)

            return True
            
        except Exception as error:
            self.logger.send_log("user_repo", logging.ERROR, f"Update user error: {error}")
            return False
    
    ###TODO: Можно упростить
    async def user_item_transaction(self, user:User, item:BaseItem, quantity:int = 1) -> bool:
        try:
            existed_item:UserInventoryLinkORM = await UserInventoryLinkORM.\
                query.where(and_(UserInventoryLinkORM.product_id == item.id,
                                 UserInventoryLinkORM.user_id == user.id)).gino.first()
            
            new_quantity = quantity
            if (existed_item):
                new_quantity = existed_item.quantity + quantity
                await UserInventoryLinkORM.update.where(and_(UserInventoryLinkORM.product_id == item.id,
                                                          UserInventoryLinkORM.user_id == user.id)).values(
                quantity=new_quantity).gino.status()
            else:
                new_item = UserInventoryLinkORM(
                    user_id = user.id,
                    product_id = item.id,
                    quantity = quantity
                )
                await new_item.create()

            inventory_item = next((i for i in user.inventory if i.id == item.id), None)

            if inventory_item:
                if new_quantity <= 0:
                    inventory_item.quantity = 0
                else:
                    inventory_item.quantity = new_quantity
            elif new_quantity > 0:
                new_dto = InventoryItem(
                    id=item.id,
                    user_id=user.id,
                    quantity=new_quantity,
                    price=item.price,
                    title=item.title,
                    tag=item.tag,
                    description=item.description,
                    action=item.action,
                    utf8_icon=item.utf8_icon
                )
                user.inventory.append(new_dto)

            return True
        except Exception as error:
            self.logger.send_log("user_repo", logging.ERROR, f"item transaction error: {error}")
            return False
        
    async def update_users_money_by_chat(self, chat_id: int, money:int) -> bool:
        try:
            await UserORM.update.where(UserORM.chat_id == chat_id).values(
                money=UserORM.money + money).gino.status()
            
            self.clear_cache()

            return True
        except Exception as error:
            self.logger.send_log("user_repo", logging.ERROR, f"update user error: {error}")
            return False
    
    async def load_user_inventory(self, user:User) -> None:
        try:
            query = (
                select([UserInventoryLinkORM, ItemORM])
                .select_from(ItemORM.join(UserInventoryLinkORM))
                .where(
                    and_(
                        UserInventoryLinkORM.user_id == user.id,
                        UserInventoryLinkORM.quantity > 0
                    )
                )
            )

            rows = await query.gino.load((UserInventoryLinkORM, ItemORM)).all()

            for row in rows:
                db_item: ItemORM
                db_user_inventory_link: UserInventoryLinkORM

                db_user_inventory_link, db_item = row

                inventory_item_dto = InventoryItem.from_orm(user.id, db_item, db_user_inventory_link) 

                if db_item:
                    inventory_item_dto.price = db_item.price
                    inventory_item_dto.title = db_item.title
                    inventory_item_dto.tag = db_item.tag
                    inventory_item_dto.description = db_item.description
                    inventory_item_dto.action = db_item.action
                    inventory_item_dto.utf8_icon = db_item.utf8_icon

                user.inventory.append(inventory_item_dto)
        except Exception as error:
            self.logger.send_log("user_repo", logging.ERROR, f"get user inventory error: {error}")
            return None
        
    async def get_user_heal_items(self, user:UserORM) -> List[InventoryItem]:
        try:
            query = (
                select([UserInventoryLinkORM, ItemORM])
                .select_from(ItemORM.join(UserInventoryLinkORM))
                .where(
                    and_(
                        ItemORM.action.ilike(f"%heal%"), 
                        UserInventoryLinkORM.user_id == user.id,
                        UserInventoryLinkORM.quantity > 0
                    )
                )
            )

            rows = await query.gino.load((UserInventoryLinkORM, ItemORM)).all()
            items:List[InventoryItem] = []

            for row in rows:
                db_item: ItemORM
                db_user_inventory_link: UserInventoryLinkORM

                db_user_inventory_link, db_item = row

                inventory_item_dto = InventoryItem.from_orm(user.id, db_item, db_user_inventory_link) 

                if db_item:
                    inventory_item_dto.price = db_item.price
                    inventory_item_dto.title = db_item.title
                    inventory_item_dto.tag = db_item.tag
                    inventory_item_dto.description = db_item.description
                    inventory_item_dto.action = db_item.action
                    inventory_item_dto.utf8_icon = db_item.utf8_icon

                items.append(inventory_item_dto)

            return items
        except Exception as error:
            print(f"get user heal items error: {error}")
            return []
        
    async def get_item_by_id(self, item_id:int) -> Optional[BaseItem]:
        try:
            item_db = await ItemORM.query.where(ItemORM.id == item_id).gino.first()
            return BaseItem.model_validate(item_db)
        except Exception as error:
            print(f"add to inventory error: {error}")
            return None
        
    async def get_random_item_by_tag(self, tag:DropTags) -> Optional[BaseItem]:
        try:
            item_db = await ItemORM.query.order_by(func.random()).\
                    where(ItemORM.tag.ilike(f"%{tag.name}%")).gino.first()
            
            return BaseItem.model_validate(item_db)
        except Exception as error:
            print(f"get item by tag error: {error}")
            return None
        
    async def get_place_in_top_by_member(self, tg_id:int, chat_id:int) -> int:
        subquery = (
            select([
                UserORM.tg_id,
                func.row_number().over(order_by=UserORM.length.desc()).label("rank")
            ])
            .where(UserORM.chat_id == chat_id)
            .alias("top_list")
        )
        
        main_query = select([subquery.c.rank]).where(subquery.c.tg_id == tg_id)
        result = await main_query.gino.scalar()
        
        return result if result is not None else -1
    
    async def is_admin(self, tg_id: int) -> bool: 
        try:
            super_users : List = self.prefs.super_users
            user:User = await self.get_user(tg_id)
            return user.role_id == 1 or f'{tg_id}' in super_users
        except Exception as error:
            self.logger.send_log("user_repo", logging.ERROR, f"check role error: {error}")
            return False
        
    async def get_role_id_by_name(self, name: str) -> int:
        try:
            role = await UserRoleORM.query.where(UserRoleORM.name == name).gino.first()
            return role.id
        except:
            return None
    
    async def change_reputation(self, source_id: str, target_id: str, delta: int) -> None:
        """Изменить репутацию (например, уменьшить при пакости)"""
        return