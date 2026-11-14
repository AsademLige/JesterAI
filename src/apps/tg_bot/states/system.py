from aiogram.fsm.state import State, StatesGroup

class EditJob(StatesGroup):
    edit_job = State()

class AdminSettings(StatesGroup):
    main = State()
    chat_list = State()
    chat_edit = State()