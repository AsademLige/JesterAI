from features.store.data.models.discounts_model import ProductDiscounts
from features.store.data.models.warehouse import Warehouse
from features.items.data.models.item_model import Item
from core.consts.dictionary import Dictionary
from core.data.models.user_model import User
from core.data.datasource import DataBase
from core.consts.consts import Consts
from typing import List, Tuple
import os

class StoreManager:
    products:List[Tuple[Warehouse, Item, ProductDiscounts]] = []
    selected_product:Tuple[Warehouse, Item, ProductDiscounts]
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
    
    def select_product(self, id:int) -> Tuple[Warehouse, Item, ProductDiscounts]:
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
            await self.db.user_item_transaction(self.customer, self.selected_product[1]) and
            await self.db.update_user(self.customer, {
                User.money.name: User.money - final_price,
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
