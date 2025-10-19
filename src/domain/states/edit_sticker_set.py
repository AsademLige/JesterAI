from aiogram.fsm.state import State, StatesGroup

class EditStickerSet(StatesGroup):
    get_sticker_set_list = State()
    edit_sticker_set = State()
    delete_sticker_set = State()
    #Добавление стикера в набор
    add_sticker_set_emoji = State()
    add_sticker_set_sticker = State()
    add_sticker_set_text_to_sticker_clip = State()
    add_sticker_set_sticker_media = State()
    add_sticker_complete = State()
    #Удаление стикера из набора
    delete_sticker_from_set = State()