from aiogram.enums import ParseMode

from apps.tg_bot.keyboards.hub_keyboard import get_hub_keyboard, fishing_button
from aiogram.filters import Command, StateFilter
from aiogram.types import CallbackQuery, Message
from ssl import SSLContext
from aiogram import F, Bot, Router

from core.consts.config import Prefs
from core.consts.dictionary import Dictionary
from core.utils.utils import Utils
from features.battles.game_controller import GameController
from features.game_engine.domain.game_engine import GameEngine
from features.user.data.dtos.user_dto import User
from features.user.data.repository.gino_user_repository import GinoUserRepository

rt = Router()
dict = Dictionary()
prefs = Prefs()
bot = Bot(token=prefs.bot_token)
user_repo:GinoUserRepository = GinoUserRepository()

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

    message = callback_query.message
        
    user: User = await user_repo.get_user(callback_query.from_user.id, message.chat.id)

    await message.delete()
    if (user.energy > 0):
        await user_repo.update(user, energy=user.energy - 1)
        game_engine.create_energy_restore_timer(user)
    else:
        answer = await bot.send_message(user.chat_id, 
                                        dict.energy_drain(user), 
                                parse_mode=ParseMode.HTML)
        await Utils.delete_old_message([answer], 10)
        return

    link_message = await bot.send_message(callback_query.message.chat.id, f"🎣 <a href='tg://user?id={user.tg_id}'> Вперед, на рыбалку!</a>", 
                                            reply_markup=fishing_button(""),
                                            parse_mode=ParseMode.HTML)
