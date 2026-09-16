from aiogram.enums import ParseMode

from apps.tg_bot.keyboards.hub_keyboard import get_hub_keyboard
from aiogram.filters import Command, StateFilter
from aiogram.types import CallbackQuery, Message
from ssl import SSLContext
from aiogram import F, Bot, Router

from core.consts.config import Prefs
from features.battles.game_controller import GameController
from features.game_engine.domain.game_engine import GameEngine

rt = Router()
prefs = Prefs()
bot = Bot(token=prefs.bot_token)

@rt.message(StateFilter(None), Command("hub"))
async def show_hub(message: Message, state: SSLContext):
    await message.answer(
        "На перепутье я стою, болт задумчиво чешу...",
        reply_markup=get_hub_keyboard()
    )

###Отправиться на Рыбалку
@rt.callback_query(StateFilter(None), F.data == "hub_fishing")
async def fishing_init(callback_query: CallbackQuery, 
                    state: SSLContext, game_controller:GameController, 
                    game_engine:GameEngine):

    link_message = await bot.send_message(callback_query.message.chat.id, f'⚔️ <a href="https://t.me/KristAIBot/fishing">Вперед, на рыбалку!</a>', 
                                        parse_mode=ParseMode.HTML)
