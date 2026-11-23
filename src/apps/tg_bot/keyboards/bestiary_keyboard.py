from apps.tg_bot.keyboards.callback_fabrics import BestiaryCF
from aiogram.utils.keyboard import InlineKeyboardBuilder
from features.user.data.dtos.user_dto import User
from aiogram.types import InlineKeyboardMarkup
from core.consts.dictionary import BESTIARY_SECTIONS, Dictionary


dict = Dictionary()


class BestiaryKeyboard():
    def menu(self, user: User) -> InlineKeyboardMarkup:
        """Разделы бестиария."""
        builder = InlineKeyboardBuilder()

        for kind, icon, title in BESTIARY_SECTIONS:
            builder.button(text=f"{icon} {title}",
                           callback_data=BestiaryCF(action="section", kind=kind,
                                                    user_id=user.tg_id).pack())

        builder.button(text=dict.exit,
                       callback_data=BestiaryCF(action="close", user_id=user.tg_id).pack())

        builder.adjust(3, 1)
        return builder.as_markup()

    def section(self, user: User) -> InlineKeyboardMarkup:
        """Навигация внутри раздела."""
        builder = InlineKeyboardBuilder()

        builder.button(text=dict.back,
                       callback_data=BestiaryCF(action="menu", user_id=user.tg_id).pack())
        builder.button(text=dict.exit,
                       callback_data=BestiaryCF(action="close", user_id=user.tg_id).pack())

        builder.adjust(2)
        return builder.as_markup()
