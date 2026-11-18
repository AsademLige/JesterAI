from apps.tg_bot.keyboards.callback_fabrics import NewspaperCF
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup
from typing import Optional


class NewspaperKeyboard():
    def issue_navigation(self, number: int, has_prev: bool, has_next: bool) -> Optional[InlineKeyboardMarkup]:
        """Кнопки перехода между выпусками газеты. None, если переходов нет."""
        builder = InlineKeyboardBuilder()

        if has_prev:
            builder.button(text="◀️ Предыдущий выпуск",
                           callback_data=NewspaperCF(action="nav", number=number - 1).pack())
        if has_next:
            builder.button(text="Следующий выпуск ▶️",
                           callback_data=NewspaperCF(action="nav", number=number + 1).pack())

        if not has_prev and not has_next:
            return None

        builder.adjust(1)
        return builder.as_markup()
