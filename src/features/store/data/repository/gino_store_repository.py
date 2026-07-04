from features.store.data.models.discounts_model_orm import ProductDiscountORM
from features.store.data.repository.store_repository import IStoreRepository
from features.store.data.models.warehouse_item_orm import WarehouseItemORM
from features.items.data.models.store_item_dto import StoreItem
from features.items.data.models.item_orm import ItemORM
from core.utils.app_herald import AppHerald
from core.data.data_base import DataBase
from core.consts.config import Prefs
from typing import List, Optional
from sqlalchemy import and_
import logging
import random

class GinoStoreRepository(IStoreRepository):
    _instance = None
    db = DataBase()
    prefs = Prefs()

    logger:AppHerald = AppHerald()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def get_store_items_with_quantity(self) -> Optional[List[StoreItem]]:
        try:
            store_items:List[StoreItem] = []
            query = ItemORM.join(WarehouseItemORM).outerjoin(
                ProductDiscountORM, 
                and_(
                    ItemORM.id == ProductDiscountORM.product_id,
                    ProductDiscountORM.is_active == True
                )
            ).select()

            rows = await query.gino.load((WarehouseItemORM, ItemORM, ProductDiscountORM)).all()

            for row in rows:
                db_item: ItemORM
                db_warehouse_item: WarehouseItemORM
                db_product_discount_item: ProductDiscountORM

                db_warehouse_item, db_item, db_product_discount_item = row

                store_item_dto = StoreItem.from_orm_objects(db_item, 
                                                                db_warehouse_item, 
                                                                db_product_discount_item) 
                store_items.append(store_item_dto)

            return store_items
    
        except Exception as error:
            self.logger.send_log("store_repo", logging.ERROR, f"get store items error: {error}")
            return None
        
    async def update_item_quantity_at_warehouse(self, item:StoreItem, quantity:int = 1) -> bool:
        try:
            if (item.warehouse_quantity - quantity >= 0):
                await WarehouseItemORM.update.where(WarehouseItemORM.product_id == item.product_id).values(
                    quantity=WarehouseItemORM.quantity - quantity).gino.status()
                item.warehouse_quantity -= quantity
                return True
            else:
                return False
        except Exception as error:
            self.logger.send_log("store_repo", logging.ERROR, f"update item {item.title} error: {error}")
            return None
        
    async def update_warehouse(self) -> bool:
        try:
            await WarehouseItemORM.update.where(WarehouseItemORM.quantity < WarehouseItemORM.max_capacity).values(
                    quantity=WarehouseItemORM.max_capacity).gino.status()
            return True
        except Exception as error:
            self.logger.send_log("store_repo", logging.ERROR, f"warehouse update error: {error}")
            return False
        
    async def deactivate_discounts(self) -> bool:
        try:
            await ProductDiscountORM.update.where(ProductDiscountORM.is_active == True).\
                    values(is_active=False).gino.status()
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
            #TODO:Шел час ночи и я так и не смог 
            #корректно достать рандомное количество из базы без дублей
            random.shuffle(discount_items)
            discount_items = discount_items[:discounts_count]

            discounts:List[StoreItem] = []

            for discount_item in discount_items:
                existed_discount:ProductDiscountORM = await ProductDiscountORM.\
                query.where(ProductDiscountORM.product_id == discount_item.id).gino.first()
            
                if (existed_discount):
                    await ProductDiscountORM.update.where(ProductDiscountORM.product_id == discount_item.id).\
                        values(is_active=True, discount_percent = random.choice([25, 35, 45, 50])).gino.status()
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

            return discounts
        except Exception as error:
            print(f"discount create error: {error}")
            return None