from core.data.models.str_assets_negative_length_change_model import StrAssetsNegativeLengthChange
from core.data.models.str_assets_positive_length_change_model import StrAssetsPositiveLengthChange
from core.data.models.custom_sticker_model import CustomSticker
from core.data.models.sticker_set_model import StickerSet
from core.consts.config import Prefs
from typing import Optional
from typing import List

prefs = Prefs()

class DataBase():
    def __init__(self):
        pass
        
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
    ### Методы загрузки наборов данных 
    ###-----------------------------------------

    async def get_negative_length_change_assets(self) -> List[str]: 
        models:List[StrAssetsNegativeLengthChange] = await StrAssetsNegativeLengthChange.query.gino.all()
        return [model.data for model in models] 
    
    async def get_positive_length_change_assets(self) -> List[str]: 
        models:List[StrAssetsPositiveLengthChange] = await StrAssetsPositiveLengthChange.query.gino.all()
        return [model.data for model in models] 