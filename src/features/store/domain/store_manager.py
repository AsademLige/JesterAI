from features.store.data.repository.store_repository import IStoreRepository
from features.user.data.repository.user_repository import IUserRepository
from features.items.data.models.store_item_dto import StoreItem
from features.user.data.models.user_model_orm import UserORM
from features.user.data.dtos.user_dto import User
from core.consts.dictionary import Dictionary
from core.data.data_base import DataBase
from core.consts.consts import Consts
from typing import List, Tuple
import os



class StoreManager:
    products:List[StoreItem] = []
    selected_product:StoreItem
    customer:User
    
    def __init__(self, db:DataBase, 
                 dictionary:Dictionary, 
                 user_repo: IUserRepository,
                 store_repo: IStoreRepository):
        
        self.user_repo = user_repo
        self.store_repo = store_repo
        self.db = db
        self.dict = dictionary

    async def openStore(self, user:User) -> dict:
        if (self.products):
            return {"error" : "⛔️ Встань в очередь!"}
        
        self.products = await self.store_repo.get_store_items_with_quantity()
        self.customer = user

        return {
            "photo_path" : os.path.join(Consts.IMAGES_DIR, f"vendor.webp"),
            "error": None
        }
    
    def select_product(self, product_id:int) -> StoreItem:
        self.selected_product = next((p for p in self.products if p.id == product_id), None)
        return self.selected_product
    
    async def buy_product(self) -> dict:
        msg:str
        final_price:int = self.selected_product.price
        if (self.selected_product.is_discount_active):
            final_price = round(final_price - (final_price * (self.selected_product.discount_percent / 100)))

        if (self.customer.money < final_price):
            self.closeStore()
            return {"msg":self.dict.not_enough_money(self.customer)}

        if (await self.store_repo.update_item_quantity_at_warehouse(self.selected_product) and 
            await self.user_repo.user_item_transaction(self.customer, self.selected_product) and
            await self.user_repo.update(self.customer, {
                UserORM.money.name: self.customer.money - final_price,
            })):
            msg = self.dict.product_buying_thanks(self.customer)
        else:
            msg = "Мы где-то наебались, мы где-то обсчитались..."
        
        return {
            "msg" : msg
        }
    
    def closeStore(self):
        self.products.clear()
        self.selected_product = None
        self.customer = None
