from apps.tg_bot.keyboards.callback_fabrics import DiceGameCF, GambaChoiceCF, GladiatorsCF, TrashLotoCF
from aiogram.utils.keyboard import InlineKeyboardBuilder
from features.user.data.dtos.user_dto import User
from aiogram.types import InlineKeyboardMarkup
from aiogram.types import InlineKeyboardButton
from core.consts.dictionary import Dictionary
from core.consts.config import Prefs

prefs = Prefs()
dict = Dictionary()

class GambaHouseKeyboard():
    def __init__(self):
        pass

    def gamba_choice(self, user:User) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.add(InlineKeyboardButton(text="🎰 Треш-лото",
                callback_data=TrashLotoCF(action="trash_loto_menu",
                                         user_id=user.tg_id).pack()))
        
        builder.add(InlineKeyboardButton(text="🎲 Кубики",
                callback_data=DiceGameCF(action="dice_game",
                                         user_id=user.tg_id).pack()))
        
        # builder.add(InlineKeyboardButton(text="🏟️ Арена",
        #         callback_data=GladiatorsCF(action="gladiators",
        #                                  user_id=user.tg_id).pack()))
        
        builder.add(InlineKeyboardButton(text=dict.exit,
                callback_data=GambaChoiceCF(action="exit",
                                         user_id=user.tg_id).pack()))

        builder.adjust(2, 2) 
        return builder.as_markup()
    
    def dice_choice(self, user:User) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.add(InlineKeyboardButton(text=dict.dice_smaller,
                callback_data=DiceGameCF(action="smaller",
                                         user_id=user.tg_id).pack()))

        builder.add(InlineKeyboardButton(text=dict.dice_equal,
            callback_data=DiceGameCF(action="equal",
                                     user_id=user.tg_id).pack()))

        builder.add(InlineKeyboardButton(text=dict.dice_bigger,
            callback_data=DiceGameCF(action="bigger",
                                     user_id=user.tg_id).pack()))
    
        builder.add(InlineKeyboardButton(text=dict.rules,
            callback_data=DiceGameCF(action="rules",
                                     user_id=user.tg_id).pack()))

        builder.add(InlineKeyboardButton(text=dict.exit,
            callback_data=DiceGameCF(action="exit",
                                     user_id=user.tg_id).pack()))
        
        builder.adjust(3, 2) 
        return builder.as_markup()

    def trash_loto_menu(self, user:User) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.add(InlineKeyboardButton(text=f"5💰",
                                        callback_data=TrashLotoCF(action="trash_loto",
                                                                    user_id=user.tg_id).pack()))

        builder.add(InlineKeyboardButton(text=f"10💰",
                                callback_data=TrashLotoCF(action="trash_loto",
                                                        bet=10,
                                                        user_id=user.tg_id).pack()))
        
        builder.add(InlineKeyboardButton(text=f"20💰",
                                callback_data=TrashLotoCF(action="trash_loto",
                                                        bet=20,
                                                        user_id=user.tg_id).pack()))

        builder.add(InlineKeyboardButton(text=dict.exit,
                    callback_data=GambaChoiceCF(action="exit",
                                             user_id=user.tg_id).pack()))

        builder.adjust(3, 2) 
        return builder.as_markup()

    def trash_loto_again(self, user:User, bet:int) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        
        builder.add(InlineKeyboardButton(text=f"Еще! (-{bet}💰)",
                        callback_data=TrashLotoCF(action="trash_loto",
                                                  bet=bet,
                                                  user_id=user.tg_id).pack()))
        
        builder.adjust(3, 2) 
        return builder.as_markup()