from features.store.data.repository.store_repository import IStoreRepository
from features.user.data.repository.user_repository import IUserRepository
from features.items.data.models.store_item_dto import StoreItem
from features.user.data.dtos.user_dto import User
from core.consts.dictionary import Dictionary
from core.consts.consts import Consts
from typing import List
import os

class StoreManager:
    products:List[StoreItem] = []
    selected_product:StoreItem
    customer:User
    
    def __init__(self, dictionary:Dictionary, 
                 user_repo: IUserRepository,
                 store_repo: IStoreRepository):
        
        self.user_repo = user_repo
        self.store_repo = store_repo
        self.dict = dictionary

    async def openStore(self, user:User) -> dict:
        self.products = await self.store_repo.get_store_items_with_quantity(user)
        self.customer = user

        return {
            "photo_path" : os.path.join(Consts.IMAGES_DIR, f"vendor.webp"),
            "error": None
        }
    
    def select_product(self, product_id:int) -> StoreItem:
        self.selected_product = next((p for p in self.products if p.id == product_id), None)
        return self.selected_product
    
    async def buy_product(self, quantity:int = 1) -> dict:
        msg:str
        final_price:int = self.selected_product.price
        if (self.selected_product.is_discount_active):
            final_price = round(final_price - (final_price * (self.selected_product.discount_percent / 100)))

        final_price = final_price * quantity

        if (self.customer.money < final_price):
            self.closeStore()
            return {"msg":self.dict.not_enough_money(self.customer)}

        if (await self.store_repo.create_purchase_transaction(self.selected_product, self.customer, quantity) and
            await self.user_repo.user_item_transaction(self.customer, self.selected_product, quantity) and
            await self.user_repo.update(self.customer, money=self.customer.money - final_price)):
            msg = self.dict.product_buying_thanks(self.customer)
        else:
            msg = "Мы где-то наебались, мы где-то обсчитались..."
        
        return {
            "msg" : msg
        }

    async def sell_item(self) -> bool:
        pass
    
    def closeStore(self):
        self.products.clear()
        self.selected_product = None
        self.customer = None
