from src.data.dictionary import Dictionary
from aiogram.types import BotCommand
from src.data.config import Prefs
from aiogram import Bot

prefs = Prefs()
dict = Dictionary()
bot = Bot(token=prefs.bot_token)

class Commands():
    ###Начать
    start = "start"

    ###Узнать возможности бота
    help = "help"

    ###Создать новый стикер-пак
    create_sticker_set = "create_sticker_set"

    ###Создать новый стикер-пак
    create_sticker_set = "create_sticker_set"

    ###Изменить стикер в пак
    edit_sticker_set = "edit_sticker_set"

    ###Информация о пользователе
    me = "me"

    ###Интерактивное действие с текущим размером пользователя
    pencil = "pencil"

    async def setup_bot_commands():
        await bot.set_my_commands([
            BotCommand(command="help", description=dict.help),
            BotCommand(command="me", description=dict.me),
            BotCommand(command="pencil", description=dict.pencil)
        ])