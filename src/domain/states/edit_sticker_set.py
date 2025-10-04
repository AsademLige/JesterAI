from aiogram.fsm.state import State, StatesGroup

class EditStickerSet(StatesGroup):
    get_sticker_set_list = State()
    edit_sticker_set = State()
    delete_sticker_set = State()