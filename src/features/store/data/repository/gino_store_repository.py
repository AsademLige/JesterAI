import copy
import re

from features.store.data.models.discounts_model_orm import ProductDiscountORM
from features.store.data.repository.store_repository import IStoreRepository
from features.store.data.models.warehouse_item_orm import WarehouseItemORM
from features.store.data.models.user_purchased_orm import UserPurchasedORM
from features.items.data.models.store_item_dto import StoreItem
from features.items.data.models.item_orm import ItemORM
from core.utils.app_herald import AppHerald
from sqlalchemy import and_, select
from typing import List, Optional
from cachetools import TTLCache
from datetime import datetime, timedelta
import logging
import random

from features.user.data.dtos.user_dto import User

class GinoStoreRepository(IStoreRepository):
    _instance = None
    _cache: TTLCache

    logger:AppHerald = AppHerald()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._cache = TTLCache(maxsize=1000, ttl=3600)
        return cls._instance
    
    async def get_store_items_with_quantity(self, user:User) -> Optional[List[StoreItem]]:
        try:
            id_query = select([ItemORM.id]).select_from(ItemORM.join(WarehouseItemORM))
            rows = await id_query.gino.all()
            if not rows:
                return []

            store_items: List[StoreItem] = []
            ids_to_fetch_from_db: List[int] = []

            for row in rows:
                item_id = row[0]
                cached_item = self._cache.get(item_id)
                
                if cached_item:
                    store_items.append(cached_item)
                else:
                    ids_to_fetch_from_db.append(item_id)

            if ids_to_fetch_from_db:
                query = ItemORM.join(WarehouseItemORM).outerjoin(
                    ProductDiscountORM, 
                    and_(
                        ItemORM.id == ProductDiscountORM.product_id,
                        ProductDiscountORM.is_active == True
                    )
                ).select().where(ItemORM.id.in_(ids_to_fetch_from_db))

                db_rows = await query.gino.load((WarehouseItemORM, ItemORM, ProductDiscountORM)).all()

                for row in db_rows:
                    db_warehouse_item, db_item, db_product_discount_item = row

                    store_item_dto = StoreItem.from_orm_objects(db_item, 
                                                                db_warehouse_item, 
                                                                db_product_discount_item) 
                    self._cache[db_item.id] = store_item_dto
                    store_items.append(store_item_dto)

            now = datetime.now()
            cutoff_date = now.date() if now.hour >= 9 else (now - timedelta(days=1)).date()

            purchased_rows = await UserPurchasedORM.query.where(
                and_(
                    UserPurchasedORM.date >= cutoff_date,
                    UserPurchasedORM.user_id == user.id
                )
            ).gino.all()

            purchased_map = {}
            for p in purchased_rows:
                purchased_map[p.product_id] = purchased_map.get(p.product_id, 0) + p.quantity

            result_items = []
            for item in store_items:
                deducted = purchased_map.get(item.id, 0)
                if deducted > 0:
                    item_copy = copy.deepcopy(item)
                    item_copy.warehouse_quantity = max(0, item_copy.warehouse_quantity - deducted)
                    result_items.append(item_copy)
                else:
                    result_items.append(item)

            return result_items
    
        except Exception as error:
            self.logger.send_log("store_repo", logging.ERROR, f"get store items error: {error}")
            return None
        
    async def update_item_quantity_at_warehouse(self, item:StoreItem, quantity:int = 1) -> bool:
        try:
            if (item.warehouse_quantity - quantity >= 0):
                await WarehouseItemORM.update.where(WarehouseItemORM.product_id == item.id).values(
                    quantity=WarehouseItemORM.quantity - quantity).gino.status()
                item.warehouse_quantity -= quantity
                
                if item.id in self._cache:
                    del self._cache[item.id]
                    
                return True
            else:
                return False
        except Exception as error:
            self.logger.send_log("store_repo", logging.ERROR, f"update item {item.title} error: {error}")
            return None
        
    async def update_warehouse(self, out_of_stock_count:int = 0) -> List[StoreItem]:
        try:
            query = ItemORM.join(WarehouseItemORM).select().\
                            where(and_(WarehouseItemORM.quantity > 0))
                    
            rows:List[ItemORM] = await query.gino.load(ItemORM).all()

            random.shuffle(rows)
            out_of_stock_orm = rows[:out_of_stock_count]
            ids = [item.id for item in out_of_stock_orm]
            
            await WarehouseItemORM.update.where(
                (WarehouseItemORM.quantity < WarehouseItemORM.max_capacity) &
                (~WarehouseItemORM.product_id.in_(ids))
            ).values(
                quantity=WarehouseItemORM.max_capacity
            ).gino.status()

            await WarehouseItemORM.update.where(
                (WarehouseItemORM.product_id.in_(ids))
            ).values(
                quantity=0
            ).gino.status()

            out_of_stock = []
            for out_of_stock_item in out_of_stock_orm:
                item:StoreItem = StoreItem.from_orm_objects(item=out_of_stock_item)
                out_of_stock.append(item)

            self._cache.clear()

            return out_of_stock
        except Exception as error:
            self.logger.send_log("store_repo", logging.ERROR, f"warehouse update error: {error}")
            return []
        
    async def deactivate_discounts(self) -> bool:
        try:
            await ProductDiscountORM.update.where(ProductDiscountORM.is_active == True).\
                    values(is_active=False).gino.status()
            
            self._cache.clear()
            
            return True
        except Exception as error:
            self.logger.send_log("store_repo", logging.ERROR, f"discount delete error: {error}")
            return False
        
    async def create_random_discount(self, discounts_count:int = 1) -> Optional[List[StoreItem]]:
        try:
            query = ItemORM.join(WarehouseItemORM).\
                outerjoin(ProductDiscountORM,
                        ProductDiscountORM.is_active == False).\
                select().\
                distinct(ItemORM.id).\
                where(and_(WarehouseItemORM.quantity > 0))
        
            discount_items:List[ItemORM] = await query.gino.load(ItemORM).all()
            
            random.shuffle(discount_items)
            discount_items = discount_items[:discounts_count]

            discounts:List[StoreItem] = []

            for discount_item in discount_items:
                existed_discount:ProductDiscountORM = await ProductDiscountORM.\
                query.where(ProductDiscountORM.product_id == discount_item.id).gino.first()
            
                if (existed_discount):
                    await ProductDiscountORM.update.where(ProductDiscountORM.product_id == discount_item.id).\
                        values(is_active=True, discount_percent = random.choice([25, 35, 45, 50])).gino.status()
                    existed_discount = await ProductDiscountORM.\
                                    query.where(ProductDiscountORM.product_id == discount_item.id).gino.first()
                    
                    item:StoreItem = StoreItem.from_orm_objects(item=discount_item, discount=existed_discount)
                    discounts.append(item)
                else:
                    new_discount = ProductDiscountORM(
                        product_id = discount_item.id,
                        discount_percent = random.choice([25, 35, 45, 50])
                    )
                    await new_discount.create()

                    item:StoreItem = StoreItem.from_orm_objects(item=discount_item, discount=new_discount)
                    discounts.append(item)

                if discount_item.id in self._cache:
                    del self._cache[discount_item.id]

            return discounts
        except Exception as error:
            print(f"discount create error: {error}")
            return None

    async def create_purchase_transaction(self, item:StoreItem, user:User, quantity:int = 1) -> bool:
        try:
            del self._cache[item.id]

            purchase_db = UserPurchasedORM(
                product_id = item.id,
                user_id = user.id,
                quantity = quantity,
                date = datetime.now(),
            )
            await purchase_db.create()
            return True
        except Exception as error:
            print(f"create purchase transaction error: {error}")
            return False

    async def check_product_quantity_by_user(self, item:StoreItem, user:User) -> int:
            pass