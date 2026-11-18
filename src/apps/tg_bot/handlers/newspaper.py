from features.newspaper.data.repository.gino_newspaper_repository import GinoNewspaperRepository
from apps.tg_bot.keyboards.newspaper_keyboard import NewspaperKeyboard
from apps.tg_bot.keyboards.callback_fabrics import NewspaperCF
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.exceptions import TelegramAPIError
from core.consts.consts import Consts
from aiogram.enums import ParseMode
from aiogram import Router
import os

rt = Router()
newspaper_repo = GinoNewspaperRepository()
newspaper_kb = NewspaperKeyboard()


@rt.callback_query(NewspaperCF.filter())
async def newspaper_navigation(callback: CallbackQuery, callback_data: NewspaperCF):
    number = callback_data.number
    text = await newspaper_repo.get_issue(number)
    if text is None:
        await callback.answer("Выпуск не найден", show_alert=True)
        return

    has_prev = (await newspaper_repo.get_issue(number - 1)) is not None
    has_next = (await newspaper_repo.get_issue(number + 1)) is not None
    markup = newspaper_kb.issue_navigation(number, has_prev, has_next)

    try:
        await callback.message.edit_caption(caption=text, reply_markup=markup, parse_mode=ParseMode.HTML)
    except TelegramAPIError:
        # Telegram не даёт редактировать сообщения старше 48 часов — шлём свежую копию выпуска
        photo = FSInputFile(os.path.join(Consts.IMAGES_DIR, "newspaper.webp"))
        await callback.message.answer_photo(photo=photo, caption=text,
                                            reply_markup=markup, parse_mode=ParseMode.HTML)
    await callback.answer()
