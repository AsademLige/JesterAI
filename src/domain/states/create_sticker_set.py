from aiogram.fsm.state import State, StatesGroup

class CreateStickerSet(StatesGroup):
    set_short_name = State()
    set_title = State()
    set_format = State()