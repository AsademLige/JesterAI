from features.store.data.models.discounts_model import ProductDiscounts
from features.user.data.user_repository import UserRepository
from features.user.data.models.user_model_orm import UserORM
from features.store.data.models.warehouse import Warehouse
from features.items.data.models.item_orm import ItemORM
from features.user.data.dtos.user_dto import User
from core.consts.dictionary import Dictionary
from core.data.data_base import DataBase
from core.consts.consts import Consts
from typing import List, Tuple
import os


class StoreManager:
    products:List[Tuple[Warehouse, ItemORM, ProductDiscounts]] = []
    selected_product:Tuple[Warehouse, ItemORM, ProductDiscounts]
    user_repo:UserRepository = UserRepository()
    customer:User
    
    def __init__(self, db:DataBase, dictionary:Dictionary):
        self.db = db
        self.dict = dictionary

    async def openStore(self, user:User) -> dict:
        if (self.products):
            return {"error" : "⛔️ Встань в очередь!"}
        
        self.products = await self.db.get_store_items_with_quantity()
        self.customer = user

        return {
            "photo_path" : os.path.join(Consts.IMAGES_DIR, f"vendor.webp"),
            "error": None
        }
    
    def select_product(self, id:int) -> Tuple[Warehouse, ItemORM, ProductDiscounts]:
        self.selected_product = next((p for p in self.products if p[1].id == id), None)
        return self.selected_product
    
    async def buy_product(self) -> dict:
        msg:str
        final_price:int = self.selected_product[1].price
        if (self.selected_product[2]):
            final_price = round(final_price - (final_price * (self.selected_product[2].discount_percent / 100)))

        if (self.customer.money < final_price):
            self.closeStore()
            return {"msg":self.dict.not_enough_money(self.customer)}

        if (await self.db.update_item_quantity_at_warehouse(self.selected_product) and 
            await self.user_repo.user_item_transaction(self.customer, self.selected_product[1]) and
            await self.user_repo.update_user(self.customer, {
                UserORM.money.name: UserORM.money - final_price,
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
