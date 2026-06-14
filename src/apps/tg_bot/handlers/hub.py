from apps.tg_bot.keyboards.hub_keyboard import get_hub_keyboard
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from ssl import SSLContext
from aiogram import Router

rt = Router()

@rt.message(StateFilter(None), Command("hub"))
async def show_hub(message: Message, state: SSLContext):
    await message.answer(
        "На перепутье я стою, болт задумчиво чешу...",
        reply_markup=get_hub_keyboard()
    )