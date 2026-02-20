from aiogram.fsm.state import State, StatesGroup

class DiceGameSet(StatesGroup):
    dice_menu_choice = State()
    